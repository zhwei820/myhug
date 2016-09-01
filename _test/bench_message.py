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
from lib.auth import get_new_ticket


def long_time_task(name):
    ticket = get_new_ticket(10000000, 15310982387, 'mb')
    print('Run task %s (%s)...' % (ticket.decode(), os.getpid()))
    loop = asyncio.get_event_loop()
    headers = {'AUTHORIZATION': ticket.decode()}
    for x in range(0, 1000):
        print(loop.run_until_complete(fetch('http://localhost:8000/msg_list.do?last_msg_id=-1&os_type=ios&app_version=1.1.0.0&uid=10000000&channel=share&package_name=com.test.package', headers = headers)))

if __name__=='__main__':
    print('Parent process %s.' % os.getpid())
    p = Pool(10)
    for i in range(10):
        p.apply_async(long_time_task, args=(i,))
    print('Waiting for all subprocesses done...')
    p.close()
    p.join()
    print('All subprocesses done.')