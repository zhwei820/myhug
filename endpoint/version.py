# coding=utf-8

import hug
from hug import types
from marshmallow import fields
from falcon import HTTP_400
import lib.err_code
from lib.auth import token_authorization
from lib.tools import tools
from lib.logger import info, error
from applib.version_lib import VersionLib

@hug.get('/version.do', examples='os_type=ios&app_version=1.1.0.0&uid=10000001&ticket=hdfkdshjkbdfhsdkfhd&rs=mb&channel=share&package_name=com.test.package')
async def version(request, os_type: types.text, app_version: types.text, uid: fields.Int(), channel: types.text, package_name: types.text):
    """获取版本更新信息:
    """
    if uid <= 0 and token_authorization(request) is False:
        return tools.response(VersionLib.get_version(os_type, app_version))
    elif uid and token_authorization(request):
        return tools.response(VersionLib.get_version(os_type, app_version, str(uid)[-2:]))
    return tools.response(code=err_code._ERR_TICKET_ERR, message="身份验证失败")
