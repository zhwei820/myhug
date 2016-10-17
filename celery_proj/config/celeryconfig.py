BROKER_URL = 'redis://192.168.199.224:6379/0'
CELERY_RESULT_BACKEND = BROKER_URL

CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_ACCEPT_CONTENT=['json']
CELERY_IMPORTS = (
                    'celery_proj.tasks.os_task',
                    'celery_proj.tasks.test_task',
                    # 'celery_proj.tasks.get_cursos',
                    'celery_proj.tasks.periodic_courses'
                )


# CELERY_ANNOTATIONS = {
#     'tasks.add': {'rate_limit': '10/m'}
# }
