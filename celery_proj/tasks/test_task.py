from __future__ import absolute_import

from celery_proj.celery import app
import time


@app.task
def add_test(x, y):
    do_request()
    return x + y


@app.task
def mul(x, y):
    return x * y


@app.task
def xsum(numbers):
    return sum(numbers)

import httplib2
def do_request():
    http = httplib2.Http()
    headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/51.0.2704.79 Chrome/51.0.2704.79 Safari/537.36'}
    url = "https://www.baidu.com/"
    response, content = http.request(url, 'GET', headers=headers)
