from dataclasses import dataclass
import logging
import json
import time

import httpx

from . import api, db, settings
from .lights import Status, managed_status


logger = logging.getLogger('astronomer')

last_event_id = None
connection = None


def ping(_):
    api.health_check()


def configure(*args):
    configuration = api.get_configuration()
    with connection as cursor:
        db.truncate_tables(cursor)
        db.insert_telescope(configuration, cursor)
        for task in configuration['tasks']:
            db.insert_task(task, cursor)


def add_task(data):
    with connection as cursor:
        db.insert_task(data['task'], cursor)


def update_task(data):
    with connection as cursor:
        db.update_task(data['task'], cursor)


def delete_task(data):
    with connection.cursor() as cursor:
        db.delete_task(data['task'], cursor)


@dataclass
class Event:
    event: str = None
    id: str = None
    data: str = ''

    class Type:
        PING = 'ping'
        CONFIGURE = 'configure'
        ADD_TASK = 'add-task'
        UPDATE_TASK = 'update-task'
        DELETE_TASK = 'delete-task'

        action = {
            PING: ping,
            CONFIGURE: configure,
            ADD_TASK: add_task,
            UPDATE_TASK: update_task,
            DELETE_TASK: delete_task,
        }

    @property
    def is_message(self):
        return self.event and self.event.lower() == 'message'

    @property
    def json(self):
        return json.loads(self.data)


def dispatch(event):
    logger.info(f'Event detected: type={event.event}, id={event.id}')
    if not event.is_message:
        return

    if action := Event.Type.action.get(event.json['type']):
        try:
            action(event.json)
        except Exception as e:
            logger.error(f'Encountered error during event handling: {e}.')


def process_event(chunk):
    try:
        return Event(**dict(chunk))
    except Exception:
        return None


def stream_data(stream, light):
    global last_event_id

    chunk = []
    for line in stream.iter_lines():
        if line == '':
            if event := process_event(chunk):
                # TODO: Move this and persist it.
                if (id := event.id) and (event.id != 'error'):
                    last_event_id = id

                light.flash_fast(end_state=True)
                dispatch(event)
        elif line[0] == ':':
            # Comment line. Just ignore it.
            continue
        elif ':' in line:
            fields = line.split(':', 1)
            key = fields[0]
            value = fields[1].lstrip(' ')
            chunk.append([key, value])
        else:
            chunk.append([line, ''])


def connect(light):
    logger.info('Configuring...')
    configure()

    logger.info('Streaming data...')
    headers = {
        'Authorization': f'Device {settings.HOME_AUTHORIZATION_TOKEN}',
    }
    if last_event_id:
        headers['Last-Event-ID'] = last_event_id

    with httpx.stream(
        'GET',
        settings.DOWNLINK_EVENT_STREAM_URL,
        follow_redirects=True,
        timeout=settings.DOWNLINK_EVENT_STREAM_TIMEOUT,
        headers=headers,
    ) as r:
        light.on()
        stream_data(r, light)


def downlink():
    global connection
    connection = db.setup_and_connect()

    logger.info('Beginning downlink from host...')

    while True:
        with managed_status(Status.downlink, initial_state=False) as light:
            try:
                connect(light)
            except Exception as e:
                light.flash_error()
                logger.error(f'Downlink error: {e}.', exc_info=True)
            else:
                logger.info('Unable to connect to stream. Retrying...')
            finally:
                light.off()

        time.sleep(settings.DOWNLINK_RECONNECT_SECONDS)
        logger.warning('Attempting reconnect...')

    logger.info('Done.')
