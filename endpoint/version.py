# coding=utf-8

import hug
from hug import types
from falcon import HTTP_400
from lib.tools import tools
from lib import redisManager
from lib.logger import info, error
from applib.version_lib import VersionLib

@hug.get('/version.do', examples='os_type=ios&app_version=1.1.0.0&uid=10000001&ticket=hdfkdshjkbdfhsdkfhd&rs=mb&channel=share&package_name=com.test.package')
async def version(request, os_type: types.text, app_version: types.text, uid: int, ticket: types.text, rs: types.text, channel: types.text, package_name: types.text):
    """获取版本更新信息
    rs : reg_resource  mb, wb, qq, wx ... etc
    ticket : 用户验证串
    """
    res = VersionLib.get_version(os_type, app_version, str(uid)[-2:])
    return res
