# coding=utf-8
import random, string
import traceback
from itsdangerous import URLSafeTimedSerializer
from itsdangerous import SignatureExpired
from itsdangerous import BadSignature
from lib.redis_cache import cache
from lib.tools import tools, http_put
from lib.logger import info, error
import lib.err_code as err_code
import conf.settings as settings

class UserLib(object):
    # reg_source 取值
    REG_SOURCE_DESC = {'wx': '微信号',
                       'qq': 'QQ号',
                       'wb': '新浪微博号',
                       'mb': '手机号'}

    # 用户VIP类型
    USER_VIP_TYPE_NONE = 0  # 不是VIP
    USER_VIP_TYPE_INVITE = 1  # 邀请狂人
    USER_VIP_TYPE_BANKER = 2  # 庄家

    @staticmethod
    async def add_user(obj):
        '''
         * `reg_qid` 注册id 即微信/qq/微博的openid或者手机号
         * `token`
         * `reg_source` 注册模式 wx:微信 qq:QQ，wb:新浪微博 mb:手机号
         * `invite_uid` 邀请uid
         * `ip` 注册ip
         * `os_type` os类型
         * `device_id` device_id
         * `app_version` 注册来自的app版本号
         * `channel` 渠道
         * `nickname`
         * `gender`
         * `figure_url`
         * `figure_url_other` 其他头像
         * `province`
         * `city`
         * `country`
         * `year` 出生年
        '''
        ret = {'uid': None, 'ticket': None, 'message': '', 'code': 0}
        if obj['invite_uid']:
            res = UserLib.check_user_by_uid(obj['invite_uid'])
            if not res:
                info('邀请人无效 %s', obj['invite_uid'])
                obj['invite_uid'] = '0'
        else:
            obj['invite_uid'] = '0'

        res = UserLib.get_info_by_qid(obj['reg_qid'], obj['reg_source'])
        if res:
            ret['message'] = '%s已注册，请直接登陆' % UserLib.REG_SOURCE_DESC.get(obj['reg_source'], '')
            ret['code'] = err_code._ERR_ALREADY_REGISTERED
            return ret

        m = tools.mysql_conn()
        m_score = None
        r = tools.get_redis()
        try:
            salt = UserLib.get_salt()
            sql = "INSERT INTO o_user_basic(ctime, channel, os_type, app_version, package_name, reg_ip, invite_uid, reg_source, reg_qid, salt, device_id, status) " \
                  "VALUES(NOW(), %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 1)"
            args = (obj['channel'], obj['os_type'], obj['app_version'], obj['package_name'], obj['reg_ip'], obj['invite_uid'], obj['reg_source'], obj['reg_qid'], salt, obj['device_id'])
            m.TQ(sql, args)
            uid = m.db.insert_id()
            assert uid
            m_score = tools.mysql_conn('d')
            if obj['reg_source'] == 'mb':  # 手机号注册，昵称默认为139*****888这种（隐藏中间5位）
                obj['nickname'] = '%s*****%s' % (str(obj['reg_qid'])[:3], str(obj['reg_qid'])[-3:])
            obj['nickname'] = obj['nickname'].strip()  # 有一些用户名前后有空格或空行，处理一下

            ticket = await UserLib.get_new_ticket(uid, obj['reg_qid'], salt)
            sql = "INSERT INTO o_user_extra(uid, reg_source, reg_qid, token, nickname, gender, figure_url, figure_url_other, province, city, country, year) " \
                  "VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
            args = (uid, obj['reg_source'], obj['reg_qid'], obj['token'], obj['nickname'], obj['gender'], obj['figure_url'], obj['figure_url_other'], obj['province'], obj['city'], obj['country'], obj['year'])
            m.TQ(sql, args)
            # info('uid: %s, score_table: %s' % (uid, UserLib._which_score_table(uid)))
            m_score.TQ("INSERT INTO %s (uid, score) VALUES(%%s, %%s)" % UserLib._which_score_table(uid), (uid, 0))
            m.db.commit()
            m_score.db.commit()
            UserLib.clear_cache(uid, obj['reg_qid'], obj['reg_source'])
        except:
            traceback.print_exc()
            try:
                m.db.rollback()
            except:
                pass
            if m_score:
                try:
                    m_score.db.rollback()
                except:
                    pass
            error('数据库错误, 添加新用户时出错', exc_info=True)
            ret['message'] = '注册失败'
            ret['code'] = err_code._ERR_REGISTERED_ERROR
            return ret

        info('用户注册成功 reg_qid: %s uid: %s ticket: %s', obj['reg_qid'], uid, ticket)
        ret['uid'] = uid
        ret['ticket'] = ticket
        return ret

    def clear_cache(uid, qid, reg_source):
        cache.invalidate(UserLib.check_user_by_uid, uid)
        cache.invalidate(UserLib.get_user_info_by_uid, uid)
        cache.invalidate(UserLib.get_info_by_qid, qid, '')
        cache.invalidate(UserLib.get_info_by_qid, qid, reg_source)

    @staticmethod
    @cache.cache()
    def check_user_by_uid(uid):
        '''判断id为 `uid` 的用户是否存在
        **return**
         <True or False>
        '''
        ret = False
        m = tools.mysql_conn('r')
        m.Q("SELECT uid FROM o_user_basic WHERE uid = %s ", (uid,))
        rs = m.fetchone()
        if rs:
            ret = True
        return ret

    @staticmethod
    @cache.cache()
    def get_info_by_qid(qid, reg_source=''):
        m = tools.mysql_conn('r')
        if reg_source:
            sql = "SELECT uid FROM o_user_basic WHERE reg_source = %s AND reg_qid = %s;"
            args = (reg_source, qid)
        else:
            sql = "SELECT uid FROM o_user_basic WHERE reg_qid=%s;"
            args = (qid, )
        m.Q(sql, args)
        return m.fetchone()

    @staticmethod
    @cache.cache()
    def get_info_by_bind_mobile(bind_mobile, reg_source=''):
        m = tools.mysql_conn('r')
        if reg_source:
            sql = "SELECT uid, qid FROM o_user_basic WHERE reg_source = %s AND bind_mobile = %s;"
            args = (reg_source, bind_mobile)
        else:
            sql = "SELECT uid, qid FROM o_user_basic WHERE bind_mobile = %s;"
            args = (bind_mobile, )
        m.Q(sql, args)
        return m.fetchone()

    @staticmethod
    def _which_score_table(uid):
        return "o_user_score_%s" % str(uid)[-1]

    @staticmethod
    def _which_score_log_table(uid):
        return "o_score_log_%s" % str(uid)[-2:]

    @staticmethod
    @cache.as_cache()
    async def get_user_info_by_uid(uid):
        m = tools.mysql_conn('r')
        sql = "SELECT a.uid, a.channel, a.invite_uid, a.reg_qid, a.bind_mobile, b.nickname, b.gender, b.figure_url, b.province, b.city, b.country, a.reg_source, a.ctime, a.os_type, a.salt FROM o_user_basic a, o_user_extra b WHERE a.uid = b.uid AND a.uid = %s"
        m.Q(sql, (uid,))
        return m.fetchone()

    def get_salt():
        return ''.join(random.sample(list(string.ascii_letters), 6))

    async def update_salt(uid, salt):
        m = tools.mysql_conn()
        sql = "UPDATE o_user_basic SET salt = %s WHERE uid = %s"
        m.Q(sql, (salt, uid))
        cache.invalidate(UserLib.get_user_info_by_uid, uid)

    async def check_ticket(ticket, uid):
        ret = {'data' : None, 'message': '', 'code': 0}
        res = await UserLib.get_user_info_by_uid(uid)
        salt = res['salt'] if res else ''
        sig = URLSafeTimedSerializer(settings.TOKEN_SECRET_KEY, salt)
        try:
            res = sig.loads(ticket, max_age = 60 * 60 * 24 * 30)
        except BadSignature:
            ret['code'] = err_code._ERR_USER_VALIDATE_WRONG
            ret['message'] = '为保证账户安全，请重新登录'
            return ret  # ticket 无效
        except SignatureExpired:
            ret['code'] = err_code._ERR_USER_VALIDATE_WRONG
            ret['message'] = '为保证账户安全，请重新登录'
            return ret# ticket 过期
        else:
            ret['data'] = res
            return ret

    async def get_new_ticket(uid, qid, salt = ''):
        if not salt:
            res = await UserLib.get_user_info_by_uid(uid)
            salt = res['salt'] if res else ''
        ticket = URLSafeTimedSerializer(settings.TOKEN_SECRET_KEY, salt).dumps({'uid': uid, 'qid': qid})
        return ticket
