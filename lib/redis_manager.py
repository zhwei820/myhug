# -*- coding: UTF-8 -*-
'''
redis链接管理
'''
import redis
from decouple import config
import dj_database_url

dbConf = dj_database_url.config(default= config('REDIS_URL', default='redis://:spwx@localhost:6379/1'))
_REDIS = redis.Redis(host = dbConf['HOST'],
                     port = dbConf['PORT'],
                     db = dbConf['NAME'])

_REDIS_HOST_LIST = {}

class Redis(object):
    @staticmethod
    def reconn(host_name=''):
        if not host_name:
            _REDIS = redis.Redis(host = dbConf['HOST'],
                                 port = dbConf['PORT'],
                                 db = dbConf['NAME'])
        elif not _REDIS_HOST_LIST.get(host_name):
                dbConf = dj_database_url.config(default= config(host_name.upper() + '_REDIS_URL', default='redis://:spwx@localhost:6379/1'))
                _REDIS_HOST_LIST[host_name] = redis.Redis(host = dbConf['HOST'],
                                                 port = dbConf['PORT'],
                                                 db = dbConf['NAME'])

    @staticmethod
    def get_instance(host_name=''):
        if not host_name:
            return _REDIS
        else:
                dbConf = dj_database_url.config(default= config(host_name.upper() + '_REDIS_URL', default='redis://:spwx@localhost:6379/1'))
                _REDIS_HOST_LIST[host_name] = redis.Redis(host = dbConf['HOST'],
                                                 port = dbConf['PORT'],
                                                 db = dbConf['NAME'])

_CHANNEL_INFO_LIST_ = "CHANNEL_INFO_LIST"  # 渠道列表
_CHANNEL_INFO_ = "CHANNEL_INFO"  # 单个渠道列表
_APP_VERSION_ = "_APP_VERSION_"  # 版本升级 最新版本
