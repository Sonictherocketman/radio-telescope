from dataclasses import dataclass
from contextlib import contextmanager
import logging
import time

from . import settings


logger = logging.getLogger('astronomer')


try:
    import RPi.GPIO as GPIO
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
except ImportError:
    GPIO = None
    logger.warning(
        'Running outside of RPi Environment. '
        'Defaulting to status messages as backup.'
    )


@dataclass
class StatusLight:
    pin: int = None

    FAST_DELAY = 0.15
    SLOW_DELAY = 0.3

    def __init__(self, pin: int = None):
        super().__init__()
        self.pin = pin
        logger.debug(f'Initializing {self.pin}.')
        if GPIO:
            GPIO.setup(self.pin, GPIO.OUT)
            logger.debug(f'[GPIO Available] Pin {self.pin} setup.')
        else:
            logger.warning(f'[GPIO Unavailable] Pin {self.pin} setup.')
        self.off()

    def _flash(self, n=1, delay=FAST_DELAY, end_state=False):
        for _ in range(0, n):
            self.off()
            time.sleep(delay)
            self.on()
            time.sleep(delay)
            self.off()
            time.sleep(delay)
        if end_state:
            self.on()

    def flash_fast(self, n=1, end_state=False):
        self._flash(n, self.FAST_DELAY, end_state)

    def flash_slow(self, n=1, end_state=False):
        self._flash(n, self.SLOW_DELAY, end_state)

    def flash_ok(self):
        self.flash_fast(n=2)

    def flash_error(self):
        self.flash_slow(n=3)

    def on(self):
        if GPIO:
            GPIO.output(self.pin, GPIO.HIGH)
            logger.debug(f'[GPIO Unavailable] Pin {self.pin} on.')
        else:
            logger.warning(f'[GPIO Unavailable] Pin {self.pin} on.')

    def off(self):
        if GPIO:
            GPIO.output(self.pin, GPIO.LOW)
            logger.debug(f'[GPIO Unavailable] Pin {self.pin} off.')
        else:
            logger.warning(f'[GPIO Unavailable] Pin {self.pin} off.')


TransmitStatusLight = StatusLight(pin=settings.TRANSMIT_STATUS_PIN)
CaptureStatusLight = StatusLight(pin=settings.CAPTURE_STATUS_PIN)
DownlinkStatusLight = StatusLight(pin=settings.DOWNLINK_STATUS_PIN)


class Status:
    transmit = 'transmit'
    capture = 'capture'
    downlink = 'downlink'

    _lights = {
        transmit: TransmitStatusLight,
        capture: CaptureStatusLight,
        downlink: DownlinkStatusLight,
    }

    @classmethod
    def light_for(cls, name):
        return cls._lights.get(name)


@contextmanager
def use_light(light: StatusLight, initial_state=True) -> StatusLight:
    start_at = time.time()
    if initial_state:
        light.on()
    else:
        light.off()
    try:
        yield light
    finally:
        if time.time() - start_at < 1:
            logger.debug('Adding 1s delay for LED toggle to avoid burnout.')
            time.sleep(1)
        light.off()


@contextmanager
def managed_status(status: str, initial_state=True) -> StatusLight:
    with use_light(Status.light_for(status), initial_state=initial_state) as light:
        yield light
