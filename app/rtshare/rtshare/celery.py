from datetime import timedelta
import os

from celery import Celery, shared_task  # noqa
from celery.schedules import crontab
from django.conf import settings


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rtshare.settings')


class Queue:
    default = 'default'
    processing = 'processing'
    management = 'management'
    alerts = 'alerts'

    all_queues = (
        default,
        processing,
        management,
        alerts,
    )

    limits = {
        default: 10,
        processing: 20,
        management: 10,
        alerts: 10,
    }


class Priority:
    eventually = 0
    low = 2
    default = 4
    high = 5
    immediate = 8
    priority_one = 10


app = Celery('rtshare')
app.config_from_object('django.conf:settings')
app.conf.task_default_queue = Queue.default
app.conf.task_queue_max_priority = Priority.priority_one
app.conf.task_default_priority = Priority.default


app.conf.beat_schedule = {

    # Occasionally each night, update any spaces that need to be updated.
    # 'autoupdate_spaces_that_need_it': {
    #     'task': 'spaces.tasks.autoupdate.autoupdate_spaces_that_need_it',
    #     'schedule': crontab(hour='0,3,20,22', minute=30),
    # },

    # Occasionally ping each device to see if it's still alive.
    'ping_all_devices': {
        'task': 'telescope.tasks.ping_all',
        'schedule': timedelta(minutes=10),
    },

    # Occasionally check to see if new observations require summarization.
    'summarize_completed_observations_if_needed': {
        'task': 'analysis.tasks.summarize_completed_observations_if_needed',
        'schedule': timedelta(minutes=5),
    },

}


app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)
