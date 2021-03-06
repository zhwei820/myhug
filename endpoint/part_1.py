import hug
import datetime, asyncio
from hug import types
from lib.tools import tools
from applib.verify_lib import VerifyLib

@hug.get("/ping")
@hug.post("/ping")
async def ping(request):
    """
Description end-point

---
tags:
  - user
summary: 健康检查
description: 健康检查
produces:
  - application/json
responses:
    "201":
        description: 检查结果

    """

    return "pong"

async def hello():
    await asyncio.sleep(0.1)
    return "haha"

@hug.get("/hello")
async def hello_world(callback: types.text = ''):
    """
summary: Hello Swagger
description: |
    Swagger 是一个规范和完整的框架，用于生成、描述、调用和可视化 RESTful 风格的 Web 服务。        
    总体目标是使客户端和文件系统作为服务器以同样的速度来更新。文件的方法，参数和模型紧密集成到服务器端的代码，允许API来始终保持同步。
    Swagger 让部署管理和使用功能强大的API从未如此简单。  按照 id 逆序排列
parameters:
  - name: start_latitude
    in: query;
    description: 几个参数
    required: true
    type: number
    format: double
  - name: start_longitude
    in: query
    description: 又一个参数
    required: true
    type: number
    format: double
  - name: end_latitude
    in: query
    description: 几个参数
    required: true
    type: number
    format: double
  - name: end_longitude
    in: query
    description: 又一个
    required: true
    type: number
    format: double
tags:
    - Estimates

responses:
    200:
        description: An array of price estimates by product
        schema:
            $ref: "#/definitions/StoreList"

============================== outputs

definitions:
  Store:
    type: object
    properties:
      id:
        type: "integer"
        description: 就是一个ID啦
      name:
        type: "string"
        description: 我也不知道是超市
      country_code:
        type: "string"
        description: 国家
      city:
        type: "string"
        description: 城市
  StoreList:
    type: array
    items: 
      $ref: "#/definitions/Store"
    """
    res = await hello()
    return tools.response(  {
                            "id": 0 ,
                            "city": "string" ,
                            "name": "string" ,
                            "country_code": "string" ,
                            }, code=0, message="发送成功", callback=callback)


@hug.get("/test")
async def test(callback: types.text = ''):
    '''
    '''
    return tools.response('test', code=0, message="发送成功", callback=callback)

@hug.get("/async_test")
async def async_test():
    return 'test'

@hug.get("/async_cache_test")
async def async_cache_test():
    res = await VerifyLib.async_cache_test()
    return res
