# coding=utf-8

import hug
from hug import types
from falcon import HTTP_400
from lib.tools import tools
from lib import redisManager
from lib.logger import info, error
from applib.user_lib import UserManager

@hug.get('/version.do', examples='os_type=ios&app_version=1.1.0.0&uid=10000001&ticket=hdfkdshjkbdfhsdkfhd&rs=mb&channel=share&package_name=com.test.package')
async def version(request, os_type: types.text, app_version: types.text, uid: int, ticket: types.text, rs: types.text, channel: types.text, package_name: types.text):
    """获取版本更新信息
    rs : reg_resource  mb, wb, qq, wx ... etc
    ticket : 用户验证串
    """
    res = await get_version(os_type, app_version, uid)
    return res

async def get_version(os_type, app_version, uid):
    r_key = redisManager._APP_VERSION_ + app_version
    res = tools.get_obj_cache(r_key)
    if res:
        return res
    m = tools.mysql_conn()
    m.Q("SELECT id, channel, parent_id, remark, ctime, channel_type FROM a_channel_set WHERE status = 1;")  # 参数绑定防止sql注入
    res = m.fetch_one()
    ret = {"data": res, "code": 0}
    tools.set_cache_obj(r_key, ret, 60 * 60 * 24)
    return ret
