import hug
import datetime, asyncio
from hug import types
from lib.tools import tools
from applib.verify_lib import VerifyLib

@hug.get("/ping")
async def ping(request):
    """
    Description end-point

    ---
    tags:
    -   user
    summary: Create user
    description: This can only be done by the logged in user.
    operationId: examples.api.api.createUser
    produces:
    -   application/json
    parameters:
    -   in: body
        name: body
        description: Created user object
        required: false
        schema:
        type: object
        properties:
            id:
            type: integer
            format: int64
            username:
            type:
                - "string"
                - "null"
            firstName:
            type: string
            lastName:
            type: string
            email:
            type: string
            password:
            type: string
            phone:
            type: string
            userStatus:
            type: integer
            format: int32
            description: User Status
    responses:
    "201":
        description: successful operation
    """
    return "pong"

async def hello():
    await asyncio.sleep(10)
    return "haha"

@hug.get("/hello")
async def hello_world():
    """
    Description end-point

    ---
    tags:
    -   hello
    summary: Create user
    description: This can only be done by the logged in user.
    operationId: examples.api.api.createUser
    produces:
    -   application/json
    parameters:
    -   in: body
        name: body
        description: Created user object
        required: false
        schema:
        type: object
        properties:
            id:
            type: integer
            format: int64
            username:
            type:
                - "string"
                - "null"
            firstName:
            type: string
            lastName:
            type: string
            email:
            type: string
            password:
            type: string
            phone:
            type: string
            userStatus:
            type: integer
            format: int32
            description: User Status
    responses:
    "201":
        description: successful operation
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
