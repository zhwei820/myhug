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
summary: Create user
description: This can only be done by the logged in user.
operationId: examples.api.api.createUser
produces:
  - application/json
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
responses:
    "201":
        description: An array of price estimates by product
        schema:
            type: array
            items:
                $ref: "#/definitions/Store"


==============================

definitions:
  Store:
    type: object
    required:
      - id
      - name
      - country_code 
      - city
    properties:
      id:
        type: "integer"
        readOnly: true
        description: Store ID
      name:
        type: "string"
        description: Store name
      country_code:
        type: "string"
        description: 3-letter country code (e.g. USA)
      city:
        type: "string"
        description: "City where the store is located"
  StoreList:
    type: array
    items: 
      $ref: "#/definitions/Store"

    """
    return "pong"

async def hello():
    await asyncio.sleep(0.1)
    return "haha"

@hug.get("/hello")
async def hello_world():
    """
summary: Price Estimates
description: |
    Swagger 是一个规范和完整的框架，用于生成、描述、调用和可视化 RESTful 风格的 Web 服务。        
    总体目标是使客户端和文件系统作为服务器以同样的速度来更新。文件的方法，参数和模型紧密集成到服务器端的代码，允许API来始终保持同步。
    Swagger 让部署管理和使用功能强大的API从未如此简单。
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
            type: array
            items:
                $ref: "#/definitions/Store"

        default:
            description: Unexpected error
            schema:
                $ref: '#/definitions/Error'

==============================

definitions:
  Store:
    type: object
    required:
      - id
      - name
      - country_code 
      - city
    properties:
      id:
        type: "integer"
        readOnly: true
        description: Store ID
      name:
        type: "string"
        description: Store name
      country_code:
        type: "string"
        description: 3-letter country code (e.g. USA)
      city:
        type: "string"
        description: "City where the store is located"
  StoreList:
    type: array
    items: 
      $ref: "#/definitions/Store"

    """
    res = await hello()
    return res

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
