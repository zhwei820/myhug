import pytest
import random
from lib.logger import info, error
from lib.auth import get_new_ticket, check_ticket

def test_get_new_ticket():
    print(get_new_ticket(10000000, '15810538098'))
    # assert False

def test_check_ticket():
    print(check_ticket('eyJ1aWQiOjEwMDAwMDAwLCJxaWQiOiIxNTgxMDUzODA5OCJ9.Cq1XzA.Gd5OK8NppLtTz62f9qP9Ii21PNk'))
    # assert False
