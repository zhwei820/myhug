# coding=utf-8

import hug
from hug import types
import lib.err_code as err_code
from lib.tools import tools
from lib.logger import info, error
from applib.verify_lib import VerifyLib

@hug.get('/send_sms_code.do')
async def send_sms_code(request, pnum: int,
                        device_id: types.text,
                        os_type: types.text,
                        app_version: types.text,
                        channel: types.text,
                        package_name: types.text):
    """
summary: Hello Swagger
description: |
    发送手机验证码    

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

============================== outputs

definitions:
  response_msg:
    type: object
    properties:
      code:
        type: "integer"
        description: 自定义错误码, 0 为返回正常
      message:
        type: "string"
        description: 返回错误信息
 
    """

    ip = tools.get_real_ip(request)
    if not tools.get_counting(pnum, 30):
        return tools.response(code=1, message="访问次数过于频繁， 请30秒后重试")
    code = VerifyLib.get_random_code()
    res = await VerifyLib.send_code(pnum, code, package_name, ip)
    if not res:
        return tools.response(code=err_code._ERR_SMS_SEND_FAILED, message="发送失败")
    return tools.response(code=0, message="发送成功")

