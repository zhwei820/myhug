from lib.redis_cache import cache
from lib.tools import tools, http_put
from lib.logger import info, error
import random, json, traceback
import conf.settings as settings


class VerifyLib():
    sms_url = {}
    verify_sms_channel = {}
    def _init_():
        self.sms_url = settings.SMS_URL
        self.verify_sms_channel = settings.VERIFY_SMS_CHANNEL

    @staticmethod
    @cache.as_cache()
    async def async_cache_test():
        return "test"

    @staticmethod
    async def add_code(pnum, device_id, code, package_name, app_version, os_type):
        m = tools.mysql_conn()
        try:
            sql = "INSERT INTO o_verify_log (pnum, device_id, status, code, package_name, app_version, os_type) \
                   VALUES(%s,%s,%s,%s,%s,%s,%s)"
            m.Q(sql, (pnum, device_id, 0, code, package_name, app_version, os_type))
            r_id = int(m.cur.lastrowid)
            cache.invalidate(VerifyLib.get_code_by_pnum, pnum)
            return r_id
        except:
            info('添加错误')
            traceback.print_exc()
            return False

    @staticmethod
    @cache.cache()
    def get_code_by_pnum(pnum):
        m = tools.mysql_conn('r')
        m.Q("SELECT code FROM o_verify_log WHERE pnum = %s ORDER BY id DESC LIMIT 1;", (pnum, ))  # 参数绑定防止sql注入
        res = m.fetch_one()
        return res['code'] if res else None

    @staticmethod
    def get_random_code():
        return random.randint(1000, 9999)

    @staticmethod
    async def send_code(pnum, code, package_name, client_ip):
        msg = '验证码：%s。为了您的帐号安全，验证码请勿转发给他人' % code
        channel = VerifyLib.verify_sms_channel.get(package_name, '100')
        sign = '【红包锁屏】'
        data = json.dumps({'mno': str(pnum),  # 目标手机号
                           'channel': channel,  # 渠道号
                           'msg': msg,  # 内容，对语音就是4-8位验证码，对短信就是完整的短信内容
                           'offer_code': '',  # 强制指定通道发送 默认是空
                           'ip': client_ip,  # 目标ip
                           'sign': sign,  # 短信签名
                           })
        url = VerifyLib.sms_url.get(package_name, '100')
        response = await http_put(url, data=data)
        if response:
            rs = None
            try:
                rs = json.loads(response.body)
            except:
                info('json错误: pnum: %s, channel: %s, return_body: %s' % (pnum, channel, str(response.body)))
            if not rs:
                info('验证码发送失败. pnum: %s. rs is None', pnum)
                return False
            elif rs["res"] != 1:
                info('发送验证码失败: pnum: %s, channel: %s, return_body: %s' % (pnum, channel, str(response.body)))
                return False
            else:
                return True

    @staticmethod
    def sms_verify(code, pnum):
        _code = VerifyLib.get_code_by_pnum(pnum)
        return _code == code
