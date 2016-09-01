import asyncio
import unittest
import random
from applib.user_lib import UserLib

loop = asyncio.get_event_loop()

def _test_add_user():
    return loop.run_until_complete(UserLib.add_user({
                                                    'reg_qid': int('135' + str(random.randint(10000000, 99999999))),
                                                    'token': 'access_token',
                                                    'reg_source': 'mb',
                                                    'invite_uid': '10000000',
                                                    'reg_ip': '127.0.0.1',
                                                    'os_type': 'ios',
                                                    'app_version': '1.0.0.0',
                                                    'channel': 'test',
                                                    'package_name': 'com.test.com',
                                                    'nickname': 'nickname',
                                                    'gender': 'M',
                                                    'figure_url': 'http://img.zcool.cn/community/0122e655f8f3e06ac7251df8686c5f.png',
                                                    'figure_url_other': 'http://img.zcool.cn/community/0122e655f8f3e06ac7251df8686c5f.png',
                                                    'province': 'province',
                                                    'city': 'city',
                                                    'country': 'country',
                                                    'year': 1988,
                                                    }))

class TestUserLib(unittest.TestCase):
    def test_add_user(self):
        self.assertEqual(_test_add_user()['code'], 0)

    def test_get_user_by_uid(self):
        self.assertEqual(UserLib.get_user_info_by_uid(10000000)['uid'], 10000000)
        self.assertIsNone(UserLib.get_user_info_by_uid(90000000))
