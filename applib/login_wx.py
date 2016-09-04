# -*- coding: utf-8  -*-
import time
import json
import random
import string
from hashlib import md5
from urllib import quote
#-#from operator import itemgetter
#-#from itertools import chain
#-#from cStringIO import StringIO
if __name__ == '__main__':
    import sys
    import os
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))
from tornado import gen
from tornado.httpclient import AsyncHTTPClient
from tornado.httpclient import HTTPRequest
from tornado.httputil import HTTPHeaders
from tornado.options import options as _options
from WXBizMsgCrypt import WXBizMsgCrypt
from lib.redis_manager import m_redis
from applib.tools_lib import pcformat
from applib.tools_lib import parseXml2Dict
from applib.ios_twin_lib import IOSTwin
from lib.applog import app_log
info, debug, error = app_log.info, app_log.debug, app_log.error


class WXLogin(object):
    # 服务号 kandao0@dianjoy.com
    APPID = 'wxd3195cea4ab462fe'
    APPSECRET = 'a1fd74c5eb834e7b6cbc5c45226cc0c4'
    TOKEN = 'kando_sd'
    ENCODINGAESKEY = 'NQYBdtrenCTn4PQEicktmf4s6AUpOFw2TD67CFGeLsF'

    # 文本消息模板
    TPL_RETURN_TEXT = '''<xml>
                            <ToUserName><![CDATA[{TOUSER}]]></ToUserName>
                            <FromUserName><![CDATA[{FROMUSER}]]></FromUserName>
                            <CreateTime>{TIME}</CreateTime>
                            <MsgType><![CDATA[text]]></MsgType>
                            <Content><![CDATA[{CONTENT}]]></Content>
                            </xml>'''
    # 图片消息模板
    TPL_RETURN_IMAGE = '''<xml>
                            <ToUserName><![CDATA[{TOUSER}]]></ToUserName>
                            <FromUserName><![CDATA[{FROMUSER}]]></FromUserName>
                            <CreateTime>{TIME}</CreateTime>
                            <MsgType><![CDATA[image]]></MsgType>
                            <Image>
                            <MediaId><![CDATA[{MEDIA_ID}]]></MediaId>
                            </Image>
                            </xml>'''

    @staticmethod
    @gen.coroutine
    def getAccessToken():
        u'''获取access token
        '''
        access_token = None
        r = m_redis.get_instance()
        c_k = '_Z_WX_ACCESS_TOKEN'
        access_token = r.get(c_k)
        if access_token:
            info('cache hit %s', c_k)
            raise gen.Return(access_token)

        url = 'https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={APPID}&secret={APPSECRET}'.format(APPID=WXLoginManager.APPID, APPSECRET=WXLoginManager.APPSECRET)
        try:
            httpc_lient = AsyncHTTPClient()
            resp = yield gen.Task(httpc_lient.fetch, url)  # , validate_cert = False)
            info('resp: %s', resp.body)
            j_data = json.loads(resp.body)
        except:
            error('', exc_info=True)
        else:
            if 'errcode' in j_data:
                info('errcode %s, errmsg: %s', j_data['errcode'], j_data.get('errmsg', ''))
            else:
                access_token = j_data['access_token']
                expires_in = j_data['expires_in']
                info('access token[:20]%s expire in %s', access_token[:20], expires_in)
                r.setex(c_k, access_token, expires_in)

        raise gen.Return(access_token)

    @staticmethod
    @gen.coroutine
    def getIpList():
        u'''获取微信服务器ip列表
        '''
        ip_list = []

        r = m_redis.get_instance()
        c_k = '_Z_WX_IP_LIST'
        ip_list = r.get(c_k)
        if ip_list:
            info('cache hit %s', c_k)
            raise gen.Return(ip_list)

        access_token = yield WXLoginManager.getAccessToken()
        if access_token:
            url = 'https://api.weixin.qq.com/cgi-bin/getcallbackip?access_token={ACCESS_TOKEN}'.format(ACCESS_TOKEN=access_token)
            try:
                httpc_lient = AsyncHTTPClient()
                resp = yield gen.Task(httpc_lient.fetch, url)  # , validate_cert = False)
                info('resp: %s', resp.body)
                j_data = json.loads(resp.body)
            except:
                error('', exc_info=True)
            else:
                if 'errcode' in j_data:
                    info('errcode %s, errmsg: %s', j_data['errcode'], j_data.get('errmsg', ''))
                    # 出错情况下 5秒内不重试
                    r.setex(c_k, json.dumps(ip_list), 5)
                else:
                    ip_list = j_data['ip_list']
                    info('ip_list: %s', ip_list)
                    r.setex(c_k, json.dumps(ip_list), 3600)
        else:
            info('can\'t get access_token, no ip list returned.')

        raise gen.Return(ip_list)

    @staticmethod
    def createText(nonce, encrypt_type, from_user, to_user, content):
        u'''构造文本消息

        ``content`` 为文本内容
        '''
        ret_data = 'success'
        to_xml = WXLoginManager.TPL_RETURN_TEXT.format(TOUSER=from_user, FROMUSER=to_user, TIME=int(time.time()), CONTENT=content)
        if encrypt_type == 'aes':
            encryp_helper = WXBizMsgCrypt(WXLoginManager.TOKEN, WXLoginManager.ENCODINGAESKEY, WXLoginManager.APPID)
            ret, encrypt_xml = encryp_helper.EncryptMsg(to_xml, nonce)
            if not ret:
                ret_data = str(encrypt_xml)
            else:
                info('加密失败 %s %s', ret, encrypt_xml)
        return ret_data

    @staticmethod
    def createImage(nonce, encrypt_type, from_user, to_user, media_id):
        u'''构造图片消息

        ``media_id`` 为图片素材id
        '''
        ret_data = 'success'
        to_xml = WXLoginManager.TPL_RETURN_IMAGE.format(TOUSER=from_user, FROMUSER=to_user, TIME=int(time.time()), MEDIA_ID=media_id)
        if encrypt_type == 'aes':
            encryp_helper = WXBizMsgCrypt(WXLoginManager.TOKEN, WXLoginManager.ENCODINGAESKEY, WXLoginManager.APPID)
            ret, encrypt_xml = encryp_helper.EncryptMsg(to_xml, nonce)
            if not ret:
                ret_data = str(encrypt_xml)
            else:
                info('加密失败 %s %s', ret, encrypt_xml)
        return ret_data

    @staticmethod
    def extractXml(nonce, encrypt_type, msg_sign, timestamp, from_xml):
        u'''解析接收的消息，以字典形式返回
        '''
        d_data = ''
#-#        info('raw data: %s', from_xml)
        if encrypt_type == 'aes':
            decrypt_helper = WXBizMsgCrypt(WXLoginManager.TOKEN, WXLoginManager.ENCODINGAESKEY, WXLoginManager.APPID)
            ret, decryp_xml = decrypt_helper.DecryptMsg(from_xml, msg_sign, timestamp, nonce)
            if not ret:
                from_xml = decryp_xml
            else:
                info('解密失败 %s %s', ret, decryp_xml)
        # parse to dict
        if from_xml:
            d_data = parseXml2Dict(from_xml)
#-#            info('接收:\n%s', pcformat(d_data))
        return d_data

    @staticmethod
    @gen.coroutine
    def getUserInfo(openid):
        u'''获取用户基本信息
        '''
        wx_user = None
        access_token = yield WXLoginManager.getAccessToken()
        if access_token:
            url = 'https://api.weixin.qq.com/cgi-bin/user/info?access_token={ACCESS_TOKEN}&openid={OPENID}&lang=zh_CN'.format(ACCESS_TOKEN=access_token, OPENID=openid)
            try:
                httpc_lient = AsyncHTTPClient()
                resp = yield gen.Task(httpc_lient.fetch, url)  # , validate_cert = False)
#-#                info('resp: %s', resp.body)  # debug only
                j_data = json.loads(resp.body)
            except:
                error('', exc_info=True)
            else:
                if j_data.get('errcode', None):
                    info('获取用户基本信息出错： errcode %s, errmsg: %s', j_data['errcode'], j_data.get('errmsg', ''))
                else:
                    wx_user = j_data
        else:
            info('can\'t get access_token, no ip list returned.')
        raise gen.Return(wx_user)

    @staticmethod
    @gen.coroutine
    def createSelfMenu():
        u'''创建自定义菜单

        * True 成功
        * False 失败
        '''
        ret_data = False
        access_token = yield WXLoginManager.getAccessToken()
        url = 'https://api.weixin.qq.com/cgi-bin/menu/create?access_token={ACCESS_TOKEN}'.format(ACCESS_TOKEN=access_token)
#-#        data = {'button': [{'type': 'view', 'name': u'快速下载', 'url': 'http://www.hongbaosuoping.com/client_share/download/download.html'},
#-#                           {'type': 'view', 'name': u'自助服务', 'url': 'http://www.hongbaosuoping.com/portal.php?mod=topic&topicid=9'},
#-#                           {'type': 'click', 'name': u'获取验证码', 'key': 'vcode'},
#-#                           ]
#-#                }
        login_cfg = {'APPID': WXLoginManager.APPID,
                     'REDIRECT_URI': quote('http://weixin.aa123bb.com/wx_auth'),
                     'SCOPE': 'snsapi_userinfo',
                     'STATE': 'login',
                     }
        test_cfg = {'APPID': WXLoginManager.APPID,
                    'REDIRECT_URI': quote('http://weixin.aa123bb.com/wx_auth'),
                    'SCOPE': 'snsapi_userinfo',
                    'STATE': 'test',
                    }
        data = {'button': [{'name': u'菜单',
                            'sub_button': [{'type': 'view',
                                            'name': '商城',
                                            'url': 'https://open.weixin.qq.com/connect/oauth2/authorize?appid={APPID}&redirect_uri={REDIRECT_URI}&response_type=code&scope={SCOPE}&state={STATE}#wechat_redirect'.format(**login_cfg)
                                            },
                                           {'type': 'view',
                                            'name': 'test',
                                            'url': 'https://open.weixin.qq.com/connect/oauth2/authorize?appid={APPID}&redirect_uri={REDIRECT_URI}&response_type=code&scope={SCOPE}&state={STATE}#wechat_redirect'.format(**test_cfg)
                                            },
                                           {'type': 'click',
                                            'name': '二维码',
                                            'key': 'qc_subscribe'
                                            },
                                           {'type': 'click',
                                            'name': '不存在',
                                            'key': 'not_exist'
                                            },
                                           ]
                            },
                           {'type': 'view',
                            'name': u'快速下载',
                            'url': 'http://cn.bing.com/'
                            },
                           {'type': 'view',
                            'name': u'自助服务',
                            'url': 'http://m.baidu.com/'
                            },
                           ]
                }
#-#        info('url: %s', url)  # debug only
#-#        info('body: %s', json.dumps(data))
        req = HTTPRequest(url, method='POST', body=json.dumps(data, ensure_ascii=False))  # , validate_cert = False)
        httpc_lient = AsyncHTTPClient()
        try:
            resp = yield gen.Task(httpc_lient.fetch, req)
            info('resp: %s', resp.body)  # debug only
            j_data = json.loads(resp.body)
        except:
            error('', exc_info=True)
        else:
            if j_data['errcode']:
                info('创建菜单出错: errcode %s, errmsg: %s', j_data['errcode'], j_data.get('errmsg', ''))
            else:
                ret_data = True
        raise gen.Return(ret_data)

    @staticmethod
    @gen.coroutine
    def getSelfMenu():
        u'''获取自定义菜单配置

        * 成功则返回json格式菜单配置信息
        * 失败则返回 None
        '''
        ret_data = None
        access_token = yield WXLoginManager.getAccessToken()
        url = '''https://api.weixin.qq.com/cgi-bin/get_current_selfmenu_info?access_token={ACCESS_TOKEN}'''.format(ACCESS_TOKEN=access_token)
        info('url: %s', url)
#-#        info('body: %s', json.dumps(data))
        req = HTTPRequest(url)  # , validate_cert = False)
        httpc_lient = AsyncHTTPClient()
        try:
            resp = yield gen.Task(httpc_lient.fetch, req)
            info('resp: %s', resp.body)
            j_data = json.loads(resp.body)
            ret_data = j_data
        except:
            error('', exc_info=True)
        raise gen.Return(ret_data)

    @staticmethod
    @gen.coroutine
    def sendTplMsg(tpl_id, openid, url, in_data):
        u'''发送模板消息

        * True 成功
        * False 失败
        '''
        ret_data = False
        access_token = yield WXLoginManager.getAccessToken()
        url = '''https://api.weixin.qq.com/cgi-bin/message/template/send?access_token={ACCESS_TOKEN}'''.format(ACCESS_TOKEN=access_token)
        data = {'touser': openid,
                'template_id': tpl_id,
                'url': url,
                'data': in_data,
                }
        info('url: %s', url)
        info('data: %s', pcformat(data))
#-#        info('body: %s', json.dumps(data))
        req = HTTPRequest(url, method='POST', body=json.dumps(data, ensure_ascii=False))  # , validate_cert = False)
        httpc_lient = AsyncHTTPClient()
        try:
            resp = yield gen.Task(httpc_lient.fetch, req)
            info('resp: %s', resp.body)
            j_data = json.loads(resp.body)
        except:
            error('', exc_info=True)
        else:
            if j_data['errcode']:
                info('发送模板消息出错: errcode %s, errmsg: %s', j_data['errcode'], j_data.get('errmsg', ''))
            else:
                ret_data = True
        raise gen.Return(ret_data)

    @staticmethod
    @gen.coroutine
    def createQrCodeTicket(data):
        u'''创建二维码ticket，一般不直接使用

        返回ticket或者None
        '''
        ret_data = None
        access_token = yield WXLoginManager.getAccessToken()
        url = 'https://api.weixin.qq.com/cgi-bin/qrcode/create?access_token={ACCESS_TOKEN}'.format(ACCESS_TOKEN=access_token)
        info('url: %s', url)
        info('data: %s', pcformat(data))
#-#        info('body: %s', json.dumps(data))
        req = HTTPRequest(url, method='POST', body=json.dumps(data, ensure_ascii=False))  # , validate_cert = False)
        httpc_lient = AsyncHTTPClient()
        try:
            resp = yield gen.Task(httpc_lient.fetch, req)
            info('resp: %s', resp.body)
            j_data = json.loads(resp.body)
        except:
            error('', exc_info=True)
        else:
            if j_data.get('errcode', None):
                info('创建二维码ticket出错: errcode %s, errmsg: %s', j_data['errcode'], j_data.get('errmsg', ''))
            else:
                ret_data = j_data
        raise gen.Return(ret_data)

    @staticmethod
    @gen.coroutine
    def getQrCodeByTicket(ticket):
        u'''通过ticket换取二维码，一般不直接使用

        返回二维码图片数据或者None
        '''
        ret_data = None
        url = 'https://mp.weixin.qq.com/cgi-bin/showqrcode?ticket={TICKET}'.format(TICKET=ticket)
        info('url: %s', url)
        req = HTTPRequest(url)  # , validate_cert = False)
        httpc_lient = AsyncHTTPClient()
        try:
            resp = yield gen.Task(httpc_lient.fetch, req)
            if resp.code == 200:
                info('%s %s', resp.headers['Content-Length'], len(resp.body))
                assert int(resp.headers['Content-Length']) == len(resp.body)
                info('resp[:20] %d: %s', len(resp.body), resp.body[:20])
                ret_data = resp.body
            else:
                info('获取二维码图片出错: http code %d', resp.code)
        except:
            error('', exc_info=True)
        raise gen.Return(ret_data)

    @staticmethod
    @gen.coroutine
    def getQrPicBySceneId(scene_id, want_temp=True):
        u'''通过场景值获取二维码图片数据

        * ``scene_id``
        * ``want_temp`` True 临时(默认)  False 永久

        返回二维码图片数据或者None
        '''
        pic_data = None
        max_expire = 604800
        r = m_redis.get_instance('ad')
        c_k = '_Z_WX_QR_%s' % scene_id
        ticket = r.get(c_k)
        if not ticket:
            if want_temp:
                if not isinstance(scene_id, int):
                    info('参数错误: 临时二维码的scene_id必须为32位非0整型!')
                    raise gen.Return(pic_data)
                data = {'expire_seconds': max_expire, 'action_name': 'QR_SCENE', 'action_info': {'scene': {'scene_id': scene_id}}}
            else:
                if isinstance(scene_id, int):
                    if not (0 < scene_id <= 100000):
                        info('参数错误: 永久二维码的scene_id为整数时，范围为(0,100000]')
                        raise gen.Return(pic_data)
                    data = {'expire_seconds': max_expire, 'action_name': 'QR_LIMIT_SCENE', 'action_info': {'scene': {'scene_id': scene_id}}}
                elif isinstance(scene_id, str):
                    if not (0 < len(scene_id) <= 64):
                        info('参数错误: 永久二维码的scene_id为字符串时，长度范围为[1,64]')
                        raise gen.Return(pic_data)
                    data = {'expire_seconds': max_expire, 'action_name': 'QR_LIMIT_STR_SCENE', 'action_info': {'scene': {'scene_str': scene_id}}}
                else:
                    info('参数错误: 永久二维码的scene_id应该为int或str')
                    raise gen.Return(pic_data)

            j_data = yield WXLoginManager.createQrCodeTicket(data)
            info('%s', pcformat(j_data))
            ticket = j_data['ticket']
            expire_at = j_data['expire_seconds']
            r.setex(c_k, ticket, expire_at)
        if ticket:
            pic_data = yield WXLoginManager.getQrCodeByTicket(ticket)
            open('/tmp/t.jpg', 'wb').write(pic_data)
        raise gen.Return(pic_data)

    @staticmethod
    @gen.coroutine
    def getMediaId(media_type, media_data, key=None):
        u'''获取素材id
        * ``media_type`` 素材类型 image/voice/video/thumb 之一
        * ``media_data`` 素材数据，如果 ``media_data`` 不为空 且 ``key`` 在缓存中查不到，则上传素材
        * ``key`` 指定的key值，以后可以设置 ``media_data`` 为空的情况下获取已经上传的素材id

        返回 media_id ，此数值可以用于构造图片消息
        '''
        media_id = None
        d_content_type = {'image': 'image/jpg',  # bmp/png/jpeg/jpg/gif
                          'voice': 'voice/mp3',  # mp3/wma/wav/amr
                          'video': 'video/mp4',
                          'thumb': 'thumb/jpg',
                          }
        if media_type not in d_content_type:
            info('unknown media_type %s', media_type)
            raise gen.Return(media_id)
        if not key:
            if not media_data:
                info('media_data 为空')
                raise gen.Return(media_id)
            key = md5(media_data).hexdigest()
        c_k = '_Z_WX_M_%s_%s' % (media_type, key)
        r = m_redis.get_instance()
        media_id = r.get(c_k)
        if not media_id:
            if not media_data:  # 缓存里面没有查到，必须先上传，media_type必须非空
                info('media_data 为空')
                raise gen.Return(media_id)
            access_token = yield WXLoginManager.getAccessToken()
            url = 'https://api.weixin.qq.com/cgi-bin/media/upload?access_token={ACCESS_TOKEN}&type={MEDIA_TYPE}'.format(ACCESS_TOKEN=access_token, MEDIA_TYPE=media_type)
#-#            info('url: %s', url)  # debug only
            nr_try = 1
            while 1:
                boundary = ''.join((random.choice(string.digits) for _ in xrange(32)))
                if media_data.find(boundary) == -1:
                    break
                nr_try += 1
            headers = HTTPHeaders({'Content-Type': 'multipart/form-data;boundary=%s' % boundary})
            form_body = '--%s\r\n' \
                        'Content-Disposition: form-data; name="media"; filename="upload.%s"\r\n' \
                        'Content-Type: %s\r\n' \
                        'FileLength: %s\r\n\r\n' \
                        '%s\r\n' \
                        '--%s--\r\n' \
                        % (boundary, d_content_type[media_type].split('/')[1], d_content_type[media_type], len(media_data), media_data, boundary)
#-#            info('form_body(header part):\n%s', form_body[:form_body.find('\r\n\r\n')])  # debug only
            req = HTTPRequest(url, method='POST', body=form_body, headers=headers)  # , validate_cert = False)
            httpc_lient = AsyncHTTPClient()
            try:
                resp = yield gen.Task(httpc_lient.fetch, req)
                info('resp: %s', resp.body)
                j_data = json.loads(resp.body)
            except:
                error('', exc_info=True)
            else:
                if j_data.get('errcode', None):
                    info('上传素材出错: errcode %s, errmsg: %s', j_data['errcode'], j_data.get('errmsg', ''))
                else:
                    media_id = j_data['media_id']
                    r.setex(c_k, media_id, 86400 * 3)
        else:
            info('cache hit %s', c_k)

        raise gen.Return(media_id)

    @staticmethod
    @gen.coroutine
    def _getOAuthAccessTokenOpenId(code, package_name):
        u'''通过code换取网页授权access_token, refresh_token 和 openid

        '''
        access_token, refresh_token, openid, err_code, err_msg = None, None, None, None, None
        r = m_redis.get_instance()
        c_k = '_Z_WX_O_ACCESS_TOKEN_%s' % code
        c_data = r.get(c_k)
        if c_data:
            access_token, openid = json.loads(c_data)
            info('cache hit %s', c_k)
            raise gen.Return((access_token, refresh_token, openid, err_code, err_msg))

        app_id, app_secret = WXLoginManager._getAppIdAndAppSecret(package_name)
        url = 'https://api.weixin.qq.com/sns/oauth2/access_token?appid={APPID}&secret={APPSECRET}&code={CODE}&grant_type=authorization_code'.format(APPID=app_id, APPSECRET=app_secret, CODE=code)
        try:
            httpc_lient = AsyncHTTPClient()
            resp = yield gen.Task(httpc_lient.fetch, url)  # , validate_cert = False)
            info('resp: %s', resp.body)
            j_data = json.loads(resp.body)
        except:
            error('', exc_info=True)
        else:
            if 'errcode' in j_data:
                err_code, err_msg = j_data['errcode'], j_data['errmsg']
                info('errcode %s, errmsg: %s', j_data['errcode'], j_data.get('errmsg', ''))
            else:
                access_token = j_data['access_token']
                refresh_token = j_data['refresh_token']
                expires_in = j_data['expires_in']
                openid = j_data['openid']
#-#                scope = j_data['scope']
#-#                unionid = j_data.get('unionid', '')
                info('access token[:20]%s expire in %s openid %s', access_token[:20], expires_in, openid)
                r.setex(c_k, json.dumps((access_token, openid)), expires_in)

        raise gen.Return((access_token, refresh_token, openid, err_code, err_msg))

    @staticmethod
    def _getAppIdAndAppSecret(package_name):
        index = IOSTwin.getIndex(package_name)
        return _options['wx_login%s_appid' % index], _options['wx_login%s_appsecret' % index]

    @staticmethod
    @gen.coroutine
    def _getOAuthUserInfo(access_token, openid):
        u'''拉取用户信息(需scope为 snsapi_userinfo)
        https://open.weixin.qq.com/cgi-bin/showdocument?action=dir_list&t=resource/res_list&verify=1&id=open1419317853&lang=zh_CN

        **参数**
         * ``access_token``
         * ``openid``

        **返回**
         * ``openid`` 用户的唯一标识
         * ``nickname`` 用户昵称
         * ``sex`` 用户的性别，值为1时是男性，值为2时是女性，值为0时是未知
         * ``province`` 用户个人资料填写的省份
         * ``city`` 普通用户个人资料填写的城市
         * ``country`` 国家，如中国为CN
         * ``headimgurl`` 用户头像，最后一个数值代表正方形头像大小（有0、46、64、96、132数值可选，0代表640*640正方形头像），用户没有头像时该项为空。若用户更换头像，原有头像URL将失效。
         * ``privilege`` 用户特权信息，json 数组，如微信沃卡用户为（chinaunicom）
         * ``unionid`` 只有在用户将公众号绑定到微信开放平台帐号后，才会出现该字段。详见：获取用户个人信息（UnionID机制）
        '''
        wx_user = None
        url = 'https://api.weixin.qq.com/sns/userinfo?access_token={ACCESS_TOKEN}&openid={OPENID}&lang=zh_CN'.format(ACCESS_TOKEN=access_token, OPENID=openid)
        try:
            httpc_lient = AsyncHTTPClient()
            resp = yield gen.Task(httpc_lient.fetch, url)  # , validate_cert = False)
            info('resp: %s', resp.body)  # debug only
            j_data = json.loads(resp.body)
        except:
            error('', exc_info=True)
        else:
            if 'errcode' in j_data:
                info('errcode %s, errmsg: %s', j_data['errcode'], j_data.get('errmsg', ''))
            else:
                wx_user = j_data

        raise gen.Return(wx_user)

    @staticmethod
    @gen.coroutine
    def getOAuthUserInfoByCode(code, package_name):
        u'''根据code获取用户基本信息
        '''
        wx_user = None
        access_token, refresh_token, openid, err_code, err_msg = yield WXLoginManager._getOAuthAccessTokenOpenId(code, package_name)
        if access_token:
            wx_user = yield WXLoginManager._getOAuthUserInfo(access_token, openid)
        raise gen.Return((access_token, wx_user, err_code, err_msg))

    @staticmethod
    @gen.coroutine
    def checkOAuthAccessToken(access_token, openid):
        u'''检查access_token有效性
        '''
        rtn = False
        url = 'https://api.weixin.qq.com/sns/auth?access_token={ACCESS_TOKEN}&openid={OPENID}'.format(ACCESS_TOKEN=access_token, OPENID=openid)
        try:
            httpc_lient = AsyncHTTPClient()
            resp = yield gen.Task(httpc_lient.fetch, url)  # , validate_cert = False)
#-#            info('resp: %s', resp.body)  # debug only
            j_data = json.loads(resp.body)
        except:
            error('', exc_info=True)
        else:
            if j_data['errcode']:
                info('errcode %s, errmsg: %s', j_data['errcode'], j_data.get('errmsg', ''))
            else:
                rtn = True

        raise gen.Return(rtn)

    @staticmethod
    @gen.coroutine
    def _refreshToken(refresh_token):
        u'''刷新access_token 有效期
        https://open.weixin.qq.com/cgi-bin/showdocument?action=dir_list&t=resource/res_list&verify=1&id=open1419317851&token=&lang=zh_CN

        **return**
         * ``access_token`` 接口调用凭证
         * ``expires_in`` access_token接口调用凭证超时时间，单位（秒）
         * ``refresh_token`` 用户刷新ccess_token
         * ``openid`` 授权用户唯一标识
         * ``scope`` 用户授权的作用域，使用逗号（,）分隔
        '''
        rtn = None
        url = 'https://api.weixin.qq.com/sns/refresh_token?app_id={APPID}&grant_type=refresh_token&refresh_token={REFRESH_TOKEN}'.format(APPID=WXLoginManager.APPID, REFRESH_TOKEN=refresh_token)
        try:
            httpc_lient = AsyncHTTPClient()
            resp = yield gen.Task(httpc_lient.fetch, url)  # , validate_cert = False)
#-#            info('resp: %s', resp.body)  # debug only
            j_data = json.loads(resp.body)
        except:
            error('', exc_info=True)
        else:
            if j_data['errcode']:
                info('errcode %s, errmsg: %s', j_data['errcode'], j_data.get('errmsg', ''))
            else:
                rtn = j_data

        raise gen.Return(rtn)

    @staticmethod
    @gen.coroutine
    def addKf(kf_account, nickname, password):
        u'''添加客服帐号
        '''
        ret_data = None
        access_token = yield WXLoginManager.getAccessToken()
        url = '''https://api.weixin.qq.com/customservice/kfaccount/add?access_token={ACCESS_TOKEN}'''.format(ACCESS_TOKEN=access_token)
        info('url: %s', url)
        data = {'kf_account': kf_account,
                'nickname': nickname,
                'password': password
                }
        req = HTTPRequest(url, method='POST', body=json.dumps(data, ensure_ascii=False))  # , validate_cert = False)
        httpc_lient = AsyncHTTPClient()
        try:
            resp = yield gen.Task(httpc_lient.fetch, req)
            j_data = json.loads(resp.body)
            ret_data = j_data
        except:
            error('', exc_info=True)
        raise gen.Return(ret_data)

    @staticmethod
    @gen.coroutine
    def updKf(kf_account, nickname, password):
        u'''修改客服帐号
        '''
        ret_data = None
        access_token = yield WXLoginManager.getAccessToken()
        url = '''https://api.weixin.qq.com/customservice/kfaccount/update?access_token={ACCESS_TOKEN}'''.format(ACCESS_TOKEN=access_token)
        info('url: %s', url)
        data = {'kf_account': kf_account,
                'nickname': nickname,
                'password': password
                }
        req = HTTPRequest(url, method='POST', body=json.dumps(data, ensure_ascii=False))  # , validate_cert = False)
        httpc_lient = AsyncHTTPClient()
        try:
            resp = yield gen.Task(httpc_lient.fetch, req)
            j_data = json.loads(resp.body)
            ret_data = j_data
        except:
            error('', exc_info=True)
        raise gen.Return(ret_data)

    @staticmethod
    @gen.coroutine
    def delKf(kf_account, nickname, password):
        u'''删除客服帐号
        '''
        ret_data = None
        access_token = yield WXLoginManager.getAccessToken()
        url = '''https://api.weixin.qq.com/customservice/kfaccount/del?access_token={ACCESS_TOKEN}'''.format(ACCESS_TOKEN=access_token)
        info('url: %s', url)
        data = {'kf_account': kf_account,
                'nickname': nickname,
                'password': password
                }
        req = HTTPRequest(url, method='POST', body=json.dumps(data, ensure_ascii=False))  # , validate_cert = False)
        httpc_lient = AsyncHTTPClient()
        try:
            resp = yield gen.Task(httpc_lient.fetch, req)
            j_data = json.loads(resp.body)
            ret_data = j_data
        except:
            error('', exc_info=True)
        raise gen.Return(ret_data)

    @staticmethod
    @gen.coroutine
    def kfSendMsg(msg_data):
        u'''客服发消息 不需要直接调用
        '''
        ret_data = None
        access_token = yield WXLoginManager.getAccessToken()
        url = '''https://api.weixin.qq.com/cgi-bin/message/custom/send?access_token={ACCESS_TOKEN}'''.format(ACCESS_TOKEN=access_token)
        info('url: %s', url)
        data = msg_data
        req = HTTPRequest(url, method='POST', body=json.dumps(data, ensure_ascii=False))
        httpc_lient = AsyncHTTPClient()
        try:
            resp = yield gen.Task(httpc_lient.fetch, req)  # , validate_cert = False)
            j_data = json.loads(resp.body)
            ret_data = j_data
        except:
            error('', exc_info=True)
        raise gen.Return(ret_data)

    @staticmethod
    @gen.coroutine
    def kfSendImageMsg(openid, media_id):
        u'''客服发送图片消息
        '''
        data = {'touser': openid,
                'msgtype': 'image',
                'image': {'media_id': media_id},
                }
        r = yield WXLoginManager.kfSendMsg(data)
        raise gen.Return(r)

    @staticmethod
    @gen.coroutine
    def kfSendTextMsg(openid, content):
        u'''客服发送文本消息
        '''
        data = {'touser': openid,
                'msgtype': 'text',
                'text': {'content': content},
                }
        r = yield WXLoginManager.kfSendMsg(data)
        raise gen.Return(r)

if __name__ == '__main__':
    @gen.coroutine
    def test_main():
        pass
#-#        yield WXLoginManager.sendTplMsg(TPL_SEND_VC, 'owD3VszZ1r115U-DVYLMdCWU1AVE', '',
#-#                                   {'first': {'value': u'尊敬的用户'}, 'number': {'value': str(random.randint(1000, 9999)), 'color': '#FF3300'}, 'remark': {'value': u'该验证码有效期30分钟可输入1次，转发无效。'}})

#-#        pic_data = yield WXLoginManager.getQrPicBySceneId(1)
#-#        open('/tmp/t.jpg', 'wb').write(pic_data)

#-#        pic_data = open('/tmp/t.jpg', 'rb').read()
#-#        media_id = yield WXLoginManager.getMediaId('image', pic_data, 'test_qr')

#-#        image_data, ticket, expire_at = yield WXLoginManager.getQrPicBySceneId(1)
        media_id = yield WXLoginManager.getMediaId('image', None, key='qrcode_subs')
        info('media_id %s', media_id)
        r = yield WXLoginManager.kfSendImageMsg('olQcFt_RHZqgL9CyNuDuyy21hhKg', media_id)
        info('r: %s', r)

    from tornado.ioloop import IOLoop
#-#    IOLoop.instance().run_sync(WXLoginManager.getAccessToken)
#-#    IOLoop.instance().run_sync(WXLoginManager.getIpList)
#-#    IOLoop.instance().run_sync(WXLoginManager.createSelfMenu)
#-#    IOLoop.instance().run_sync(WXLoginManager.getSelfMenu)
    IOLoop.instance().run_sync(test_main)
