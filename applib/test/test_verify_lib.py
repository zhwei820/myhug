import asyncio
import unittest
import random
from test.test_tools import print_b
from applib.verify_lib import VerifyLib

loop = asyncio.get_event_loop()

def _test_add_code():
    return loop.run_until_complete(VerifyLib.add_code(15810538098, '12345678', 9876, 'com.test.com', '1.0.0.0', 'ios'))


class TestVerifyLib(unittest.TestCase):
    def test_get_code_by_pnum(self):
        self.assertEqual(int(VerifyLib.get_code_by_pnum(15810538098)), 9876)

    def test_add_code(self):
        self.assertNotEqual(_test_add_code(), False)
