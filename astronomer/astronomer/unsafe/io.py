from dataclasses import dataclass
import logging
import socket
import time

from .. import settings


logger = logging.getLogger('astronomer')


try:
    import RPi.GPIO as GPIO
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    IS_TEST_MODE = False
except ImportError:
    import threading
    IS_TEST_MODE = True
    GPIO = None
    logger.warning(
        'Running outside of RPi Environment. '
        'Defaulting to status messages as backup.'
    )
    dummy_callback_registry = {}


# BEGIN Test Rig


def get_dummy_socket_server(callback):
    def _socket_server():
        soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        soc.bind((settings.TEST_SOCKET_HOST, settings.TEST_SOCKET_RECV_PORT))
        while True:
            soc.listen(5)
            client, address = soc.accept()
            response = client.recv(255)
            callback(response)
    return _socket_server


def handle_dummy_callback(message: bytes):
    try:
        dummy_callback_registry[message.decode('ascii')]()
    except KeyError:
        logger.warning(f'Invalid message {message}')


def dummy_socket_send(message: [bytes]):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((settings.TEST_SOCKET_HOST, settings.TEST_SOCKET_SEND_PORT))
            s.sendall(message)
            logger.info(f'Message sent: {message}.')
    except IOError as e:
        logger.error(f'Unable to send message to remote socket: {e}')


def setup_dummy_server():
    server = get_dummy_socket_server(handle_dummy_callback)
    thread = threading.Thread(target=server)
    thread.daemon = True
    thread.start()


# END Test Rig


def register_event_callback(
    channel,
    callback,
    method=None,
    bouncetime=200,
):
    if GPIO:
        if method is None:
            method = GPIO.RISING
        GPIO.setup(channel, GPIO.IN)
        GPIO.add_event_detect(
            channel,
            method,
            callback=callback,
            bouncetime=bouncetime,
        )
    else:
        logger.warning(f'Preferring dummy callback rig for channel: {channel}')
        global dummy_callback_registry
        dummy_callback_registry[channel] = callback


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
            dummy_socket_send(f'{self.pin}-1'.encode('ascii'))
            logger.warning(f'[GPIO Unavailable] Pin {self.pin} on.')

    def off(self):
        if GPIO:
            GPIO.output(self.pin, GPIO.LOW)
            logger.debug(f'[GPIO Unavailable] Pin {self.pin} off.')
        else:
            dummy_socket_send(f'{self.pin}-0'.encode('ascii'))
            logger.warning(f'[GPIO Unavailable] Pin {self.pin} off.')
