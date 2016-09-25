#!/usr/bin/env python
# coding=utf-8
import settings
import hug
import time
from endpoint import part_1, login, version, sms_verify, user
from endpoint.my import msg_list

@hug.extend_api("/api")
def with_other_apis():
    return [part_1, login, version, msg_list, sms_verify, user]

if not settings.DEBUG:
    @hug.not_found()
    def not_found():
        return {'Nothing': 'to see'}

if __name__ == '__main__':
    __hug__.serve()  # noqa
# api = hug.API(__name__)
# app = api.http.server()
