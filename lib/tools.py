# coding=utf-8

import os
import sys
if __name__ == '__main__':
    import os
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))

import asyncio
import aiohttp

import json
import traceback
import hashlib
import datetime
import sys
import os
from lib.mysql_manager import Mysql
from lib.json_encoder import CJsonEncoder
from lib.redis_cache import cache

class Tools(object):
    def __init__(self):
        self._mysql_conn_arr = {}
        self._service_conn = None

    def mysql_conn(self, db_name=""):
        _conn = self._mysql_conn_arr.get(db_name)
        if not _conn:
            _conn = Mysql(db_name)
            self._mysql_conn_arr[db_name] = _conn
        return _conn

    def temp_cache_key(self, key):
        return "_ZHUAN_%s%s" % (self.__class__.__name__, key)

    def get_counting(self, key, interval, host_name=''):
        r = cache
        r_key = self.temp_cache_key(key)
        rs = r.get(r_key)
        if rs:
            return False
        else:
            rs = r.set(r_key, 1, interval)
            return True

    def del_counting(self, key, host_name=''):
        r = cache
        r_key = self.temp_cache_key(key)
        r.delete(r_key)

    def response(self, rs = None, code = 0, message = '', callback=''):
        rsp = {"code": code, "message": message}
        if not rs:
            return rsp
        if isinstance(rs, dict):
            rsp.update(rs)
        else:
            rsp['data'] = rs
        if not callback:
            return rsp
        else:
            return callback + '(' + json.dumps(rsp) + ')'

    def get_real_ip(self, request):
        peername = request.transport.get_extra_info('peername')
        if peername is not None:
            host, port = peername
            return host

tools = Tools()

async def fetch(url, headers = None):
    try:
        with aiohttp.ClientSession(headers=headers) as client:
            async with client.get(url) as resp:
                res = await resp.text()
                return res
    except Exception as e:
        return None

async def http_post(url, data=None):
    try:
        with aiohttp.ClientSession() as client:
            async with client.post(url, data=data) as resp:
                return await resp.text()
    except Exception as e:
        return None

async def http_put(url, data=None):
    try:
        with aiohttp.ClientSession() as client:
            async with client.put(url, data=data) as resp:
                return await resp.text()
    except Exception as e:
        return None


if __name__ == '__main__':
    s = Tools()
    loop = asyncio.get_event_loop()
    print(loop.run_until_complete(fetch('http://atanx.alicdn.com/t/tanxssp.js?_v=12')))
    print(loop.run_until_complete(http_post('http://atanx.alicdn.com/t/tanxssp.js?_v=12')))
    print(loop.run_until_complete(http_put('http://atanx.alicdn.com/t/tanxssp.js?_v=12')))
