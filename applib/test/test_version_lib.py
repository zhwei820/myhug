
import unittest
import random
from test.test_tools import print_b
from applib.version_lib import VersionLib

class TestVersionLib(unittest.TestCase):
    def test_get_version(self):
        # print_b(VersionLib.get_version('ios', '1.0.0.0', '00'))
        self.assertEqual(VersionLib.get_version('ios', '1.0.0.0', '00')['os_type'], 'ios')
        # self.assertEqual(VersionLib.get_version('ios', '1.0.0.0', '00')['os_type'], 'ios')
        self.assertIsNone(VersionLib.get_version('ios', '9.0.0.0', '00'))


    def test_get_version_value(self):
        self.assertEqual(VersionLib.get_version_value('1.0.0.1'), [1, 0, 0, 1])
        self.assertEqual(VersionLib.get_version_value('10.0.0.1'), [10, 0, 0, 1])
        self.assertEqual(VersionLib.get_version_value('10.0.0'), [10, 0, 0, 0])
        self.assertEqual(VersionLib.get_version_value('22.99'), [22, 99, 0, 0])

    def test_version_compare(self):
        self.assertEqual(VersionLib.version_compare('1.0.0.1', '1.0.0.1'), 0)
        self.assertEqual(VersionLib.version_compare('10.0.0.1', '1.0.0.1'), 1)
        self.assertEqual(VersionLib.version_compare('9.0.0', '10.0.0.1'), -1)
        self.assertEqual(VersionLib.version_compare('22.99', '10.0.0.1'), 1)
