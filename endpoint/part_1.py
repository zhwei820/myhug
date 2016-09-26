import hug
import datetime, asyncio
from hug import types
from lib.tools import tools
from applib.verify_lib import VerifyLib

async def hello():
    await asyncio.sleep(10)
    return "haha"

@hug.get("/hello")
async def hello_world():
    res = await hello()
    return res

@hug.get("/test")
async def test(callback: types.text = ''):
    '''api test: doc test \r\n, test multiple line;
    '''
    return tools.response('test', code=0, message="发送成功", callback=callback)

@hug.get("/async_test")
async def async_test():
    return 'test'

@hug.get("/async_cache_test")
async def async_cache_test():
    res = await VerifyLib.async_cache_test()
    return res
