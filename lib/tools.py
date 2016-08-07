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

    # 查询并缓存结果，需要传入数据库句柄
    def get_sql_cach(self, db_handle, sql, cache_time):
        r = Redis.get_instance()
        sql_key = "zhuansql_" + hashlib.md5(sql).hexdigest()
        cachers = r.get(sql_key)
        if not cachers:
            db_handle.Q(sql)
            rs_obj = db_handle.fetchall()
            if not rs_obj:
                rs_obj = []
            r.set(sql_key, json.dumps(rs_obj, cls=CJsonEncoder), cache_time)
            cachers = r.get(sql_key)
        rs_obj = json.loads(cachers)
        return rs_obj

    def get_password(self, password):
        return hashlib.md5(password + 'dianABCDEF12').hexdigest()

    def get_pnum(self, pnum):
        return hashlib.md5(str(pnum) + 'dianABCDE5').hexdigest()

    def check_cache(self, key, rdb_name=""):
        r = Redis.get_instance(rdb_name)
        rs = r.get(key)
        if rs:
            self.writeS(json.loads(rs))
            return True
        return False

    def set_cache_obj(self, key, obj, ex, rdb_name=""):
        self.set_cache(key, json.dumps(obj, cls=CJsonEncoder), ex, rdb_name)

    def get_obj_cache(self, key, rdb_name=""):
        string = self.get_cache(key, rdb_name)
        if string:
            return json.loads(string.decode())
        return None

    def set_cache(self, key, val, ex, rdb_name=""):
        r = Redis.get_instance(rdb_name)
        r.set(key, val, ex)
        return True

    def get_cache(self, key, rdb_name=""):
        r = Redis.get_instance(rdb_name)
        rs = r.get(key)
        return rs

    def del_cache(self, key, rdb_name=''):
        r = Redis.get_instance(rdb_name)
        return r.delete(key)

    def temp_cache_key(self, key):
        return "_ZHUAN_%s%s" % (self.__class__.__name__, key)


    def get_counting(self, key, interval, default_cooltime=1, onmonth=0, db=''):
        today = str(datetime.date.today()) if not onmonth else str(datetime.date.today())[:7]
        r_cool_key = key + "_" + today
        r = Redis.get_instance(db)
        rcooltime = r.incr(r_cool_key)
        if rcooltime == 1:
            r.expire(r_cool_key, interval)
        if default_cooltime != 1:
            if rcooltime > default_cooltime:
                return True
        elif rcooltime != 1:
            return True
        return False

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

    def get_sys_config(self):
        r = Redis.get_instance()
        sys_conf = r.get(Redis._ZHUAN_SYS_CONF_)
        conf = {}
        if not sys_conf:
            m = mmysql()
            m.Q("select sys_key,sys_value from o_sys_conf")
            rs = m.fetchall()
            m.close()
            if rs:
                for i in rs:
                    conf[i[0]] = i[1]
                r.set(Redis._ZHUAN_SYS_CONF_, json.dumps(conf), 600)
        else:
            conf = json.loads(sys_conf)
        return conf


    def cache_get_hash_all_obj(self, name, host_name=''):
        u'''获取名为 ``name`` 的hash 的键和值，以dict格式返回
        支持值为非字符串对象
        '''
        ret = {}
        r = Redis.get_instance(host_name)
        d = r.hgetall(name)
        for _k, _v in d.iteritems():
            try:
                _tmp = _v.replace("'", '"')
                _obj = json.loads(_tmp)
                ret[_k] = _obj
            except:
                info('%s %s', _k, pcformat(_v), exc_info=True)
#-#                error('', exc_info=True)
                ret[_k] = _v

        return ret

    def cache_get_hash_obj_value(self, name, key, host_name=''):
        u'''获取名为 ``name`` 的hash中key为 ``key`` 的值
        支持值为非字符串对象
        '''
        r = Redis.get_instance(host_name)
        s = r.hget(name, key)
        if s:
            try:
                _tmp = s.replace("'", '"')
                s = json.loads(_tmp)
            except:
                error('', exc_info=True)
                pass
        return s

    def cache_set_hash_obj_value(self, name, key, value, ex=None, host_name=''):
        u'''设置名为 ``name`` 的hash中key为 ``key`` 的值为 ``value``
        支持值为非字符串对象
        '''
        r = Redis.get_instance(host_name)
        s = value
        if s:
            try:
                _tmp = json.dumps(s, cls=CJsonEncoder)
                s = _tmp
            except:
                error('', exc_info=True)
                pass
        ret = r.hset(name, key, s)
        if ex:
            r.expire(name, ex)
        return ret

    def cache_set_hash_all_obj(self, name, dict_obj, ex=None, host_name=''):
        u'''设置名为 ``name`` 的hash 的键和值为 ``dict_obj`` 中的键和值
        支持值为非字符串对象
        '''
        r = Redis.get_instance(host_name)
        _obj = {}
        for _k, _v in dict_obj.iteritems():
            try:
                _tmp = json.dumps(_v, cls=CJsonEncoder)
            except:
                _tmp = _v
            _obj[_k] = _tmp
        ret = r.hmset(name, _obj)
        if ex:
            r.expire(name, ex)
        return ret

tools = Tools()

if __name__ == '__main__':
    s = Tools()
