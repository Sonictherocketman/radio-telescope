from base64 import b64encode
from datetime import datetime
import os
import time

from rtlsdr import RtlSdr, rtlsdr

from .. import settings
from ..models.lights import StatusLight
from ..models.observation import Observation
from ..mpsafe import managed_status
from ..unsafe.devices import DefaultDevice
from ..utils import iqdp


device: DefaultDevice = None
calibration: Observation = None


def setup(log, event_queue, test_mode=False, bias_tee=True):
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


def warm_up(log, sample_rate, frequency, gain, bandwidth, n=int(1e7)):
    log.put(('info', f'Performing device warmup {n=}...'))
    global device
    device.read(
        sample_rate=sample_rate,
        frequency=frequency,
        gain=gain,
        bandwidth=bandwidth,
        n=n,
    )


def take_calibration_reading(log, *args, **kwargs):
    log.put(('info', '[Calibration] Begin...'))
    observation = take_reading(
        log,
        *args,
        directory=settings.CALIBRATION_PATH,
        **kwargs,
    )
    global calibration
    calibration = observation
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
    directory=settings.CAPTURE_DATA_PATH,
) -> Observation:
    """ Take a reading from the device given the settings provided
    and save those to the a file as a compressed archive.
    """
    filename = f'sample-{identifier}.iqdp'
    path = os.path.join(directory, filename)

    global device
    log.put(('debug', 'Collecting data from device...'))
    signal = device.read(
        sample_rate=sample_rate,
        frequency=frequency,
        gain=gain,
        bandwidth=bandwidth,
        n=n,
    )

    observation = Observation(
        identifier=identifier,
        frequency=frequency,
        sample_rate=sample_rate,
        gain=gain,
        bandwidth=bandwidth,
        signal=signal,
        # TODO: Check the calibration has the same settings as
        # the current observation. If not, do not use.
        calibration=calibration,
    )

    log.put(('debug', 'Writing data to disk...'))
    iqdp.write(path, observation)


def loop(log, event_queue, should_calibrate, should_observe):
    now = datetime.utcnow()
    short_now = now.strftime('%Y-%m-%dT%H-%M-%S-%f%Z')

    kwargs = dict(
        identifier=short_now,
        frequency=settings.CAPTURE_FREQUENCY,
        sample_rate=settings.CAPTURE_SAMPLE_RATE,
        gain=settings.CAPTURE_GAIN,
        n=settings.CAPTURE_SAMPLE_SIZE,
        bandwidth=settings.CAPTURE_BANDWIDTH,
        ts=now,
    )

    try:
        with managed_status(event_queue, StatusLight.capture):
            if should_calibrate.is_set():
                take_calibration_reading(log, **kwargs)
                should_calibrate.clear()
            if should_observe.is_set():
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
                    settings.CAPTURE_FREQUENCY,
                    settings.CAPTURE_SAMPLE_RATE,
                    settings.CAPTURE_GAIN,
                    settings.CAPTURE_BANDWIDTH,
                )
            log.put(('info', 'Capturing data...'))
            while True:
                log.put(('debug', 'Begin data capture iteration...'))
                loop(log, event_queue, should_calibrate, should_observe)
                log.put(('debug', 'End data capture iteration. Sleeping...'))
                time.sleep(settings.STEP_DURATION_SECONDS)
        except KeyboardInterrupt:
            log_queue.put(('info', 'Interrupted by user.'))
        except Exception as e:
            log.put(('error', f'Encountered error during recording. {e}. Exiting...'))
    else:
        log.put(('error', 'Setup failed. Exiting.'))

    log.put(('info', 'Done.'))
