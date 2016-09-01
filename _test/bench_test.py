import asyncio
import random
from multiprocessing import Pool
import os, time
import urllib.parse
import httplib2

if __name__ == '__main__':
    import os
    import sys
    par_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir))
    sys.path.append(par_dir)

from lib.tools import fetch


def do_request():
    http = httplib2.Http()
    headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/51.0.2704.79 Chrome/51.0.2704.79 Safari/537.36'}
    url = 'http://b-myhug.com/api/add_code.do?os_type=ios&app_version=1.1.0.0&channel=share&package_name=com.test.package&pnum=1862753079&device_id=llllllfffff&a=%s'
    response, content = http.request(url, 'GET', headers=headers)

def long_time_task(name):
    process_id = os.getpid()
    print('Run task %s (%s)...' % (name, process_id))
    loop = asyncio.get_event_loop()
    for x in range(0, 100):
        # do_request()
        headers = {'Content-type': 'text/html'}
        loop.run_until_complete(fetch('http://b-myhug.com/api/async_cache_test', headers))
        # loop.run_until_complete(fetch('http://localhost:9876/sport_score.do?sport_id=10', headers))
        # loop.run_until_complete(fetch('http://b-myhug.com/api/dateadd?value=2014-12-22T03:12:58&addend=63', headers))
        # loop.run_until_complete(fetch('http://b-myhug.com/api/test', headers))
        # loop.run_until_complete(fetch('http://b-myhug.com/api/async_test', headers))
        # loop.run_until_complete(fetch('http://b-myhug.com/api/add_code.do?os_type=ios&app_version=1.1.0.0&channel=share&package_name=com.test.package&pnum=1862753079&device_id=llllllfffff&a=%s' % process_id, headers))
        # loop.run_until_complete(fetch('http://b-myhug.com/api/async_add_code.do?os_type=ios&app_version=1.1.0.0&channel=share&package_name=com.test.package&pnum=1862753079&device_id=llllllfffff&a=%s' % process_id, headers))
    print('Run task end %s (%s) ' % (name, os.getpid()))

if __name__=='__main__':
    print('Parent process %s.' % os.getpid())
    import time;start_CPU = time.time()
    p = Pool(50)
    for i in range(100):
        p.apply_async(long_time_task, args=(i,))
    p.close()
    p.join()
    end_CPU = time.time(); print("all Task takes %s seconds" % (end_CPU - start_CPU))
