# coding=utf-8

import hug
from hug import types
from falcon import HTTP_400
from lib.tools import tools
from lib.logger import info, error
from applib.user_lib import UserManager
from applib.message_lib import MessageLib

@hug.get('/msg_list.do', examples='last_msg_id=-1&os_type=ios&app_version=1.1.0.0&uid=10000000&channel=share&package_name=com.test.package')
def message_list(request, last_msg_id: int, os_type: types.text, app_version: types.text, channel: types.text, package_name: types.text = 'com.test.package', uid: int  = -1):
    """获取消息列表
    """
    if uid <= 0 and token_authorization() is False:
        return tools.response(MessageLib.get_msg_list(last_msg_id))
    elif uid and token_authorization():
        return tools.response(MessageLib.get_msg_list(last_msg_id, uid))
