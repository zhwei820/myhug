#!/usr/bin/env python
# coding=utf-8

import multiprocessing

bind = '127.0.0.1:8701'
max_requests = 10000
keepalive = 5

proc_name = 'my_hug'

workers = 5
# worker_class = 'gaiohttp'

loglevel = 'debug'

x_forwarded_for_header = 'X-FORWARDED-FOR'

errorlog = '/data/logs/myhug_error.log'
accesslog = '/data/logs/myhug_access.log'
