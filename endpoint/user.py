# coding=utf-8

import hug
from hug import types
import lib.err_code as err_code
from applib.user_lib import UserLib
from lib.tools import tools
from lib.logger import info, error

@hug.get('/init.do')
async def init(request,
               os_type: types.text,
               app_version: types.text,
               device_id: types.text,
               device_name: types.text,
               channel: types.text,
               package_name: types.text = 'com.test.package',
               uid: types.number  = -1,
               ticket: types.text = ''):
    """
summary: init
description: |
    应用初始化接口

parameters:
  - name: pnum
    in: query
    description: 手机号
    required: true
    type: number
    format: int
  - name: device_id
    in: query
    description: 设备号
    required: true
    type: string
  - name: device_name
    in: query
    description: 设备型号名称
    required: true
    type: string
  - name: os_type
    in: query
    description: 用户系统： android, os_type
    required: true
    type: string
  - name: app_version
    in: query
    description: 应用版本号 
    required: true
    type: string
  - name: channel
    in: query
    description: 应用渠道号
    required: true
    type: string
  - name: package_name
    in: query
    description: 应用包名
    required: true
    type: string
tags:
    - user

responses:
    200:
        description: An array of price estimates by product
        schema:
            $ref: "#/definitions/response_msg"


    """
    return tools.response()
    
    res = await UserLib.check_ticket(ticket, uid)
    ret = res['data']
    if uid <= 0:  # when to update log in ticket ?
        pass
    elif uid and ret:
        info(ret)
        res = await UserLib.get_new_ticket(ret['uid'], ret['qid'])
        info(ticket)
        return tools.response([{'new_ticket': res}])
    return tools.response(code=err_code._ERR_TICKET_ERR, message="身份验证失败")
