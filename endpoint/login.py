#!/usr/bin/env python
# coding=utf-8

import hug
from hug import types
from falcon import HTTP_400
from lib.tools import tools
from lib.logger import info, error
from lib.redis_manager import Redis
from applib.user_lib import UserManager


@hug.post('/login', examples='openid=15810538008&os_type=ios&app_version=1.1.0.0&rs=mb&access_token=10000dkjdksjfkds&channel=share&package_name=com.test.package&invite_uid=10000000&gender=m')
def regster(request, openid: types.text,
            access_token: types.text,
            rs: types.text,
            invite_uid: int,
            os_type: types.text,
            app_version: types.text,
            channel: types.text,
            package_name: types.text,
            nickname: types.text = '',
            gender: types.text = '',
            figure_url: types.text = '',
            figure_url_other: types.text = '',
            province: types.text = '',
            city: types.text = '',
            country: types.text = '',
            year: types.text = ''):
    ip = request.remote_addr
    uid, ticket, err_msg = UserManager.add_user({
        'reg_qid': openid,
        'token': access_token,
        'reg_source': rs,
        'invite_uid': invite_uid,
        'reg_ip': ip,
        'os_type': os_type,
        'app_version': app_version,
        'channel': channel,
        'package_name': package_name,
        'nickname': nickname,
        'gender': gender,
        'figure_url': figure_url,
        'figure_url_other': figure_url_other,
        'province': province,
        'city': city,
        'country': country,
        'year': year,
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
