# coding=utf-8

import hug
from hug import types
import lib.err_code as err_code
from applib.user_lib import UserLib
from lib.tools import tools
from lib.logger import info, error

@hug.get('/init.do', examples='os_type=ios&app_init=1.1.0.0&channel=share&package_name=com.test.package&uid=10000000&ticket=eyJ1aWQiOjEwMDAwMDAwLCJxaWQiOiIxNTgxMDUzODA5OCJ9.Cq3LVA.Cj-xAUb5ipibHbW89ISKcPGl56w')
async def init(request,
               os_type: types.text,
               app_init: types.text,
               channel: types.text,
               package_name: types.text = 'com.test.package',
               uid: types.number  = -1,
               ticket: types.text = ''):
    """app init 接口
    """
    res = await UserLib.check_ticket(ticket, uid)
    ret = res['data']
    if uid <= 0:
        return tools.response()
    elif uid and ret:
        info(ret)
        res = await UserLib.get_new_ticket(ret['uid'], ret['qid'])
        info(ticket)
        return tools.response([{'new_ticket': res}])
    return tools.response(code=err_code._ERR_TICKET_ERR, message="身份验证失败")
