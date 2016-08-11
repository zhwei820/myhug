# coding=utf-8

import hug
from hug import types
from falcon import HTTP_400
from lib.tools import tools
from lib import redisManager
from lib.logger import info, error
from applib.user_lib import UserManager
from applib.message_lib import MessageLib

@hug.get('/msg_list.do', examples='last_msg_id=-1&os_type=ios&app_version=1.1.0.0&uid=10000000&ticket=hdfkdshjkbdfhsdkfhd&rs=mb&channel=share&package_name=com.test.package')
def message_list(request, last_msg_id: int, os_type: types.text, app_version: types.text, uid: int, ticket: types.text, rs: types.text, channel: types.text, package_name: types.text):
    """获取版本更新信息
    rs : reg_resource  mb, wb, qq, wx ... etc
    ticket : 用户验证串
    """
    return MessageLib.get_msg_list(last_msg_id, uid)
