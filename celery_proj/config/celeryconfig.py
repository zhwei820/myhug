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

CELERYD_MAX_TASKS_PER_CHILD = 100

CELERY_ANNOTATIONS = {
    'celery_proj.tasks.add': {'rate_limit': '10/m'}
}




from kombu import Queue, Exchange

CELERY_DEFAULT_QUEUE = "push"
CELERY_DEFAULT_EXCHANGE = "push"
CELERY_DEFAULT_ROUTING_KEY = "push"

CELERY_QUEUES = (
    # Queue("auto_push", routing_key="auto_push")
    Queue("test_task", Exchange("test_task"), routing_key="test_task"),
    Queue("push", routing_key="push")
)


CELERY_ROUTES = {
    "celery_proj.tasks.test_task.add_test": {
        "queue": "test_task",
        "routing_key": "test_task",
    },
    "celery_proj.tasks.test_task.mul": {
        "queue": "test_task",
        "routing_key": "test_task",
    },
}

# CELERY_ROUTES = {
#     "device_push.tasks.auto_device_push": {
#         "queue": "push",
#         "routing_key": "push",
#     },
#     "device_push.tasks.handle_expired_tokens": {
#         "queue": "push",
#         "routing_key": "push",
#     },
#     "device_push.tasks.send_custom_push": {
#         "queue": "push",
#         "routing_key": "push",
#     },
#     "device_push.tasks.send_custom_msg_push": {
#         "queue": "push",
#         "routing_key": "push",
#     },
#     "device_push.tasks.send_request_push": {
#         "queue": "single_push",
#         "exchange": "single_push",
#         "routing_key": "single_push",
#     },
#     "device_push.tasks.send_single_message": {
#         "queue": "single_push",
#         "exchange": "single_push",
#         "routing_key": "single_push",
#     }
# }
