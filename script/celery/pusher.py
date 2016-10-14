from celery import Celery
# from celery.utils.log import get_task_logger
app = Celery('pusher', broker='redis://192.168.199.224:6379/0')

@app.task()
def sum_test(self, num):
    try:
        # f = open('plog','a')
        # f.write('retry\n')
        # f.close()
        num = num + 1
        return num
    except Exception as exc:
        raise self.retry(exc=exc, countdown=60)
