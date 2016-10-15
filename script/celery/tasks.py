#!/usr/bin/env python

import sys
import os
import errno
import subprocess
from random import uniform

from celery import Celery
from celery.utils.log import get_task_logger
import celeryconfig

LOGGER = get_task_logger(__name__)
APP_NAME = 'tasks'

try:
    app = Celery(APP_NAME)
    app.config_from_object('celeryconfig', force=True)
except ImportError:
    # redis_url = os.getenv('REDIS_URL', 'redis://')
    print('celeryconfig not found, using %s' % redis_url)
    app = Celery(APP_NAME, broker=redis_url, )  # backend=redis_url

def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as e:
        if e.errno == errno.EEXIST:
            pass

@app.task(ignore_result=True)
def sum_test(num):
    num = num + 1
    do_request()
    return num

import httplib2
def do_request():
    http = httplib2.Http()
    headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/51.0.2704.79 Chrome/51.0.2704.79 Safari/537.36'}
    url = "https://www.baidu.com/"
    response, content = http.request(url, 'GET', headers=headers)


if __name__ == "__main__":
    r = main(sys.argv)
    print(r)
