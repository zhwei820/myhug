from lib.rc import cache
from lib.tools import tools
from lib import redisManager
from lib.logger import info, error
import random
from decouple import config


class VerifyLib():
    @staticmethod
    def add_code(pnum, device_id, status, code, package_name, app_version, os_type):
        m = tools.mysql_conn()
        try:
            sql = "INSERT INTO o_verify_log (pnum, device_id, status, code, package_name, app_version, os_type) \
                   VALUES(%s,%s,%s,%s,%s,%s,%s)"
            m.Q(sql, (pnum, device_id, status, code, package_name, app_version, os_type))
            r_id = int(m.cur.lastrowid)
            return r_id
        except:
            return False

    @staticmethod
    def save_code(self, last_id, code):
        m = tools.mysql_conn()
        try:
            sql = "UPDATE o_verify_log SET status = 1, code = %s WHERE id = %s;"
            m.Q(sql, (int(code), int(last_id)))
            return True
        except:
            return False

    @staticmethod
    @cache.cache()
    def get_code_by_pnum(pnum):
        m = tools.mysql_conn('r')
        m.Q("SELECT code FROM o_verify_log WHERE pnum = %s ORDER BY id DESC LIMIT 1;", (pnum, ))  # 参数绑定防止sql注入
        res = m.fetch_one()
        return res['code'] if res and res[9] else None

    @staticmethod
    def get_random_code():
        return random.randint(1000, 9999)

    @staticmethod
    def send_code(pnum, code, package_name):
        msg = '验证码：%s。为了您的帐号安全，验证码请勿转发给他人' % code
        channel = config('verify_sms_channel', default='100').get(package_name, '100')
        sign = '【红包锁屏】'
        data = json.dumps({'mno': str(pnum),  # 目标手机号
                           'channel': channel,  # 渠道号
                           'msg': msg,  # 内容，对语音就是4-8位验证码，对短信就是完整的短信内容
                           'offer_code': '',  # 强制指定通道发送 默认是空
                           'ip': client_ip,  # 目标ip
                           'sign': sign,  # 短信签名
                           })
        url = config('sms_url', default='http://rest.yxpopo.com/message_center/voice_verify/send').get(package_name, '100')
        http_client = httpclient.AsyncHTTPClient()
        response = yield gen.Task(http_client.fetch, url, method='PUT', body=data)
        rs = None
        try:
            rs = json.loads(response.body)
        except:
            info('json错误: pnum: %s, validate_type: %s, channel: %s, return_body: %s' % (pnum, validate_type, channel, str(response.body)))
        if not rs:
            info('验证码发送失败. pnum: %s. rs is None', pnum)
            self.writeS({'re': '', 'msg': ''}, self.err._ERR_SMS_SENT_FAIL, u'验证码发送失败，请稍后再试', callback)
            return
        elif rs["res"] != 1:
            info('%s 发送%s验证码失败 %s %s', pnum, '语音' if validate_type == 1 else '短信', code, pcformat(rs))
            self.writeS({'re': rs["res"], 'msg': rs["msg"]}, self.err._ERR_SMS_SENT_FAIL, u'验证码发送失败，请稍后再试', callback)
            return
        else:
            r.setex(r_key, 1, 2)
