import os
import os.path
import tempfile
import urllib.parse


# General Settings

USER_AGENT = 'astronomer/1.0'
DEFAULT_REQUEST_TIMEOUT = 15
DATABASE_LOCATION = os.path.expanduser(os.environ.get(
    'DATABASE_LOCATION',
    './db.sqlite',
))

TELESCOPE_ID = os.environ['TELESCOPE_ID']

CALIBRATION_PATH = os.path.expanduser(os.environ.get(
    'CALIBRATION_PATH',
    tempfile.gettempdir(),
))

CALIBRATE_STATUS_PIN = 24

# Capture Settings

CAPTURE_DATA_PATH = os.path.expanduser(os.environ.get(
    'DATA_PATH',
    './data/iqdp',
))

CAPTURE_STATUS_PIN = int(os.environ.get(
    'CAPTURE_STATUS_PIN',
    24,
))

CAPTURE_TEST_MODE_ENABLED = True  # TODO

CAPTURE_OBSERVE_INPUT_CHANNEL = None

CAPTURE_CALIBRATE_INPUT_CHANNEL = None

CAPTURE_FREQUENCY = 1.4204e8

CAPTURE_BANDWIDTH = 1e6

CAPTURE_GAIN = 49.6

CAPTURE_SAMPLE_RATE = 3.2e6

CAPTURE_SAMPLE_SIZE = 2**16

# Spectrum Settings

SPECTRUM_DATA_PATH = os.path.expanduser(os.environ.get(
    'DATA_PATH',
    './data/spectra',
))

SPECTRUM_STATUS_PIN = int(os.environ.get(
    'CAPTURE_STATUS_PIN',
    24,  # TODO
))

SPECTRUM_BATCH_SIZE = 3

# Transmit Settings

HOME_AUTHORIZATION_TOKEN = os.environ['HOME_AUTHORIZATION_TOKEN']
HOME_URL = os.environ.get(
    'HOME_URL',
    'https://starsweep.space',
)
HOME_API_HEALTH_CHECK_URL = os.environ.get(
    'HOME_API_HEALTH_CHECK_URL',
    urllib.parse.urljoin(HOME_URL, f'/api/telescope/{TELESCOPE_ID}/health-check'),
)
HOME_API_TRANSMIT_URL = os.environ.get(
    'HOME_API_TRANSMIT_URL',
    urllib.parse.urljoin(HOME_URL, f'/api/telescope/{TELESCOPE_ID}/transmit'),
)
TRANSMIT_WAIT_SECONDS = 60
TRANSMIT_BATCH_SIZE = 1_000

TRANSMIT_STATUS_PIN = int(os.environ.get(
    'TRANSMIT_STATUS_PIN',
    23,
))

# Downlink Settings

DOWNLINK_CONFIGURATION_URL = os.environ.get(
    'DOWNLINK_CONFIGURATION_URL',
    urllib.parse.urljoin(HOME_URL, f'/api/telescope/{TELESCOPE_ID}/tasks'),
)
DOWNLINK_EVENT_STREAM_URL = os.environ.get(
    'DOWNLINK_EVENT_STREAM_URL',
    urllib.parse.urljoin(HOME_URL, f'/api/events/TEL-{TELESCOPE_ID}'),
)
DOWNLINK_EVENT_STREAM_TIMEOUT = 30
DOWNLINK_RECONNECT_SECONDS = 10

DOWNLINK_STATUS_PIN = int(os.environ.get(
    'DOWNLINK_STATUS_PIN',
    11,
))

# Lackey Configuration Settings

# STEP_ANGLE =
STEP_DURATION_SECONDS = 10
