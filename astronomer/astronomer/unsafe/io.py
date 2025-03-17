from dataclasses import dataclass
import logging
import time


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
class Light:
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
