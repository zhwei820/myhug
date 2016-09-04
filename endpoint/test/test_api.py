import pytest
import hug

from server import api

def test_api():
    assert hug.test.get(api, 'api/test').data['result'] == 'result'
