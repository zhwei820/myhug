# coding=utf-8

import hug
from hug import types
from falcon import HTTP_400
import lib.err_code as err_code
from lib.tools import tools
from lib.logger import info, error
from applib.sms_verify import VerifyLib

@hug.get('/send_sms_code.do', examples='os_type=ios&app_version=1.1.0.0&channel=share&package_name=com.test.package&pnum=1862753079&device_id=llllllfffff')
async def send_sms_code(request, pnum: int, device_id: types.text, os_type: types.text, app_version: types.text, channel: types.text, package_name: types.text):
    """发送短信验证码
    每30秒发一条
    """
    if not tools.get_counting(pnum, 30):
        return tools.response(code=1, message="访问次数过于频繁， 请30秒后重试")
    code = VerifyLib.get_random_code()
    res = await VerifyLib.send_code(pnum, code, package_name)
    if not res:
        return tools.response(code=err_code._ERR_SMS_SEND_FAILED, message="发送失败")
    return tools.response(code=0, message="发送成功")

@hug.get('/sms_verify.do', examples='os_type=ios&app_version=1.1.0.0&channel=share&package_name=com.test.package&pnum=1862753079&device_id=llllllfffff&code=1000')
async def sms_verify(request, code: int, pnum: int, device_id: types.text, os_type: types.text, app_version: types.text, channel: types.text, package_name: types.text):
    _code = VerifyLib.get_code_by_pnum(pnum)
    if _code = code:
        # pass
        return tools.response(code=0, message="验证成功")
    else:
        return tools.response(code=err_code._ERR_SMS_VERIFY_FAILED, message="验证失败")
