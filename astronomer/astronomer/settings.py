from datetime import timedelta
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

CALIBRATION_DATA_PATH = os.path.expanduser(os.environ.get(
    'CALIBRATION_DATA_PATH',
    os.path.join(BASE_DIR, './data/calibration'),
))

CALIBRATE_STATUS_PIN = 24

# Capture Settings

CAPTURE_DATA_PATH = os.path.expanduser(os.environ.get(
    'CAPTURE_DATA_PATH',
    os.path.join(BASE_DIR, './data/observations'),
))

CAPTURE_STATUS_PIN = int(os.environ.get(
    'CAPTURE_STATUS_PIN',
    25,
))

CAPTURE_TEST_MODE_ENABLED = False
# CAPTURE_TEST_MODE_ENABLED = True

CAPTURE_OBSERVE_INPUT_CHANNEL = 23
# CAPTURE_OBSERVE_INPUT_CHANNEL = 'observe'

CAPTURE_CALIBRATE_INPUT_CHANNEL = 13
# CAPTURE_CALIBRATE_INPUT_CHANNEL = 'calibrate'

CAPTURE_BANDWIDTH = 1e6

# shift the main freq off center
CAPTURE_FREQUENCY = 1.4202e9
CAPTURE_OFFSET = 0.0005e9

# CAPTURE_FREQUENCY = 8.91e7
# CAPTURE_OFFSET = 0.0005e7

CAPTURE_GAIN = 49.6

CAPTURE_SAMPLE_RATE = 2.4e6

CAPTURE_SAMPLE_SIZE = 2**22

WARM_UP_SAMPLES = 2**16

# Spectrum Settings

SPECTRUM_DATA_PATH = os.path.expanduser(os.environ.get(
    'SPECTRUM_DATA_PATH',
    os.path.join(BASE_DIR, './data/spectra'),
))

SPECTRUM_STATUS_PIN = int(os.environ.get(
    'SPECTRUM_STATUS_PIN',
    26,  # TODO
))

SIGNAL_BUFFER_LENGTH = 100
SPECTRUM_BATCH_SIZE = 10
SMOOTHING_WINDOW_LENGTH = 4
SMOOTHING_ENABLED = False
MIN_CHART_Y_SCALE = 0.2

# Transmit Settings

HOME_URL = os.environ.get(
    'HOME_URL',
    'https://starsweep.space',
)
HOME_API_HEALTH_CHECK_URL = os.environ.get(
    'HOME_API_HEALTH_CHECK_URL',
    urllib.parse.urljoin(HOME_URL, '/'),
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
    'astronomer'
)
TRANSMIT_TEST_MODE_ENABLED = False
# TRANSMIT_TEST_MODE_ENABLED = True
TRANSMIT_REMOTE_DIRECTORY = os.environ.get(
    'TRANSMIT_REMOTE_DIRECTORY',
    './data/test-deploy'
        if TRANSMIT_TEST_MODE_ENABLED else
        '/opt/starsweep.space/data/raw/'
)


# Downlink Settings

DOWNLINK_CONFIG_EXPIRY = timedelta(
    seconds=int(os.environ.get('DOWNLINK_CONFIG_EXPIRY_SECONDS', '30'))
)
DOWNLINK_CONFIGURATION_URL = os.environ.get(
    'DOWNLINK_CONFIGURATION_URL',
    urllib.parse.urljoin(HOME_URL, '/config/configuration.json'),
)
DOWNLINK_CONFIGURATION_PATH = os.environ.get(
    'DOWNLINK_CONFIGURATION_PATH',
    os.path.join(BASE_DIR, './data/config'),
)
DOWNLINK_CONFIGURATION_FILE = os.environ.get(
    'DOWNLINK_CONFIGURATION_FILE',
    os.path.join(DOWNLINK_CONFIGURATION_PATH, 'configuration.json'),
)
DOWNLINK_STATUS_PIN = int(os.environ.get(
    'DOWNLINK_STATUS_PIN',
    11,
))


class Wait:
    device = 5
    processing = 0.5
    background = 5


# Test Rig

TEST_SOCKET_HOST = ''
TEST_SOCKET_SEND_PORT = 50008
TEST_SOCKET_RECV_PORT = 50007
