import gzip
import logging
import os
import os.path
import shutil
import tempfile

import httpx

from . import settings


logger = logging.getLogger('astronomer')


def ping_home(timeout=settings.DEFAULT_REQUEST_TIMEOUT):
    logger.debug(f'Attempting to ping {settings.HOME_API_HEALTH_CHECK_URL}...')
    response = httpx.get(
        settings.HOME_API_HEALTH_CHECK_URL,
        headers={
            'User-Agent': settings.USER_AGENT,
            'Authorization': f'Token {settings.HOME_AUTHORIZATION_TOKEN}',
        },
        timeout=timeout,
    )
    response.raise_for_status()
    return True


def transmit(filename, timeout=settings.DEFAULT_REQUEST_TIMEOUT):
    with open(filename, 'rb') as f:
        response = httpx.post(
            settings.HOME_API_TRANSMIT_URL,
            headers={
                'User-Agent': settings.USER_AGENT,
                'Authorization': f'Token {settings.HOME_AUTHORIZATION_TOKEN}',
                'Content-Encoding': 'gzip',
            },
            files={filename: f},
            timeout=timeout,
        )
        response.raise_for_status()
        return response.json()


def loop():
    files = [
        file
        for file in sorted(os.listdir(settings.CAPTURE_DATA_PATH))
        if file.endswith('.iqd') or file.endswith('.iqd.gz')
    ]

    if not files:
        logger.debug('No data files found.')
        return

    logger.info('Found {len(files)} to transmit.')
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
        try:
            transmit(gz_path)
        except httpx.RequestError as e:
            logger.warning(
                f'Transmission failure: {file}. '
                f'Status Code: {e.response.status_code} '
                f'Exception thrown during transmision: {e}'
            )
        else:
            os.remove(gz_path)
            logger.info('Transmission complete.')


def phone_home():
    """ Given the data in the database, watch for new entries
    and phone home when they appear.
    """
    try:
        ping_home()
    except Exception as e:
        logger.error(
            f'Unable to ping home. Are you sure there is internet? {e}'
        )
        return

    try:
        while True:
            logger.debug('Beginning transmission...')
            loop(connection)
            logger.debug('Ending transmission. Sleeping...')
            time.sleep(settings.TRANSMIT_WAIT_SECONDS)
    except Exception as e:
        logger.warning(f'Received error: {e}. Exiting...')
    finally:
        pass

    logger.info('Done')

