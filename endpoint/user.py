# coding=utf-8

import hug
from hug import types
from marshmallow import fields
from falcon import HTTP_400
import lib.err_code as err_code
from lib.auth import check_ticket, get_new_ticket
from lib.tools import tools
from lib.logger import info, error

@hug.get('/init.do', examples='os_type=ios&app_init=1.1.0.0&channel=share&package_name=com.test.package&uid=10000000&ticket=eyJ1aWQiOjEwMDAwMDAwLCJxaWQiOiIxNTgxMDUzODA5OCJ9.Cq1XzA.Gd5OK8NppLtTz62f9qP9Ii21PNk')
async def init(request,
               os_type: types.text,
               app_init: types.text,
               channel: types.text,
               package_name: types.text = 'com.test.package',
               uid: fields.Int()  = -1,
               ticket: types.text = ''):
    """app init 接口
    """
    code, message, ret = check_ticket(ticket)
    if uid <= 0:
        return tools.response()
    elif uid and ret:
        res = get_new_ticket(ret['uid'], ret['qid'])
        return tools.response([{'new_ticket': res}])
    return tools.response(code=err_code._ERR_TICKET_ERR, message="身份验证失败")
