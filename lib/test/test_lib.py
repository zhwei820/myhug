import pytest
import random
from lib.logger import info, error
from lib.auth import get_new_ticket

def test_get_new_ticket():
    print(get_new_ticket(10000000, '15810538098'))
    # assert False
