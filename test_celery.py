from __future__ import absolute_import
from celery_proj.tasks.test_task import add_test

if __name__ == '__main__':
    for ii in range(1000):
        add_test.delay(1, 2)
