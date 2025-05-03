from .. import settings
from ..models.lights import StatusLight
from ..unsafe.io import register_event_callback, setup_dummy_server, IS_TEST_MODE, Light


def process_light(name, value, lights, log):
    if value is True:
        method = 'on'
    elif value is False:
        method = 'off'
    else:
        method = value

    try:
        getattr(lights[name], method)()
    except KeyError:
        log.put(('warn', f'No method on light found for method: {method}'))


def handle_io(log, event_queue, should_calibrate, should_observe):
    """ Handle status events for toggling lights/sounds and button input. """
    log.put(('info', '[I/O] Configuring status indicators...'))

    # Lights

    lights = {
        name: Light(pin)
        for name, pin in StatusLight.pins.items()
    }

    log.put(('info', '[I/O] Configuring input triggers...'))

    if IS_TEST_MODE:
        log.put(('info', '[I/O] Setting up dummy test server...'))
        setup_dummy_server()

    # Calibrate

    def set_should_calibrate(*args):
        log.put(('debug', '[I/O] Calibrate command detected.'))
        should_calibrate.set()

    register_event_callback(
        settings.CAPTURE_CALIBRATE_INPUT_CHANNEL,
        set_should_calibrate,
    )

    # Observe

    def toggle_should_observe(*args):
        log.put(('debug', '[I/O] Toggle observe command detected.'))
        if should_observe.is_set():
            should_observe.clear()
        else:
            should_observe.set()

    # TODO: Make more concurrent for multiple lights at the same time.

    register_event_callback(
        settings.CAPTURE_OBSERVE_INPUT_CHANNEL,
        toggle_should_observe,
    )

    log.put(('info', '[I/O] Listening...'))
    while True:
        kind, name, value = event_queue.get()
        if kind == 'light':
            log.put(('debug', f'[I/O] {kind}({name=}, {value=})'))
            process_light(name, value, lights, log)
        else:
            log.put(('warn', f'[I/O] Unknown Event: {kind}({name=}, {value=})'))

