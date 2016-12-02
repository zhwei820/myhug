# coding=utf-8

import hug
from hug import types
from lib.tools import tools
from applib.user_lib import UserLib
from lib.logger import info, error
import lib.err_code as err_code
from applib.message_lib import MessageLib

@hug.get('/msg_list.do', examples='last_msg_id=-1&os_type=ios&app_version=1.1.0.0&channel=share&package_name=com.test.package&uid=10000000&ticket=eyJ1aWQiOjEwMDAwMDAwLCJxaWQiOiIxNTgxMDUzODA5OCJ9.Cq3LVA.Cj-xAUb5ipibHbW89ISKcPGl56w')
async def message_list(request,
                 last_msg_id: types.number,
                 os_type: types.text,
                 app_version: types.text,
                 channel: types.text,
                 package_name: types.text = 'com.test.package',
                 uid: types.number  = -1,
                 ticket: types.text = ''):
    """
    """
    if uid <= 0:
        return tools.response(MessageLib.get_msg_list(last_msg_id))
    res = await UserLib.check_ticket(ticket, uid)
    if res['data']:
        return tools.response(MessageLib.get_msg_list(last_msg_id, uid))
    return tools.response(code=err_code._ERR_TICKET_ERR, message="身份验证失败")
