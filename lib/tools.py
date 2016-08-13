# coding=utf-8

import os
import sys
if __name__ == '__main__':
    import os
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))

import json
import traceback
import hashlib
import datetime
import sys
import os
from lib.redisManager import Redis
from lib.mysqlManager import Mysql
from lib.jsonEncoder import CJsonEncoder

class Tools(object):
    def __init__(self):
        self._mysql_conn_arr = {}
        self._service_conn = None

    def get_redis(self, host_name=''):
        return Redis.get_instance(host_name)

    def mysql_conn(self, db_name=""):
        _conn = self._mysql_conn_arr.get(db_name)
        if not _conn:
            _conn = Mysql(db_name)
            self._mysql_conn_arr[db_name] = _conn
        return _conn

    def get_password(self, password):
        return hashlib.md5(password + 'dianABCDEF12').hexdigest()


    #计数器功能升级版
    def get_counting_super(self, key, interval, default_cooltime=1, onmonth=0, db=''):
        keystr = self.temp_cache_key(key)
        return self.get_counting(keystr, interval, default_cooltime, onmonth, db)

    def del_counting(self, key, onmonth=0, db=''):
        u'''删除 ``get_counting(...)``` 创建的计数器
        '''
        today = str(datetime.date.today()) if not onmonth else str(datetime.date.today())[:7]
        r_cool_key = key + "_" + today
        r = Redis.get_instance(db)
        r.delete(r_cool_key)

tools = Tools()

if __name__ == '__main__':
    s = Tools()
