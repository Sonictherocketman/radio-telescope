from base64 import b64encode
from datetime import datetime
from multiprocessing import get_logger
import os
import shutil
import time


from .. import settings
from ..models.lights import StatusLight
from ..models.observation import Observation, Calibration
from ..mpsafe import managed_status
from ..unsafe.devices import DefaultDevice
from ..utils.attributes import load_relevant_attributes
from ..utils import iqd


logger = get_logger()


device: DefaultDevice = None
calibration: Calibration = None
calibration_signal_path = None


CALIBRATION_FILE_EXTENSION = '.ciq'
SIGNAL_FILE_EXTENSION = '.iq'
CONFIG_FILE_EXTENSION = '.json'


def setup(
    event_queue,
    sample_rate,
    frequency,
    gain,
    bandwidth,
    test_mode=False,
    bias_tee=False,
):
    # Connect to SDR
    if test_mode:
        logger.info('Test SDR mode: enabled')
    global device
    try:
        device = DefaultDevice(
            sample_rate=sample_rate,
            frequency=frequency,
            gain=gain,
            bandwidth=bandwidth,
            test_mode=test_mode,
            bias_tee=bias_tee,
        )
    except Exception as e:
        logger.error(f'Unable to use SDR: {e}')
        return False

    # Setup data directories
    os.makedirs(settings.CAPTURE_DATA_PATH, exist_ok=True)
    os.makedirs(settings.CALIBRATION_DATA_PATH, exist_ok=True)

    # Test SDR Connection
    with managed_status(
        event_queue,
        StatusLight.capture,
        initial_state=False,
    ) as light:
        if not device.test():
            logger.error('Failed receiving test data from SDR.')
            light('flash_error')
            return False
        else:
            light('flash_ok')
            return True


def warm_up(
    n=settings.WARM_UP_SAMPLES,
    destination='/dev/null',
):
    global device
    estimated_time = n // device.sample_rate
    logger.info(f'Performing device warmup {n=}, {estimated_time=}s...')
    device.read(destination, n=n)


def take_calibration_reading(*args, c_ext=CALIBRATION_FILE_EXTENSION, **kwargs):
    logger.info('[Calibration] Begin...')
    observation, signal_path = take_reading(
        *args,
        directory=settings.CALIBRATION_DATA_PATH,
        signal_ext=c_ext,
        use_calibration=False,
        is_calibration=True,
        **kwargs,
    )
    global calibration
    calibration = observation
    global calibration_signal_path
    calibration_signal_path = signal_path
    logger.info('[Calibration] End.')


def take_reading(
    identifier,
    frequency,
    sample_rate,
    gain=0,
    n=1,
    bandwidth=1,
    ts=None,
    use_calibration=True,
    is_calibration=False,
    signal_ext=SIGNAL_FILE_EXTENSION,
    config_ext=CONFIG_FILE_EXTENSION,
    c_ext=CALIBRATION_FILE_EXTENSION,
    directory=settings.CAPTURE_DATA_PATH,
    observation_attributes_config_path=settings.DOWNLINK_CONFIGURATION_FILE,
) -> (Observation, str):
    """ Take a reading from the device given the settings provided
    and save those to the a file as a compressed archive.
    """
    signal_filename = f'{identifier}{signal_ext}'
    signal_path = os.path.join(directory, signal_filename)

    if is_calibration:
        extra_kwargs = {}
    else:
        extra_kwargs = dict(attributes=load_relevant_attributes())

    estimated_time = n // sample_rate
    logger.debug(f'Collecting data from device {n=}, {estimated_time=}s...')

    # Capture the signal

    device.read(signal_path, n=n)

    # Write the config

    type = Calibration if is_calibration else Observation
    observation = type(
        identifier=identifier,
        frequency=frequency,
        sample_rate=sample_rate,
        gain=gain,
        bandwidth=bandwidth,
        timestamp=datetime.utcnow().isoformat(),
        n=n,
        **extra_kwargs,
    )

    if use_calibration and calibration is not None:
        logger.debug('Copying calibration data...')
        observation.calibration = calibration

        c_signal_filename = f'{identifier}{c_ext}'
        c_signal_path = os.path.join(directory, c_signal_filename)
        shutil.copyfile(calibration_signal_path, c_signal_path)

    logger.debug('Writing config data to disk...')
    observation_filename = f'{identifier}{config_ext}'
    observation_path = os.path.join(directory, observation_filename)
    iqd.write_config(observation_path, observation)
    return observation, signal_path


def loop(event_queue, should_calibrate, should_observe):
    now = datetime.utcnow()
    short_now = now.strftime('%Y-%m-%dT%H-%M-%S-%f%Z')

    kwargs = dict(
        identifier=f'sample-{short_now}',
        frequency=settings.CAPTURE_FREQUENCY,
        sample_rate=settings.CAPTURE_SAMPLE_RATE,
        gain=settings.CAPTURE_GAIN,
        n=settings.CAPTURE_SAMPLE_SIZE,
        bandwidth=settings.CAPTURE_BANDWIDTH,
        ts=now,
    )

    try:
        if should_calibrate.is_set():
            with managed_status(event_queue, StatusLight.calibrate):
                take_calibration_reading(**kwargs)
                should_calibrate.clear()
        if should_observe.is_set():
            with managed_status(event_queue, StatusLight.capture):
                take_reading(**kwargs)
    except Exception as e:
        logger.error(f'Failed to take reading. {e}')
        raise e


def watch_sky(event_queue, should_calibrate, should_observe):
    """ Continuously watch the sky and record values to disk. """
    if setup(
        event_queue,
        settings.CAPTURE_SAMPLE_RATE,
        settings.CAPTURE_FREQUENCY,
        settings.CAPTURE_GAIN,
        settings.CAPTURE_BANDWIDTH,
        settings.CAPTURE_TEST_MODE_ENABLED,
    ):
        try:
            logger.info(f'[WatchSky] pid: {os.getpid()} [P: {os.getppid()}]')
            with managed_status(event_queue, StatusLight.capture):
                warm_up()
            logger.info('Ready...')
            while True:
                logger.debug('Begin data capture iteration...')
                loop(event_queue, should_calibrate, should_observe)
                logger.debug('End data capture iteration. Sleeping...')
                time.sleep(settings.Wait.device)
        except KeyboardInterrupt:
            logger.info('Interrupted by user.')
        except Exception as e:
            logger.error(f'Encountered error during recording. {e}. Exiting...')
    else:
        logger.error('Setup failed. Exiting.')

    logger.info('Done.')
