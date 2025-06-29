import os
import os.path
from pathlib import Path
import tempfile
import urllib.parse


BASE_DIR = Path(__file__).resolve().parent.parent


# General Settings

USER_AGENT = 'astronomer/1.0'
DEFAULT_REQUEST_TIMEOUT = 15
DATABASE_LOCATION = os.path.expanduser(os.environ.get(
    'DATABASE_LOCATION',
    os.path.join(BASE_DIR, './db.sqlite'),
))

TELESCOPE_ID = os.environ['TELESCOPE_ID']

CALIBRATION_PATH = os.path.expanduser(os.environ.get(
    'CALIBRATION_PATH',
    os.path.join(BASE_DIR, './data/calibration'),
))

CALIBRATE_STATUS_PIN = 24

# Capture Settings

CAPTURE_DATA_PATH = os.path.expanduser(os.environ.get(
    'DATA_PATH',
    os.path.join(BASE_DIR, './data/observations'),
))

CAPTURE_STATUS_PIN = int(os.environ.get(
    'CAPTURE_STATUS_PIN',
    25,
))

CAPTURE_TEST_MODE_ENABLED = True  # TODO

CAPTURE_OBSERVE_INPUT_CHANNEL = 'observe' # TODO

CAPTURE_CALIBRATE_INPUT_CHANNEL = 'calibrate' # TODO

CAPTURE_FREQUENCY = 1.4202e9

CAPTURE_BANDWIDTH = 1e6

CAPTURE_GAIN = 49.6

CAPTURE_SAMPLE_RATE = 3.2e6

CAPTURE_SAMPLE_SIZE = 2**25 + 32

WARM_UP_SAMPLES = CAPTURE_SAMPLE_SIZE

# Spectrum Settings

SPECTRUM_DATA_PATH = os.path.expanduser(os.environ.get(
    'DATA_PATH',
    os.path.join(BASE_DIR, './data/spectra'),
))

SPECTRUM_STATUS_PIN = int(os.environ.get(
    'SPECTRUM_STATUS_PIN',
    26,  # TODO
))

SIGNAL_BUFFER_LENGTH = 50
SPECTRUM_BATCH_SIZE = 10

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
TRANSMIT_BATCH_SIZE = 50

TRANSMIT_STATUS_PIN = int(os.environ.get(
    'TRANSMIT_STATUS_PIN',
    23,
))

DEFAULT_REQUEST_TIMEOUT = int(os.environ.get(
    'DEFAULT_REQUEST_TIMEOUT',
    10,
))
TRANSMIT_REMOTE_HOST = os.environ.get(
    'TRANSMIT_REMOTE_HOST',
    'starsweep.space'
)
TRANSMIT_REMOTE_USER = os.environ.get(
    'TRANSMIT_REMOTE_USER',
    'brian'
)
TRANSMIT_REMOTE_DIRECTORY = os.environ.get(
    'TRANSMIT_REMOTE_DIRECTORY',
    'data/'
)


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


class Wait:
    device = 0.3
    processing = 1
    background = 10


# Test Rig

TEST_SOCKET_HOST = ''
TEST_SOCKET_SEND_PORT = 50008
TEST_SOCKET_RECV_PORT = 50007
