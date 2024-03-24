from datetime import datetime, UTC
import logging
import os
import shlex
from subprocess import run, CalledProcessError
import time

from . import settings


logger = logging.getLogger('astronomer')


HEADER_TEMPLATE = """
# Frequency: {frequency}
# Sample Rate: {sample_rate}
# Gain: {gain}
# PPM: {ppm}
# N-Samples: {n}
# Capture Time: {timestamp}
"""


def setup():
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
            -f {settings.CAPTURE_CENTER_FREQUENCY} \
            -s {settings.CAPTURE_SAMPLE_RATE} \
            -d {device_index} \
            -g {settings.CAPTURE_GAIN} \
            -p {settings.CAPTURE_PPM} \
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
    frequency,
    sample_rate,
    gain=0,
    device_index=0,
    ppm=0,
    n=0,
    compression=1,
):
    """ Take a reading from the device given the settings provided
    and save those to the a file as a compressed archive.
    """
    now = datetime.now(UTC)
    header = HEADER_TEMPLATE.format(
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
            rtl_sdr \
                -f {frequency} \
                -s {sample_rate} \
                -d {device_index} \
                -g {gain} \
                -p {ppm} \
                -S \
                -n {n} {filename};
    """

    return run(
        command,
        shell=True,
#         check=True,
        capture_output=True,
        cwd=settings.CAPTURE_DATA_PATH,
    )


def loop():
    try:
        take_reading(
            frequency=settings.CAPTURE_CENTER_FREQUENCY,
            sample_rate=settings.CAPTURE_SAMPLE_RATE,
            gain=settings.CAPTURE_GAIN,
            ppm=settings.CAPTURE_PPM,
            n=settings.CAPTURE_SAMPLES_PER_DUMP
        )
    except CalledProcessError as e:
        logger.error(f'Failed to take reading. {e}')
        raise e

    # TODO: Check Bounds & Move


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
            logger.error('Encountered error during recording. Exiting...')
    else:
        logger.error('Setup failed. Exiting.')

    logger.info('Done.')


