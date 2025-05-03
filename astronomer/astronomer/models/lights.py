from .. import settings


class StatusLight:

    transmit = 'transmit'
    capture = 'capture'
    calibrate = 'calibrate'
    downlink = 'downlink'
    analysis = 'analysis'

    pins = {
        transmit: settings.TRANSMIT_STATUS_PIN,
        capture: settings.CAPTURE_STATUS_PIN,
        downlink: settings.DOWNLINK_STATUS_PIN,
        analysis: settings.SPECTRUM_STATUS_PIN,
        calibrate: settings.CALIBRATE_STATUS_PIN,
    }
