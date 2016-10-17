from __future__ import absolute_import
from celery_proj.celery import app
from celery.utils.log import get_task_logger

logger = get_task_logger(__name__)

@app.task(ignore_result=True)
def output_log(*args,**kwargs):
    logger.info(*args,**kwargs)
