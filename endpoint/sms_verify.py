# coding=utf-8

import hug
from hug import types
import lib.err_code as err_code
from lib.tools import tools
from lib.logger import info, error
from applib.verify_lib import VerifyLib

@hug.get('/send_sms_code.do', examples='os_type=ios&app_version=1.1.0.0&channel=share&package_name=com.test.package&pnum=1862753079&device_id=llllllfffff')
async def send_sms_code(request, pnum: int,
                        device_id: types.text,
                        os_type: types.text,
                        app_version: types.text,
                        channel: types.text,
                        package_name: types.text):
    """
    """
    print(dir(request))
    print(request.raw_headers)

    ip = request.remote_addr
    if not tools.get_counting(pnum, 30):
        return tools.response(code=1, message="访问次数过于频繁， 请30秒后重试")
    code = VerifyLib.get_random_code()
    res = await VerifyLib.send_code(pnum, code, package_name, ip)
    if not res:
        return tools.response(code=err_code._ERR_SMS_SEND_FAILED, message="发送失败")
    return tools.response(code=0, message="发送成功")

#  for test
@hug.get('/async_add_code.do', examples='os_type=ios&app_version=1.1.0.0&channel=share&package_name=com.test.package&pnum=1862753079&device_id=llllllfffff')
async def async_add_code(request, pnum: int,
                         device_id: types.text,
                         os_type: types.text,
                         app_version: types.text,
                         channel: types.text,
                         package_name: types.text):
    """
    """
    code = VerifyLib.get_random_code()
    res = await VerifyLib.add_code(pnum, '', code, package_name, '1.0.0.0', 'ios')
    return tools.response(code=0, message="发送成功")

@hug.get('/add_code.do', examples='os_type=ios&app_version=1.1.0.0&channel=share&package_name=com.test.package&pnum=1862753079&device_id=llllllfffff')
async def add_code(request, pnum: int,
             device_id: types.text,
             os_type: types.text,
             app_version: types.text,
             channel: types.text,
             package_name: types.text):
    """
    """
    code = VerifyLib.get_random_code()
    res = VerifyLib.add_code_test(pnum, '', code, package_name, '1.0.0.0', 'ios')  # pnum, device_id, code, package_name, app_version, os_type
    return tools.response(code=0, message="发送成功")
