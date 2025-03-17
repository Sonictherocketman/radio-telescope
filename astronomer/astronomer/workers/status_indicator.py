import logging
import sys

from ..models.lights import StatusLight


logger = logging.getLogger('astronomer.worker')


def process_light(name, value, lights):
    if value is True:
        method = 'on'
    elif value is False:
        method = 'off'
    else:
        method = value

    try:
        getattr(lights[name], method)()
    except KeyError:
        logger.warn(f'No method on light found for method: {method}')


def handle_events(log, event_queue):
    """ Handle status events for toggling lights/sounds. """
    log.put(('info', '[Indicator] Configuring indicators...'))
    # Enable Lights. Do this here to avoid multi-import in
    # process pool children.
    from ..unsafe.io import Light
    lights = {
        name: Light(pin)
        for name, pin in StatusLight.pins.items()
    }

    log.put(('info', '[Indicator] Listening...'))
    while True:
        kind, name, value = event_queue.get()
        if kind == 'light':
            log.put(('debug', f'[Indicator] {kind}({name=}, {value=})'))
            process_light(name, value, lights)
        else:
            log.put(('warn', f'[Indicator] Unknown Event: {kind}({name=}, {value=})'))
