from datetime import datetime
from multiprocessing import get_logger
import os
import json
import time

import httpx

from .. import settings
from ..models.lights import StatusLight
from ..mpsafe import managed_status
from ..utils import api


logger = get_logger()


def setup():
    os.makedirs(settings.DOWNLINK_CONFIGURATION_PATH, exist_ok=True)
    return True


def get_and_write_config():
    logger.debug('[ ] Fetching remote config')
    configuration = api.get_configuration()
    logger.debug('[✔] Fetching remote config')
    logger.debug('[ ] Writing Remote config to disk')
    with open(settings.DOWNLINK_CONFIGURATION_FILE, 'w') as f:
        json.dump(configuration, f)
    logger.info('[✔] Remote config written to disk')


def health_check():
    logger.debug('[ ] Health check')
    api.health_check()
    logger.info('[✔] Health check')


def is_expired(updated_at, threshold):
    if updated_at is None:
        return True
    now = datetime.utcnow()
    logger.debug(
        f'Checking expiry: {now}, {updated_at}, {now - updated_at} - '
        f't: {threshold.seconds}'
    )
    return now - updated_at > threshold


def downlink(event_queue, config_expiry=settings.DOWNLINK_CONFIG_EXPIRY):
    logger.info('Beginning downlink from host...')
    logger.info(f'downlink pid: {os.getpid()} [P: {os.getppid()}]')

    if not setup():
        logger.warning('Unable to setup downlink.')
        return

    config_updated_at = None

    while True:
        with managed_status(event_queue, StatusLight.downlink) as light:
            try:
                health_check()
                if is_expired(config_updated_at, config_expiry):
                    get_and_write_config()
                    config_updated_at = datetime.utcnow()
            except Exception as e:
                light('flash_error')
                logger.error(f'Downlink error: {e}.')

        time.sleep(settings.Wait.background)
