import os
import os.path
import urllib.parse


# General Settings

USER_AGENT = 'astronomer/1.0'
DEFAULT_REQUEST_TIMEOUT = 15
DATABASE_LOCATION = os.path.expanduser(os.environ.get(
    'DATABASE_LOCATION',
    './db.sqlite',
))

TELESCOPE_ID = os.environ['TELESCOPE_ID']

# Capture Settings

CAPTURE_TEST_CENTER_FREQUENCY = int(os.environ.get(
    'CAPTURE_TEST_CENTER_FREQUENCY',
    89_500_000,
))
CAPTURE_DATA_PATH = os.path.expanduser(os.environ.get(
    'DATA_PATH',
    './data',
))

CAPTURE_STATUS_PIN = int(os.environ.get(
    'CAPTURE_STATUS_PIN',
    24,
))

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
DOWNLINK_EVENT_STREAM_TIMEOUT = 60 * 60 * 3  # 3 hours
DOWNLINK_RECONNECT_SECONDS = 10

DOWNLINK_STATUS_PIN = int(os.environ.get(
    'DOWNLINK_STATUS_PIN',
    11,
))

# Lackey Configuration Settings

# STEP_ANGLE =
STEP_DURATION_SECONDS = 10
