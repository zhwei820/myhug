import hug
import datetime, asyncio
from hug import types
from marshmallow import fields
from marshmallow.validate import Range, OneOf
from applib.verify_lib import VerifyLib

async def hello():
    asyncio.sleep(0.1)
    return "haha"

@hug.get("/hello")
async def hello_world():
    res = await hello()
    return "Hello"

@hug.get("/test")
def test():
    return 'test'

@hug.get("/async_test")
async def async_test():
    return 'test'

@hug.get("/async_cache_test")
async def async_cache_test():
    res = await VerifyLib.async_cache_test()
    return res

@hug.get('/dateadd', examples="value=2014-12-22T03:12:58&addend=63")
async def dateadd(value: fields.DateTime(),
            addend: fields.Int(validate=Range(min=1)),
            unit: fields.Str(validate=OneOf(['minutes', 'days']))='days',
            ii: fields.Integer() = 1):
    '''获取时间相加的数值

    '''
    value = value or dt.datetime.utcnow()
    if unit == 'minutes':
        delta = datetime.timedelta(minutes=addend)
    else:
        delta = datetime.timedelta(days=addend)
    result = value + delta
    return {'result': result}
