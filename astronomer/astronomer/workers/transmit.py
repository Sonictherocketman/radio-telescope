import gzip
import logging
import os
import os.path
import json
import random
import shutil
from subprocess import CalledProcessError
import time

import httpx

from .. import settings
from ..utils import api
from ..mpsafe import managed_status
from ..models.lights import StatusLight


def ping_home(log):
    log.put(('debug', f'Attempting to ping {settings.HOME_API_HEALTH_CHECK_URL}...'))
    return True # TODO
    try:
        return api.health_check()
    except Exception:
        return False


def loop(
    log,
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
        log.put(('debug', 'No data files found.'))
        return

    batch = files[:batch_size]
    log.put(('info', f'Found {len(files)} total to transmit. Uploading {len(batch)}.'))
    for path in batch:
        with open(path) as f:
            config = json.load(f)

        identifier = config.get('identifier', None)
        if not identifier:
            log.put(('error', 'Found malformed data config. Purging...'))
            os.remove(path)
            continue

        # Find all related files

        associated_files = [
            os.path.join(settings.SPECTRUM_DATA_PATH, file)
            for file in os.listdir(settings.SPECTRUM_DATA_PATH)
            if identifier in file
        ]

        if len(associated_files) != total_associated_files_per_sample:
            log.put(('error', 'Found malformed sample. Uploading partial data.'))

        log.put(('info', f'Transmitting sample ({identifier}) to remote host...'))
        try:
            for path in associated_files:
                with managed_status(event_queue, StatusLight.transmit):
                    api.upload_observation(path)
        except CalledProcessError as e:
            log.put((
                'warning',
                f'Transmission failure: {path}. '
                f'Status Code: {e.returncode} '
                f'Exception thrown during transmision: {e}'
            ))
            event_queue.put((StatusLight.transmit, 'flash_error'))
        else:
            for path in associated_files:
                os.remove(path)
            log.put(('info', 'Transmission complete.'))
            event_queue.put((StatusLight.analysis, 'flash_ok'))

        # Sleep for a while to not overload the server.
        time.sleep(random.randint(0, 10))


def transmit(log, event_queue):
    """ Search the given spectrum data path and upload whatever is found there. """
    while not ping_home(log):
        log.put((
            'error',
            'Unable to ping home. Are you sure there is internet? '
            f'Will try again in {settings.Wait.background} '
        ))
        time.sleep(settings.Wait.background)

    while True:
        log.put(('debug', 'Beginning transmission...'))
        try:
            loop(log, event_queue)
        except Exception as e:
            log.put(('warning', f'Received error: {e}. Retrying...'))
        finally:
            log.put(('debug', 'Ending transmission. Sleeping...'))
        time.sleep(settings.Wait.background)

    log.put(('info', 'Done'))
