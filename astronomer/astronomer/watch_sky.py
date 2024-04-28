from datetime import datetime
import logging
import os
import shlex
from subprocess import run, CalledProcessError
import time

from . import db, settings


logger = logging.getLogger('astronomer')

connection = None


HEADER_TEMPLATE = """
# Frequency: {frequency}
# Sample Rate: {sample_rate}
# Gain: {gain}
# PPM: {ppm}
# N-Samples: {n}
# Capture Time: {timestamp}
# Identifier: {identifier}
"""


def setup():
    # Setup database
    global connection
    connection = db.setup_and_connect()

    # TODO: Reset position

    # TODO: Check Lackey Connections

    # Setup data directories
    os.makedirs(settings.CAPTURE_DATA_PATH, exist_ok=True)

    # Test SDR Connection
    device_is_functional = test_device()
    if not device_is_functional:
        logger.error('Failed receiving test data from SDR.')
        return False

    return True


def test_device(n=10, device_index=0):
    command = f"""
        rtl_sdr \
            -f {settings.CAPTURE_TEST_CENTER_FREQUENCY} \
            -d {device_index} \
            -S \
            -n {n} -
    """

    try:
        run(
            command,
            shell=True,
            check=True,
            cwd=settings.CAPTURE_DATA_PATH,
            capture_output=True,
        )
    except CalledProcessError:
        return False
    else:
        return True


def take_reading(
    identifier,
    frequency,
    sample_rate,
    gain=0,
    device_index=0,
    ppm=0,
    n=0,
):
    """ Take a reading from the device given the settings provided
    and save those to the a file as a compressed archive.
    """
    now = datetime.utcnow()
    header = HEADER_TEMPLATE.format(
        identifier=identifier,
        frequency=frequency,
        sample_rate=sample_rate,
        gain=gain,
        ppm=ppm,
        n=n,
        timestamp=str(now),
    ).strip()

    short_now = now.strftime('%Y-%m-%dT%H-%M-%S-%f%z')
    filename = f'sample-{short_now}.iqd'

    command = f"""
        {{
            echo "{header}";
            rtl_sdr \
                -f {frequency} \
                -s {sample_rate} \
                -d {device_index} \
                -g {gain} \
                -p {ppm} \
                -S \
                -n {n} - | base64 | fold -s -w80;
        }} > {filename}
    """

    return run(
        command,
        shell=True,
        capture_output=True,
        cwd=settings.CAPTURE_DATA_PATH,
    )


def loop():
    with connection as cursor:
        tasks = db.list_active_tasks(cursor, datetime.utcnow())


    # TODO: Check Bounds & Move

    # TODO: Track?

    for task in tasks:
        try:
            take_reading(
                identifier=task['id'],
                frequency=task['frequency'],
                sample_rate=task['sample_rate'],
                gain=task['gain'],
                ppm=task['ppm'],
                n=task['sample_size'],
            )
        except CalledProcessError as e:
            logger.error(f'Failed to take reading. {e}')
            raise e


def watch_sky():
    """ Continuously watch the sky and record values to disk. """
    if setup():
        logger.info('Capturing data...')
        try:
            while True:
                logger.debug('Begin data capture iteration...')
                loop()
                logger.debug('End data capture iteration. Sleeping...')
                time.sleep(settings.STEP_DURATION_SECONDS)
        except Exception as e:
            logger.error(f'Encountered error during recording. {e}. Exiting...')
    else:
        logger.error('Setup failed. Exiting.')

    logger.info('Done.')
