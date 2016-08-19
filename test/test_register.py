import asyncio
import random
from multiprocessing import Pool
import os, time
if __name__ == '__main__':
    import os
    import sys
    par_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir))
    sys.path.append(par_dir)

from lib.tools import http_post


def long_time_task(name):
    print('Run task %s (%s)...' % (name, os.getpid()))
    loop = asyncio.get_event_loop()
    for x in range(0, 1000):
        print(loop.run_until_complete(http_post('http://localhost:8000/login?openid=158105%s&os_type=ios&app_version=1.1.0.0&rs=mb&access_token=10000dkjdksjfkds&channel=share&package_name=com.test.package&invite_uid=10000000&gender=m' % random.randint(100000, 999999))))
    print('Task %s runs %0.2f seconds.' % (name, (end - start)))

if __name__=='__main__':
    print('Parent process %s.' % os.getpid())
    p = Pool(10)
    for i in range(5):
        p.apply_async(long_time_task, args=(i,))
    print('Waiting for all subprocesses done...')
    p.close()
    p.join()
    print('All subprocesses done.')
