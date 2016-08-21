#!/usr/bin/env python
# coding=utf-8

import hug
import time
import asyncio
from gevent import monkey
from decouple import config

from endpoint import part_1, login, version
from endpoint.my import msg_list

@hug.extend_api()
def with_other_apis():
    return [part_1, login, version, msg_list]

DEBUG = config('DEBUG')

if not DEBUG:
    @hug.not_found()
    def not_found():
        return {'Nothing': 'to see'}

if __name__ == '__main__':
    monkey.patch_thread()
    __hug__.serve()  # noqa
