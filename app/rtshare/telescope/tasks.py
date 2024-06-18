import logging

from celery import group
from django_eventstream import send_event


from rtshare.celery import shared_task, Queue, Priority
from .models import Telescope


logger = logging.getLogger(__name__)


@shared_task(queue=Queue.default, priority=Priority.default)
def ping(telescope_id):
    logger.info('Attempting to ping ')
    send_event(telescope_id, 'message', {'type': 'ping'})


@shared_task(queue=Queue.default, priority=Priority.default)
def ping_all():
    qs = Telescope.objects.filter(status=Telescope.Status.ACTIVE)
    workflow = group([
        ping.si(telescope.public_id)
        for telescope in qs
    ])
    workflow.delay()
