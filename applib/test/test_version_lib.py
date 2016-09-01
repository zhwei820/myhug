
import random
from _test.test_tools import print_b
from applib.version_lib import VersionLib

def test_get_version():
    # print_b(VersionLib.get_version('ios', '1.0.0.0', '00'))
    assert VersionLib.get_version('ios', '1.0.0.0', '00')['os_type'] == 'ios'
    # assert VersionLib.get_version('ios', '1.0.0.0', '00')['os_type'], 'ios')
    assert not VersionLib.get_version('ios', '9.0.0.0', '00')


def test_get_version_value():
    assert VersionLib.get_version_value('1.0.0.1') == [1, 0, 0, 1]
    assert VersionLib.get_version_value('10.0.0.1') == [10, 0, 0, 1]
    assert VersionLib.get_version_value('10.0.0') == [10, 0, 0, 0]
    assert VersionLib.get_version_value('22.99') == [22, 99, 0, 0]

def test_version_compare():
    assert VersionLib.version_compare('1.0.0.1', '1.0.0.1') == 0
    assert VersionLib.version_compare('10.0.0.1', '1.0.0.1') == 1
    assert VersionLib.version_compare('9.0.0', '10.0.0.1') == -1
    assert VersionLib.version_compare('22.99', '10.0.0.1') == 1
