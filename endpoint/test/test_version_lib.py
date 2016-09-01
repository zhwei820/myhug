
import pytest
import hug

from endpoint.part_1 import test


def test_per_api_directives():
    """Test to ensure it's easy to define a directive within an API"""

    print(dir(hug.test.get(test, 'test')))
    assert False
