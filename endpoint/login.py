#!/usr/bin/env python
# coding=utf-8

import hug
from hug import types
from lib.tools import tools
from lib.logger import info, error
from applib.user_lib import UserLib


@hug.post('/login', examples='openid=15810538008&os_type=ios&device_id=fake_device_id_12345678&app_version=1.1.0.0&rs=mb&access_token=10000dkjdksjfkds&channel=share&package_name=com.test.package&invite_uid=10000000&gender=m')
async def login():
    uid, err_code, err_msg = None, 0, ''
    ret = {'data' : None, 'message': '', 'code': 0}

    if ticket:
        ret = await UserLib.check_ticket(ticket, uid)
        if ret['data']:
            await self.login_return_common(usc, uid, ticket, callback)
        else:
            self.writeS(None, self.err._ERR_ONE_LOGIN_ERROR_, err_msg or u'登录失败，请稍后再试', callback)
    else:
        if reg_source == 'mb':
            await self.login_return_common(usc, uid, ticket, callback)
        elif reg_source == 'wx':
            await self.login_weixin(usc, callback, post_data, reg_source, invite_uid, ip, os_type, app_version, channel, package_name)
        elif reg_source == 'qq':
            await self.login_qq(usc, callback, post_data, reg_source, invite_uid, ip, os_type, app_version, channel, package_name)
        elif reg_source == 'wb':
            await self.login_wb(usc, callback, post_data, reg_source, invite_uid, ip, os_type, app_version, channel, package_name)

async def regster(request, openid: types.text,
            access_token: types.text,
            rs: types.text,
            invite_uid: int,
            os_type: types.text,
            device_id: types.text,
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
            year: types.text = '1900'):
    ''' 用户注册接口
    '''
    ip = request.remote_addr
    ret = await UserLib.add_user({
        'reg_qid': openid,
        'token': access_token,
        'reg_source': rs,
        'invite_uid': invite_uid,
        'reg_ip': ip,
        'os_type': os_type,
        'device_id': device_id,
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
    return tools.response(ret)
