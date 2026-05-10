from concurrent.futures import ThreadPoolExecutor
from multiprocessing import get_logger
import os
from queue import SimpleQueue

from .. import settings
from ..models.lights import StatusLight
from ..unsafe.io import register_event_callback, setup_dummy_server, IS_TEST_MODE, Light


logger = get_logger()


def process_light(name, value, light):
    if value is True:
        method = 'on'
    elif value is False:
        method = 'off'
    else:
        method = value

    try:
        getattr(light, method)()
    except Exception as e:
        logger.warn(f'No method on light found for method: {method}')


def get_light_handler(name, entry):
    logger.debug(f'[I/O] Configuring handler for: Light={name}')
    queue, light = entry['queue'], entry['light']
    def light_handler():
        while True:
            action = queue.get()
            logger.debug(f'[I/O] Light={name} received action: {action}')
            process_light(name, action, light)

    return light_handler


def handle_io(event_queue, should_calibrate, should_observe):
    """ Handle status events for toggling lights/sounds and button input. """
    logger.info('[I/O] Configuring status indicators...')

    ##
    # Lights
    ##

    lights = {
        name: {
            'queue': SimpleQueue(),
            'light': Light(pin),
        }
        for name, pin in StatusLight.pins.items()
    }

    logger.info('[I/O] Configuring input triggers...')

    if IS_TEST_MODE:
        logger.info('[I/O] Setting up dummy test server...')
        setup_dummy_server()

    ##
    # Buttons
    ##

    # Calibrate

    def set_should_calibrate(*args):
        logger.info('[I/O] Calibrate command detected.')
        should_calibrate.set()
        lights[StatusLight.calibrate]['queue'].put('flash_ok')

    register_event_callback(
        settings.CAPTURE_CALIBRATE_INPUT_CHANNEL,
        set_should_calibrate,
    )

    # Observe

    def toggle_should_observe(*args):
        logger.info('[I/O] Toggle observe command detected.')
        if should_observe.is_set():
            should_observe.clear()
        else:
            should_observe.set()
        lights[StatusLight.capture]['queue'].put('flash_ok')

    register_event_callback(
        settings.CAPTURE_OBSERVE_INPUT_CHANNEL,
        toggle_should_observe,
    )

    logger.info('[I/O] Listening...')
    logger.info(f'[I/O] pid: {os.getpid()} [P: {os.getppid()}]')
    with ThreadPoolExecutor(max_workers=len(StatusLight.pins)) as executor:
        for light, value in lights.items():
            executor.submit(get_light_handler(light, value))

        # Reset state

        for light, value in lights.items():
            value['queue'].put(False)

        # Listen for new events

        while True:
            try:
                kind, name, value = event_queue.get()
            except ValueError as e:
                logger.error(f'Malformed event. Wrong number of values: {e}')
                continue

            if kind == 'light':
                logger.debug(f'[I/O] {kind}({name=}, {value=})')
                lights.get(name)['queue'].put(value)
            else:
                logger.warn(f'[I/O] Unknown Event: {kind}({name=}, {value=})')
