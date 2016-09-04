# -*- coding: utf-8  -*-
import sys
reload(sys)
sys.setdefaultencoding('utf8')
import time
import random
import string
from datetime import datetime
from hashlib import md5
from urllib import urlencode
#-#from urllib import quote
#-#from operator import itemgetter
from itertools import chain
from tornado import gen
from tornado.options import options as _options
from tornado.httpclient import AsyncHTTPClient
from tornado.httpclient import HTTPRequest
if __name__ == '__main__':
    import sys
    import os
    par_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir))
    sys.path.append(par_dir)
    import server_conf
    server_conf
from applib.tools_lib import pcformat
from applib.tools_lib import parseXml2Dict
from applib.tools_lib import dict2Xml
from lib.applog import app_log
info, debug, error = app_log.info, app_log.debug, app_log.error


class WXPayManager(object):
    CHARS = string.ascii_letters + string.digits

    def __init__(self, pkg_name='', mch_id=''):
        self.setConf(pkg_name, mch_id)

    def setConf(self, pkg_name='', mch_id=''):
        u'''根据包名确定相关配置
        '''
        if pkg_name == 'com.ppdb.papapa' or mch_id == _options.one_wx_mch_id_1:
            self.APPID = _options.one_wx_appid_1
            self.MCH_ID = _options.one_wx_mch_id_1
            self.PAY_KEY = _options.one_wx_pay_key_1
            self.NOTIFY_URL = _options.one_wx_notify_url_1
        else:
            self.APPID = _options.one_wx_appid  # appid 微信开放平台->管理中心->应用详情
            self.MCH_ID = _options.one_wx_mch_id  # 商户号 https://pay.weixin.qq.com/index.php/account
            self.PAY_KEY = _options.one_wx_pay_key  # 微信商户平台(pay.weixin.qq.com)-->账户设置-->API安全-->密钥设置
            self.NOTIFY_URL = _options.one_wx_notify_url  # 回调地址

    def _get_wx_pay_sign(self, d_data):
        u'''获取支付签名
        '''
        s = '&'.join(chain(('%s=%s' % (_k, _v.encode('utf8') if isinstance(_v, unicode) else str(_v)) for _k, _v in sorted(((_k, _v) for _k, _v in d_data.iteritems() if _k != 'sign' and _v))), ('key=%s' % self.PAY_KEY, )))
        return md5(s).hexdigest().upper()

    def _check_wx_pay_sign(self, d_data):
        u'''验证支付签名
        '''
        if (not d_data) or ('sign' not in d_data) or (not d_data['sign']):
            return False
        return self._get_wx_pay_sign(d_data) == d_data['sign']

    @gen.coroutine
    def _fetchUrl(self, url, method='GET', d_data=None):
        err_code, err_msg, ret_data = 0, '', None

        req = HTTPRequest(url, method=method, body=dict2Xml(d_data) if d_data else None)  # , validate_cert=False)
        httpc_lient = AsyncHTTPClient()
        try:
            resp = yield gen.Task(httpc_lient.fetch, req)
#-#            info('resp: %s', resp.body)  # debug only
            d_rslt = parseXml2Dict(resp.body)
        except:
            error('', exc_info=True)
        else:
#-#            info('d_rslt: %s', pcformat(d_rslt))
            if 'return_code' not in d_rslt:
                info('wx return data no return_code !!! %s', d_rslt)
                err_code = -1
                err_msg = u'微信端返回数据，但没有return_code!'
            elif d_rslt['return_code'] != 'SUCCESS':  # 通信不成功
                err_code = -1
                err_msg = d_rslt['return_msg']
            elif not self._check_wx_pay_sign(d_rslt):
                info('check wx pay sign failed !!! %s', d_rslt)
                err_code = -1
                err_msg = u'微信端返回数据，但签名校验不通过！'
            else:
                ret_data = d_rslt

        raise gen.Return((err_code, err_msg, ret_data))

    @gen.coroutine
    def unifiedOrder(self, body, detail, out_trade_no, total_fee, spbill_create_ip, openid='',
                     time_start='', time_expire='', device_info='WEB',
                     attach='', fee_type='CNY', goods_tag='',
                     trade_type='JSAPI', product_id='', limit_pay=''):
        u'''微信支付统一下单 https://pay.weixin.qq.com/wiki/doc/api/jsapi.php?chapter=9_1
        '''
        ret_data = {'err_code': '',
                    'err_msg': ''
                    }
        url = 'https://api.mch.weixin.qq.com/pay/unifiedorder'
        nonce_str = ''.join((random.choice(WXPayManager.CHARS) for _ in xrange(32)))
        d_data = {'appid': self.APPID,
                  'mch_id': self.MCH_ID,
                  'device_info': device_info,
                  'nonce_str': nonce_str,
                  'body': body,
                  'detail': detail,
                  'attach': attach,
                  'out_trade_no': out_trade_no,
                  'fee_type': fee_type,
                  'total_fee': total_fee,
                  'spbill_create_ip': spbill_create_ip,
                  'time_start': time_start,
                  'time_expire': time_expire,
                  'goods_tag': goods_tag,
                  'notify_url': self.NOTIFY_URL,
                  'trade_type': trade_type,
                  'product_id': product_id,
                  }
        if limit_pay == 'no_credit':
            d_data['limit_pay'] = limit_pay
        if openid:
            d_data['openid'] = openid
        sign = self._get_wx_pay_sign(d_data)
        d_data['sign'] = sign

        err_code, err_msg, d_rslt = yield self._fetchUrl(url, 'POST', d_data)
        if err_code == -1:
            ret_data['err_code'] = err_code
            ret_data['err_msg'] = err_msg
        else:
            _r_appid = d_rslt['appid']
            assert _r_appid == self.APPID
            _r_mch_id = d_rslt['mch_id']
            assert _r_mch_id == self.MCH_ID
#-#                _r_device_info = d_rslt['device_info']
#-#                _r_nonce_str = d_rslt['nonce_str']
#-#                _r_sign = d_rslt['sign']
            result_code = d_rslt['result_code']
            if result_code == 'SUCCESS':  # 获得预支付交易会话标识
#-#                    ret_data['trade_type'] = d_rslt['trade_type']
#-#                    ret_data['prepay_id'] = d_rslt['prepay_id']
#-#                    ret_data['code_url'] = d_rslt.get('code_url', '')
#-#                    # 生成网页端调起支付API所需参数
#-#                    d = {'appId': self.APPID,
#-#                         'timeStamp': str(int(time.time())),
#-#                         'nonceStr': ''.join((random.choice(WXPayManager.CHARS) for _ in xrange(32))),
#-#                         'package': 'prepay_id=%s' % ret_data['prepay_id'],
#-#                         'signType': 'MD5',
#-#                         }
                # 生成app端调起微信所需参数
                d = {'appid': self.APPID,
                     'partnerid': self.MCH_ID,
                     'prepayid': d_rslt['prepay_id'],
                     'package': 'Sign=WXPay',
                     'noncestr': ''.join((random.choice(WXPayManager.CHARS) for _ in xrange(32))),
                     'timestamp': str(int(time.time())),
                     }
                code_url = d_rslt.get('code_url')
                if code_url:
                    d['code_url'] = code_url
                sign = self._get_wx_pay_sign(d)
#-#                    d['paySign'] = sign
                d['sign'] = sign
#-#                    ret_data.update(d)
                ret_data['pay_args'] = urlencode(d)
            else:
                ret_data['err_code'] = d_rslt['err_code']
                ret_data['err_msg'] = d_rslt['err_code_des']

        raise gen.Return(ret_data)

    @gen.coroutine
    def payCallBack(self, handler, resp_data, succ_call_back, fail_call_back):
        u'''处理微信支付结果 https://pay.weixin.qq.com/wiki/doc/api/jsapi.php?chapter=9_7
        '''
        info('resp: %s', repr(resp_data))  # debug only
        ret_code, ret_msg = 'FAIL', u'未知错误'
        d = parseXml2Dict(resp_data)
        return_code, return_msg = d.get('return_code', ''), d.get('return_msg', '')
        if return_code == 'SUCCESS':
            self.setConf(mch_id=d['mch_id'])
            if self._check_wx_pay_sign(d):
                ret_code = 'SUCCESS'
                ret_msg = ''
                result_code = d['result_code']
                err_code = d.get('err_code', '')
                err_code_des = d.get('err_code_des', '')
                out_trade_no = d['out_trade_no']  # recharge_id
                appid = d['appid']
                assert appid == self.APPID
                mch_id = d['mch_id']
#-#                assert mch_id == self.MCH_ID
                time_end = d['time_end']
                total_fee = d['total_fee']
                # debug
                info('[notify]交易%s @%s recharge %s fee %s %s %s', result_code, datetime.strptime(time_end, '%Y%m%d%H%M%S').strftime('%Y-%m-%d_%H:%M:%S'), out_trade_no, total_fee, err_code, err_code_des)

                if result_code == 'SUCCESS':
                    # 支付成功
                    pay_args = {'pay_trade_no': d['transaction_id'],
                                'pay_seller_id': mch_id,
                                'pay_user_id': d['openid'],
                                'pay_status': result_code,
                                'pay_remark': u'付款%s@%s' % (total_fee, datetime.strptime(time_end, '%Y%m%d%H%M%S').strftime('%Y-%m-%d_%H:%M:%S')),
                                }
                    ret_msg, ret_data = yield succ_call_back(handler, out_trade_no, **pay_args)
                else:
                    # 支付超时/失败
                    pay_args = {'pay_trade_no': d['transaction_id'],
                                'pay_seller_id': mch_id,
                                'pay_user_id': d['openid'],
                                'pay_status': result_code,
                                'pay_remark': u'失败%s@%s' % (total_fee, datetime.strptime(time_end, '%Y%m%d%H%M%S').strftime('%Y-%m-%d_%H:%M:%S')),
                                }
            else:
                ret_msg = u'签名失败'
        else:
            ret_code, ret_msg = return_code, return_msg

        raise gen.Return((ret_code, ret_msg))

    @gen.coroutine
    def orderQuery(self, transaction_id, out_trade_no):
        u'''查询订单 https://pay.weixin.qq.com/wiki/doc/api/jsapi.php?chapter=9_2
        '''
        ret_data = {'err_code': '',
                    'err_msg': ''
                    }
        url = 'https://api.mch.weixin.qq.com/pay/orderquery'
        nonce_str = ''.join((random.choice(WXPayManager.CHARS) for _ in xrange(32)))
        d_data = {'appid': self.APPID,
                  'mch_id': self.MCH_ID,
                  'transaction_id': transaction_id,
                  'out_trade_no': out_trade_no,
                  'nonce_str': nonce_str,
                  }
        sign = self._get_wx_pay_sign(d_data)
        d_data['sign'] = sign

        err_code, err_msg, d_rslt = yield self._fetchUrl(url, 'POST', d_data)
        if err_code == -1:
            ret_data['err_code'] = err_code
            ret_data['err_msg'] = err_msg
        else:
            _r_appid = d_rslt['appid']
            assert _r_appid == self.APPID
            _r_mch_id = d_rslt['mch_id']
            assert _r_mch_id == self.MCH_ID
            result_code = d_rslt['result_code']
            if result_code == 'SUCCESS':  # 获得预支付交易会话标识
                ret_data['device_id'] = d_rslt.get('device_id', '')
                ret_data['openid'] = d_rslt.get('openid')
                ret_data['is_subscribe'] = d_rslt.get('is_subscribe', '')
                ret_data['trade_type'] = d_rslt.get('trade_type')

                # SUCCESS—支付成功
                # REFUND—转入退款
                # NOTPAY—未支付
                # CLOSED—已关闭
                # REVOKED—已撤销（刷卡支付）
                # USERPAYING--用户支付中
                # PAYERROR--支付失败(其他原因，如银行返回失败)
                ret_data['trade_state'] = d_rslt['trade_state']
                ret_data['bank_type'] = d_rslt.get('bank_type')
                ret_data['total_fee'] = d_rslt.get('total_fee')
                ret_data['fee_type'] = d_rslt.get('fee_type', '')
                ret_data['cash_fee'] = d_rslt.get('cash_fee')
                ret_data['cash_fee_type'] = d_rslt.get('cash_fee_type', '')
                ret_data['coupon_fee'] = d_rslt.get('coupon_fee', '')
                ret_data['coupon_count'] = d_rslt.get('coupon_count', 0)
                for _i in xrange(ret_data.get('coupon_count', 0)):
                    ret_data['coupon_batch_id_%d' % _i] = d_rslt['coupon_batch_id_%d' % _i]
                    ret_data['coupon_id_%d' % _i] = d_rslt['coupon_id_%d' % _i]
                    ret_data['coupon_fee_%d' % _i] = d_rslt['coupon_fee_%d' % _i]
                ret_data['transaction_id'] = d_rslt.get('transaction_id')
                ret_data['out_trade_no'] = d_rslt['out_trade_no']
                ret_data['attach'] = d_rslt.get('attach', '')
                ret_data['time_end'] = d_rslt.get('time_end')
                ret_data['trade_state_desc'] = d_rslt.get('trade_state_desc', '')  # 文档描述此参数不为空，但测试此参数可能为空
        raise gen.Return(ret_data)

    @gen.coroutine
    def closeOrder(self, out_trade_no):
        u'''关闭订单 https://pay.weixin.qq.com/wiki/doc/api/jsapi.php?chapter=9_3
        '''
        ret_data = {'err_code': '',
                    'err_msg': ''
                    }
        url = 'https://api.mch.weixin.qq.com/pay/closeorder'
        nonce_str = ''.join((random.choice(WXPayManager.CHARS) for _ in xrange(32)))
        d_data = {'appid': self.APPID,
                  'mch_id': self.MCH_ID,
                  'out_trade_no': out_trade_no,
                  'nonce_str': nonce_str,
                  }
        sign = self._get_wx_pay_sign(d_data)
        d_data['sign'] = sign

        err_code, err_msg, d_rslt = yield self._fetchUrl(url, 'POST', d_data)
        if err_code == -1:
            ret_data['err_code'] = err_code
            ret_data['err_msg'] = err_msg
        else:
            _r_appid = d_rslt['appid']
            assert _r_appid == self.APPID
            _r_mch_id = d_rslt['mch_id']
            assert _r_mch_id == self.MCH_ID
            ret_data['err_code'] = d_rslt.get('err_code', '')
            ret_data['err_msg'] = d_rslt.get('err_code_desc', '')
#-#                ret_data['result_code'] = d_rslt.get('result_code', '')

        raise gen.Return(ret_data)

    @gen.coroutine
    def refund(self, transaction_id, out_trade_no, total_fee, refund_fee):
        u'''申请退款 https://pay.weixin.qq.com/wiki/doc/api/jsapi.php?chapter=9_4
        '''
        ret_data = {'err_code': '',
                    'err_msg': ''
                    }
        url = 'https://api.mch.weixin.qq.com/secapi/pay/refund'
        nonce_str = ''.join((random.choice(WXPayManager.CHARS) for _ in xrange(32)))
        d_data = {'appid': self.APPID,
                  'mch_id': self.MCH_ID,
                  'nonce_str': nonce_str,
                  'transaction_id': transaction_id,
                  'out_trade_no': out_trade_no,
                  'out_refund_no': out_trade_no,  # 商户系统内部的退款单号，商户系统内部唯一，同一退款单号多次请求只退一笔
                  'total_fee': total_fee,
                  'refund_fee': refund_fee,
                  'refund_fee_type': 'CNY',
                  'op_user_id': self.MCH_ID,
                  }
        sign = self._get_wx_pay_sign(d_data)
        d_data['sign'] = sign

        err_code, err_msg, d_rslt = yield self._fetchUrl(url, 'POST', d_data)
        if err_code == -1:
            ret_data['err_code'] = err_code
            ret_data['err_msg'] = err_msg
        else:
            _r_appid = d_rslt['appid']
            assert _r_appid == self.APPID
            _r_mch_id = d_rslt['mch_id']
            assert _r_mch_id == self.MCH_ID
            ret_data['result_code'] = d_rslt['result_code']  # SUCCESS/FAIL SUCCESS退款申请接收成功，结果通过退款查询接口查询 FAIL 提交业务失败

        raise gen.Return(ret_data)

    @gen.coroutine
    def refundQuery(self, transaction_id, out_trade_no, total_fee, refund_fee):
        u'''退款查询 https://pay.weixin.qq.com/wiki/doc/api/jsapi.php?chapter=9_5
        '''
        ret_data = {'err_code': '',
                    'err_msg': ''
                    }
        url = 'https://api.mch.weixin.qq.com/pay/refundquery'
        nonce_str = ''.join((random.choice(WXPayManager.CHARS) for _ in xrange(32)))
        d_data = {'appid': self.APPID,
                  'mch_id': self.MCH_ID,
                  'nonce_str': nonce_str,
                  'transaction_id': transaction_id,
                  'out_trade_no': out_trade_no,
                  }
        sign = self._get_wx_pay_sign(d_data)
        d_data['sign'] = sign

        err_code, err_msg, d_rslt = yield self._fetchUrl(url, 'POST', d_data)
        if err_code == -1:
            ret_data['err_code'] = err_code
            ret_data['err_msg'] = err_msg
        else:
            _r_appid = d_rslt['appid']
            assert _r_appid == self.APPID
            _r_mch_id = d_rslt['mch_id']
            assert _r_mch_id == self.MCH_ID
            ret_data['result_code'] = d_rslt['result_code']  # SUCCESS/FAIL SUCCESS退款申请接收成功，结果通过退款查询接口查询 FAIL 提交业务失败

        raise gen.Return(ret_data)

    @gen.coroutine
    def downloadBill(self, bill_date, bill_type='ALL'):
        u''' 下载对账单 https://pay.weixin.qq.com/wiki/doc/api/jsapi.php?chapter=9_6
        '''
        ret_data = {'err_code': '',
                    'err_msg': ''
                    }
        url = 'https://api.mch.weixin.qq.com/pay/downloadbill'
        nonce_str = ''.join((random.choice(WXPayManager.CHARS) for _ in xrange(32)))
        d_data = {'appid': self.APPID,
                  'mch_id': self.MCH_ID,
                  'nonce_str': nonce_str,
                  'bill_date': bill_date,
                  'bill_type': bill_type,
                  }
        sign = self._get_wx_pay_sign(d_data)
        d_data['sign'] = sign
        req = HTTPRequest(url, method='POST', body=dict2Xml(d_data))  # , validate_cert=False)
        info('req.body: %s', req.body)
        httpc_lient = AsyncHTTPClient()
        try:
            resp = yield gen.Task(httpc_lient.fetch, req)
#-#            info('resp: %s', resp.body)  # debug only
#-#            d_rslt = parseXml2Dict(resp.body)
        except:
            error('', exc_info=True)
        else:  # TODO 实际测试
            info('resp.body: %s', resp.body)

        raise gen.Return(ret_data)

    @gen.coroutine
    def transferToOpenid(self, user_trade_no, user_openid, amount, desc, ip, user_name=None):
        u''' 企业付款 https://pay.weixin.qq.com/wiki/doc/api/mch_pay.php?chapter=14_2
        '''
        ret_data = {'err_code': '',
                    'err_msg': ''
                    }
        url = 'https://api.mch.weixin.qq.com/mmpaymkttransfers/promotion/transfers'
        d_data = {'mch_appid': self.APPID,
                  'mchid': self.MCH_ID,
                  'nonce_str': ''.join((random.choice(WXPayManager.CHARS) for _ in xrange(32))),
                  'partner_trade_no': user_trade_no,  # 商户订单号
                  'openid': user_openid,  # 商户appid下，某用户的openid
                  'check_name': 'OPTION_CHECK' if user_name else 'NO_CHECK',  # NO_CHECK：不校验真实姓名 FORCE_CHECK：强校验真实姓名（未实名认证的用户会校验失败，无法转账） OPTION_CHECK：针对已实名认证的用户才校验真实姓名（未实名认证用户不校验，可以转账成功）
                  're_user_name': user_name,  # 收款用户真实姓名。 如果check_name设置为FORCE_CHECK或OPTION_CHECK，则必填用户真实姓名
                  'amount': amount,  # 企业付款金额，单位为分
                  'desc': desc,  # 企业付款操作说明信息。必填。
                  'spbill_create_ip': ip,
                  }
        sign = self._get_wx_pay_sign(d_data)
        d_data['sign'] = sign
        req = HTTPRequest(url, method='POST', body=dict2Xml(d_data))  # , validate_cert=False)
        info('req.body: %s', req.body)
        httpc_lient = AsyncHTTPClient()
        try:
            resp = yield gen.Task(httpc_lient.fetch, req)
#-#            info('resp: %s', resp.body)  # debug only
#-#            d_rslt = parseXml2Dict(resp.body)
        except:
            error('', exc_info=True)
        else:  # TODO 实际测试
            info('resp.body: %s', resp.body)

        raise gen.Return(ret_data)

    @gen.coroutine
    def getTransferInfo(self, user_trade_no):
        u''' 查询企业付款 https://pay.weixin.qq.com/wiki/doc/api/mch_pay.php?chapter=14_3
        '''
        ret_data = {'err_code': '',
                    'err_msg': ''
                    }
        url = 'https://api.mch.weixin.qq.com/mmpaymkttransfers/gettransferinfo'
        d_data = {'appid': self.APPID,  # 商户号的appid
                  'mch_id': self.MCH_ID,  # 微信支付分配的商户号
                  'nonce_str': ''.join((random.choice(WXPayManager.CHARS) for _ in xrange(32))),
                  'partner_trade_no': user_trade_no,  # 商户调用企业付款API时使用的商户订单号
                  }
        sign = self._get_wx_pay_sign(d_data)
        d_data['sign'] = sign
#-#        req = HTTPRequest(url, method='POST', body=dict2Xml(d_data))
        client_key = '/home/kevin/data_bk/work/source/dup_zhuan/zhuan/apiclient_key.pem'
        client_cert = '/home/kevin/data_bk/work/source/dup_zhuan/zhuan/apiclient_cert.pem'
        ca_certs = '/home/kevin/data_bk/work/source/dup_zhuan/zhuan/rootca.pem'
        req = HTTPRequest(url=url, method='POST', client_key=client_key, client_cert=client_cert, ca_certs=ca_certs, body=dict2Xml(d_data))
        info('req.body: %s', req.body)
        httpc_lient = AsyncHTTPClient()
        try:
            resp = yield gen.Task(httpc_lient.fetch, req)
#-#            info('resp: %s', resp.body)  # debug only
#-#            d_rslt = parseXml2Dict(resp.body)
        except:
            error('', exc_info=True)
        else:  # TODO 实际测试
            info('resp.body: %s', resp.body)

        raise gen.Return(ret_data)


if __name__ == '__main__':
    from IPython import embed
    embed

    @gen.coroutine
    def test_main():
        pass
#-#        rslt = yield WXPayManager.unifiedOrder('olQcFt_RHZqgL9CyNuDuyy21hhKg,', u'测试商品body', u'测试商品detail', '12345678', 100, '192.168.199.112', trade_type='APP')
        rslt = yield WXPayManager().unifiedOrder(u'测试商品body', u'测试商品detail', '12345679c', 100, '192.168.199.112', trade_type='NATIVE', product_id='xxx')
        info('rslt: %s', pcformat(rslt))
#-#        if 'pay_args' in rslt:
#-#            info('%s', repr(rslt['pay_args']))
#-#        rslt = yield WXPayManager().orderQuery('1008450740201411110005820873', '12345678')
#-#        info('rslt: %s', pcformat(rslt))
#-#        rslt = yield WXPayManager().transferToOpenid('12345678', 'olQcFt_RHZqgL9CyNuDuyy21hhKg', 1, u'测试企业付款', '192.168.199.112', user_name=None)
#-#        info('rslt: %s', pcformat(rslt))

#-#        rslt = yield WXPayManager().getTransferInfo('12345678')
#-#        info('rslt: %s', pcformat(rslt))
#-#        s = '''<xml><appid><![CDATA[wxd7638e7c7c727042]]></appid>\n<bank_type><![CDATA[CFT]]></bank_type>\n<cash_fee><![CDATA[100]]></cash_fee>\n<device_info><![CDATA[WEB]]></device_info>\n<fee_type><![CDATA[CNY]]></fee_type>\n<is_subscribe><![CDATA[N]]></is_subscribe>\n<mch_id><![CDATA[1293673701]]></mch_id>\n<nonce_str><![CDATA[yzsrehuDGrxJIkLFh3rME3XZo75u103X]]></nonce_str>\n<openid><![CDATA[o_vNFv6loQ2AdDXXCM41fUHoY1ZA]]></openid>\n<out_trade_no><![CDATA[230]]></out_trade_no>\n<result_code><![CDATA[SUCCESS]]></result_code>\n<return_code><![CDATA[SUCCESS]]></return_code>\n<sign><![CDATA[C10A2AD73D2D71AE7D2E58281883E0A4]]></sign>\n<time_end><![CDATA[20160106162040]]></time_end>\n<total_fee>100</total_fee>\n<trade_type><![CDATA[APP]]></trade_type>\n<transaction_id><![CDATA[1009200993201601062541053281]]></transaction_id>\n</xml>'''
#-#        req = HTTPRequest('http://b-api.aa123bb.com/test_wx_cb.do', method='POST', body=s)
#-#        httpc_lient = AsyncHTTPClient()
#-#        try:
#-#            resp = yield gen.Task(httpc_lient.fetch, req)
#-#        except:
#-#            error('', exc_info=True)
#-#        else:
#-#            info('resp:\n%s', resp.body)

    from tornado.ioloop import IOLoop
    IOLoop.instance().run_sync(test_main)
