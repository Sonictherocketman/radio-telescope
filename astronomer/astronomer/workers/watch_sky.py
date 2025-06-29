from base64 import b64encode
from datetime import datetime
import os
import shutil
import time

from rtlsdr import RtlSdr, rtlsdr

from .. import settings
from ..models.lights import StatusLight
from ..models.observation import Observation, Calibration
from ..mpsafe import managed_status
from ..unsafe.devices import DefaultDevice
from ..utils import iqd


device: DefaultDevice = None
calibration: Calibration = None
calibration_signal_path = None


CALIBRATION_FILE_EXTENSION = '.ciq'
SIGNAL_FILE_EXTENSION = '.iq'
CONFIG_FILE_EXTENSION = '.json'


def setup(log, event_queue, test_mode=False, bias_tee=False):
    # Connect to SDR
    if test_mode:
        log.put(('info', 'Test SDR mode: enabled'))
    global device
    try:
        device = DefaultDevice(test_mode=test_mode, bias_tee=bias_tee)
    except Exception as e:
        log.put(('critical', f'Unable to use SDR: {e}'))
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
            log.put(('error', 'Failed receiving test data from SDR.'))
            light('flash_error')
            return False
        else:
            light('flash_ok')
            return True


def warm_up(
    log,
    sample_rate,
    frequency,
    gain,
    bandwidth,
    n=settings.WARM_UP_SAMPLES,
    destination='/dev/null',
):
    estimated_time = n // sample_rate
    log.put(('info', f'Performing device warmup {n=}, {estimated_time=}s...'))
    global device
    device.read(
        destination,
        sample_rate=sample_rate,
        frequency=frequency,
        gain=gain,
        bandwidth=bandwidth,
        n=n,
    )


def take_calibration_reading(log, *args, c_ext=CALIBRATION_FILE_EXTENSION, **kwargs):
    log.put(('info', '[Calibration] Begin...'))
    observation, signal_path = take_reading(
        log,
        *args,
        directory=settings.CALIBRATION_DATA_PATH,
        signal_ext=c_ext,
        use_calibration=False,
        **kwargs,
    )
    global calibration
    calibration = observation
    global calibration_signal_path
    calibration_signal_path = signal_path
    log.put(('info', '[Calibration] End.'))


def take_reading(
    log,
    identifier,
    frequency,
    sample_rate,
    gain=0,
    n=1,
    bandwidth=1,
    ts=None,
    use_calibration=True,
    signal_ext=SIGNAL_FILE_EXTENSION,
    config_ext=CONFIG_FILE_EXTENSION,
    c_ext=CALIBRATION_FILE_EXTENSION,
    directory=settings.CAPTURE_DATA_PATH,
) -> (Observation, str):
    """ Take a reading from the device given the settings provided
    and save those to the a file as a compressed archive.
    """
    signal_filename = f'{identifier}{signal_ext}'
    signal_path = os.path.join(directory, signal_filename)

    estimated_time = n // sample_rate
    log.put(('debug', f'Collecting data from device {n=}, {estimated_time=}s...'))

    # Capture the signal

    device.read(
        signal_path,
        sample_rate=sample_rate,
        frequency=frequency,
        gain=gain,
        bandwidth=bandwidth,
        n=n,
    )

    # Write the config

    observation = Observation(
        identifier=identifier,
        frequency=frequency,
        sample_rate=sample_rate,
        gain=gain,
        bandwidth=bandwidth,
        timestamp=datetime.utcnow().isoformat(),
    )

    if use_calibration and calibration is not None:
        log.put(('debug', 'Copying calibration data...'))
        observation.calibration = calibration

        c_signal_filename = f'{identifier}{c_ext}'
        c_signal_path = os.path.join(directory, c_signal_filename)
        shutil.copyfile(calibration_signal_path, c_signal_path)

    log.put(('debug', 'Writing config data to disk...'))
    observation_filename = f'{identifier}{config_ext}'
    observation_path = os.path.join(directory, observation_filename)
    iqd.write_config(observation_path, observation)
    return observation, signal_path


def loop(log, event_queue, should_calibrate, should_observe):
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
                take_calibration_reading(log, **kwargs)
                should_calibrate.clear()
        if should_observe.is_set():
            with managed_status(event_queue, StatusLight.capture):
                take_reading(log, **kwargs)
    except Exception as e:
        log.put(('error', f'Failed to take reading. {e}'))
        raise e


def watch_sky(log, event_queue, should_calibrate, should_observe):
    """ Continuously watch the sky and record values to disk. """
    if setup(log, event_queue, settings.CAPTURE_TEST_MODE_ENABLED):
        try:
            with managed_status(event_queue, StatusLight.capture):
                warm_up(
                    log,
                    settings.CAPTURE_SAMPLE_RATE,
                    settings.CAPTURE_FREQUENCY,
                    settings.CAPTURE_GAIN,
                    settings.CAPTURE_BANDWIDTH,
                )
            log.put(('info', 'Capturing data...'))
            while True:
                log.put(('debug', 'Begin data capture iteration...'))
                loop(log, event_queue, should_calibrate, should_observe)
                log.put(('debug', 'End data capture iteration. Sleeping...'))
                time.sleep(settings.Wait.device)
        except KeyboardInterrupt:
            log_queue.put(('info', 'Interrupted by user.'))
        except Exception as e:
            log.put(('error', f'Encountered error during recording. {e}. Exiting...'))
    else:
        log.put(('error', 'Setup failed. Exiting.'))

    log.put(('info', 'Done.'))
