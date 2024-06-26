import gzip
import logging
import os
import os.path
import random
import shutil
import time

import httpx

from . import api, settings
from .lights import managed_status, Status


logger = logging.getLogger('astronomer')


def ping_home():
    logger.debug(f'Attempting to ping {settings.HOME_API_HEALTH_CHECK_URL}...')
    return api.health_check()


def transmit_data(filename):
    with open(filename, 'rb') as f:
        return api.upload_observation(filename, f)


def loop():
    files = [
        file
        for file in sorted(os.listdir(settings.CAPTURE_DATA_PATH))
        if file.endswith('.iqd') or file.endswith('.iqd.gz')
    ]

    if not files:
        logger.debug('No data files found.')
        return

    logger.info(f'Found {len(files)} to transmit.')
    for file in files:
        path = os.path.join(settings.CAPTURE_DATA_PATH, file)

        if file.endswith('.iqd.gz'):
            logger.info('Skipping compression for already-compressed data.')
            gz_path = path
        else:
            gz_path = f'{path}.gz'
            with (
                open(path, 'rb') as input_file,
                gzip.open(gz_path, 'wb') as compressed_file
            ):
                logger.info(f'Compressing data file ({file}) for transport...')
                shutil.copyfileobj(input_file, compressed_file)
            os.remove(path)

        logger.info(f'Transmitting file ({file}) to remote host...')
        with managed_status(Status.transmit) as light:
            try:
                transmit_data(gz_path)
            except httpx.RequestError as e:
                logger.warning(
                    f'Transmission failure: {file}. '
                    f'Status Code: {e.response.status_code} '
                    f'Exception thrown during transmision: {e}'
                )
                light.flash_error()
            else:
                os.remove(gz_path)
                logger.info('Transmission complete.')
                light.flash_ok()

        # Sleep for a while to not overload the server.
        time.sleep(random.randint(0, 10))


def transmit():
    """ Given the data in the database, watch for new entries
    and phone home when they appear.
    """
    with managed_status(Status.transmit, initial_state=False) as light:
        try:
            ping_home()
        except Exception as e:
            light.flash_error()
            logger.error(
                f'Unable to ping home. Are you sure there is internet? {e}'
            )
            return
        else:
            light.flash_ok()

    while True:
        logger.debug('Beginning transmission...')
        try:
            loop()
        except Exception as e:
            logger.warning(f'Received error: {e}. Exiting...')
        finally:
            logger.debug('Ending transmission. Sleeping...')
            time.sleep(settings.TRANSMIT_WAIT_SECONDS)

    logger.info('Done')
