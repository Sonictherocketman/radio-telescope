import time

import httpx

from .. import settings
from ..models.lights import StatusLight
from ..mpsafe import managed_status
from ..utils import api


# def configure(*args):
#     configuration = api.get_configuration()
#     with connection as cursor:
#         db.truncate_tables(cursor)
#         db.insert_telescope(configuration, cursor)
#         for task in configuration['tasks']:
#             db.insert_task(task, cursor)
#
#
# def add_task(data):
#     with connection as cursor:
#         db.insert_task(data['task'], cursor)
#
#
# def update_task(data):
#     with connection as cursor:
#         db.update_task(data['task'], cursor)
#
#
# def delete_task(data):
#     with connection.cursor() as cursor:
#         db.delete_task(data['task'], cursor)


def check_config():
    # TODO: Add config check here. For now we just ping.
    api.health_check()


def downlink(log, event_queue):
#     global connection
#     connection = db.setup_and_connect()

    log.put(('info', 'Beginning downlink from host...'))

    while True:
        with managed_status(event_queue, StatusLight.downlink) as light:
            log.put(('info', 'Checking remote configuration...'))
            try:
                check_config()
            except Exception as e:
                light('flash_error')
                log.put(('error', f'Downlink error: {e}.'))

        time.sleep(settings.Wait.background)
