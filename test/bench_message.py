import asyncio
import random
from multiprocessing import Pool
import os, time
if __name__ == '__main__':
    import os
    import sys
    par_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir))
    sys.path.append(par_dir)

from lib.tools import fetch


def long_time_task(name):
    print('Run task %s (%s)...' % (name, os.getpid()))
    loop = asyncio.get_event_loop()
    headers = {'Authorization': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1aWQiOjEwMDYwOTEwLCJtb2JpbGUiOiIxNTgxMDUxMjEwNTEifQ.UihvxbnNutCpSZU0R0QynxPmkLRDV331F37hQAD9LCw'}
    for x in range(0, 1):
        print(loop.run_until_complete(fetch('http://localhost:8000/msg_list.do?last_msg_id=-1&os_type=ios&app_version=1.1.0.0&uid=0&channel=share&package_name=com.test.package', headers = headers)))
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
