# coding=utf-8

import hug
from hug import types
import lib.err_code as err_code
from applib.user_lib import UserLib
from lib.tools import tools
from lib.logger import info, error
from applib.version_lib import VersionLib

@hug.get('/version.do', examples='os_type=ios&app_version=1.1.0.0&channel=share&package_name=com.test.package&uid=10000000&ticket=eyJ1aWQiOjEwMDAwMDAwLCJxaWQiOiIxNTgxMDUzODA5OCJ9.Cq3LVA.Cj-xAUb5ipibHbW89ISKcPGl56w')
async def version(request,
                  os_type: types.text,
                  app_version: types.text,
                  channel: types.text,
                  package_name: types.text = 'com.test.package',
                  uid: types.number  = -1,
                  ticket: types.text = ''):
    """
    """
    if uid <= 0:
        return tools.response(VersionLib.get_version(os_type, app_version))
    elif uid and await UserLib.check_ticket(ticket, uid):
        return tools.response(VersionLib.get_version(os_type, app_version, str(uid)[-2:]))
    return tools.response(code=err_code._ERR_TICKET_ERR, message="身份验证失败")
