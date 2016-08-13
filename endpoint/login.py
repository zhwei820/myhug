#!/usr/bin/env python
# coding=utf-8

import hug
from hug import types
from falcon import HTTP_400
from lib.tools import tools
from lib.logger import info, error
from lib import redisManager
from applib.user_lib import UserManager


@hug.post('/login')
def regster(request, openid: types.text, access_token: types.text, reg_source: types.text, invite_uid: int, os_type: types.text, app_version: types.text, channel: types.text):
    ip = request.remote_addr
    uid, ticket, err_msg = UserManager.addUser(tools, {
        'reg_qid': openid,
        'token': access_token,
        'reg_source': reg_source,
        'invite_uid': invite_uid,
        'ip': ip,
        'os_type': os_type,
        'app_version': app_version,
        'channel': channel
        })
    return {"uid": uid, "ticket": ticket, "message": err_msg, "code": 0}

@hug.get()
def quick(response):
    if status < 0:
        response.status = HTTP_400
    return 'Serving!'

@hug.get("/hello")
async def hello_world():
    res = await test()
    return "Hello"

async def test():
    # time.sleep(1)
    # asyncio.sleep(0.1)
    return "haha"

@hug.get('/channel', examples='channel=test')
async def channel(request, channel: types.text):
    """get channel info"""
    res = await get_channel(channel)
    return res

async def get_channel(channel):
    r_key = redisManager._CHANNEL_INFO_ + channel
    res = tools.get_obj_cache(r_key)
    if res:
        return res
    m = tools.mysql_conn('r')
    m.Q("SELECT id, channel, parent_id, remark, ctime, channel_type FROM a_channel_set WHERE status = 1 AND channel like '%s' limit 1;" % (channel + '%'))  # 参数绑定防止sql注入
    res = m.fetch_one()
    ret = {"data": res, "code": 0}
    tools.set_cache_obj(r_key, ret, 60 * 60 * 24)
    return ret

@hug.get('/channel_list', examples=' ')
async def channel_list(request):
    """get channel info"""
    res = await get_channel_list()
    return res

async def get_channel_list():
    r_key = redisManager._CHANNEL_INFO_LIST_ + channel
    res = tools.get_obj_cache(r_key)
    if res:
        return res
    m = tools.mysql_conn('r')
    m.Q("SELECT id, channel, parent_id, remark, ctime, channel_type FROM a_channel_set WHERE status = 1;")  # 参数绑定防止sql注入
    res = m.fetch_all()
    ret = {"data": res, "code": 0}
    tools.set_cache_obj(r_key, ret, 60 * 60 * 24)
    return ret
