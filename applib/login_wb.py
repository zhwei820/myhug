#coding=utf8

if __name__ == '__main__':
    import sys
    import os
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))
import json
from tornado import gen
from tornado.httpclient import AsyncHTTPClient
#-#from tornado.httpclient import HTTPRequest
#-#from tornado.httputil import HTTPHeaders
from lib.applog import app_log
info, debug, error = app_log.info, app_log.debug, app_log.error


class WBLogin(object):
    @staticmethod
    @gen.coroutine
    def getOAuthUserInfo(access_token, uid):
        u'''获取微博用户基本信息

        http://open.weibo.com/wiki/%E6%8E%88%E6%9D%83%E6%9C%BA%E5%88%B6
        http://open.weibo.com/wiki/%E5%BE%AE%E5%8D%9AAPI#.E7.94.A8.E6.88.B7
        http://open.weibo.com/wiki/2/users/show
        '''
        j_data = {'ret': -1, 'msg': '登录失败，请稍后再试'}
        url = 'https://api.weibo.com/2/users/show.json?uid={UID}&access_token={ACCESS_TOKEN}'.format(ACCESS_TOKEN=access_token, UID=uid)
        try:
            httpc_lient = AsyncHTTPClient()
            resp = yield gen.Task(httpc_lient.fetch, url)  # , validate_cert=False)
            info('resp: %s', resp.body)
            j_data = json.loads(resp.body)
        except:
            error('获取微博用户基本信息失败 access_token %s uid %s', access_token, uid, exc_info=True)

        raise gen.Return((j_data, j_data.get('error_code', ''), j_data.get('error', '')))
