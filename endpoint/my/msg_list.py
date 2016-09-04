# coding=utf-8

import hug
from hug import types
from marshmallow import fields
from falcon import HTTP_400
from lib.tools import tools
from lib.auth import check_ticket
from lib.logger import info, error
import lib.err_code as err_code
from applib.message_lib import MessageLib

@hug.get('/msg_list.do', examples='last_msg_id=-1&os_type=ios&app_version=1.1.0.0&channel=share&package_name=com.test.package&uid=10000000&ticket=eyJ1aWQiOjEwMDAwMDAwLCJxaWQiOiIxNTgxMDUzODA5OCJ9.Cq1XzA.Gd5OK8NppLtTz62f9qP9Ii21PNk')
def message_list(request,
                 last_msg_id: fields.Int(),
                 os_type: types.text,
                 app_version: types.text,
                 channel: types.text,
                 package_name: types.text = 'com.test.package',
                 uid: fields.Int()  = -1,
                 ticket: types.text = ''):
    """获取消息列表 \n\n
    """
    if uid <= 0:
        return tools.response(MessageLib.get_msg_list(last_msg_id))
    elif uid and check_ticket(ticket):
        return tools.response(MessageLib.get_msg_list(last_msg_id, uid))
    return tools.response(code=err_code._ERR_TICKET_ERR, message="身份验证失败")
