import pytest
import random
from _test.test_tools import print_b
from applib.message_lib import MessageLib

def test_get_msg_list():
    # print_b(MessageLib.get_msg_list(0, -1))
    assert isinstance(MessageLib.get_msg_list(0, -1), list)  # public msg

def test_get_msg_list_uid():
    # print_b(MessageLib.get_msg_list(0, 10000000))
    assert isinstance(MessageLib.get_msg_list(0, 10000000), list)  # private msg

    res = MessageLib.get_msg_list(0, 10000000)
    last_msg_id = res[len(res) - 1]['id']
    # print_b(MessageLib.get_msg_list(last_msg_id, 10000000))
    assert isinstance(MessageLib.get_msg_list(last_msg_id, 10000000), list)  # private msg
