import gzip
import logging
import os
import os.path
import json
from multiprocessing import get_logger
import random
import shutil
from subprocess import CalledProcessError
import time

import httpx

from .. import settings
from ..utils import api
from ..mpsafe import managed_status
from ..models.lights import StatusLight


logger = get_logger()


def ping_home():
    logger.debug(f'Attempting to ping {settings.HOME_API_HEALTH_CHECK_URL}...')
    try:
        return api.health_check()
    except Exception:
        return False


def loop(
    event_queue,
    batch_size=settings.TRANSMIT_BATCH_SIZE,
    total_associated_files_per_sample=3,
):
    files = [
        os.path.join(settings.SPECTRUM_DATA_PATH, file)
        for file in sorted(os.listdir(settings.SPECTRUM_DATA_PATH))
        if file.endswith('.json')
    ]

    if not files:
        logger.debug('No data files found.')
        return

    batch = files[:batch_size]
    logger.info(f'Found {len(files)} total to transmit. Uploading {len(batch)}.')
    for path in batch:
        with open(path) as f:
            config = json.load(f)

        identifier = config.get('identifier', None)
        if not identifier:
            logger.error('Found malformed data config. Purging...')
            os.remove(path)
            continue

        # Find all related files

        associated_files = [
            os.path.join(settings.SPECTRUM_DATA_PATH, file)
            for file in os.listdir(settings.SPECTRUM_DATA_PATH)
            if identifier in file
        ]

        if len(associated_files) != total_associated_files_per_sample:
            logger.error('Found malformed sample. Uploading partial data.')

        logger.info(f'Transmitting sample ({identifier}) to remote host...')
        try:
            for path in associated_files:
                with managed_status(event_queue, StatusLight.transmit):
                    api.upload_observation(path)
        except CalledProcessError as e:
            logger.warning(
                f'Transmission failure: {path}. '
                f'Status Code: {e.returncode} '
                f'Exception thrown during transmision: {e}'
            )
            event_queue.put(('light', StatusLight.transmit, 'flash_error'))
        else:
            for path in associated_files:
                os.remove(path)
            logger.info('Transmission complete.')
            event_queue.put(('light', StatusLight.analysis, 'flash_ok'))

        # Sleep for a while to not overload the server.
        time.sleep(random.randint(0, 10))


def transmit(event_queue):
    """ Search the given spectrum data path and upload whatever is found there. """
    logger.info(f'[Transmit] pid: {os.getpid()} [P: {os.getppid()}]')
    while not ping_home():
        logger.error(
            'Unable to ping home. Are you sure there is internet? '
            f'Will try again in {settings.Wait.background} '
        )
        time.sleep(settings.Wait.background)

    while True:
        logger.debug('Beginning transmission...')
        try:
            loop(event_queue)
        except Exception as e:
            logger.warning(f'Received error: {e}. Retrying...')
        finally:
            logger.debug('Ending transmission. Sleeping...')
        time.sleep(settings.Wait.background)

    logger.info('Done')
