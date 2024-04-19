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

# Capture Settings

CAPTURE_CENTER_FREQUENCY = int(os.environ.get(
    'CAPTURE_CENTER_FREQUENCY',
    89_500_000,
))
CAPTURE_SAMPLE_RATE = int(os.environ.get(
    'CAPTURE_SAMPLE_RATE',
    2_048_000,
))
CAPTURE_SAMPLES_PER_DUMP = int(os.environ.get(
    'CAPTURE_SAMPLES_PER_DUMP',
    1_024,
))
CAPTURE_GAIN = int(os.environ.get(
    'CAPTURE_GAIN',
    0,
))
CAPTURE_PPM = int(os.environ.get(
    'CAPTURE_PPM',
    0,
))
CAPTURE_DATA_PATH = os.path.expanduser(os.environ.get(
    'DATA_PATH',
    './data',
))

# Transmit Settings

HOME_URL = os.environ['HOME_URL']
HOME_AUTHORIZATION_TOKEN = os.environ['HOME_AUTHORIZATION_TOKEN']
HOME_API_HEALTH_CHECK_URL = os.environ.get(
    'HOME_API_HEALTH_CHECK_URL',
    urllib.parse.urljoin(HOME_URL, '/api/telescope/health-check'),
)
HOME_API_TRANSMIT_URL = os.environ.get(
    'HOME_API_TRANSMIT_URL',
    urllib.parse.urljoin(HOME_URL, '/api/telescope/transmit'),
)
TRANSMIT_WAIT_SECONDS = 60
TRANSMIT_BATCH_SIZE = 1_000

# Downlink Settings

DOWNLINK_CONFIGURATION_URL = os.environ.get(
    'DOWNLINK_CONFIGURATION_URL',
    urllib.parse.urljoin(HOME_URL, '/api/telescope/tasks'),
)
DOWNLINK_EVENT_STREAM_URL = os.environ.get(
    'DOWNLINK_EVENT_STREAM_URL',
    urllib.parse.urljoin(HOME_URL, '/api/events'),
)
DOWNLINK_EVENT_STREAM_TIMEOUT = 60 * 60 * 3  # 3 hours
DOWNLINK_RECONNECT_SECONDS = 10

# Lackey Configuration Settings

# STEP_ANGLE =
STEP_DURATION_SECONDS = 0.25
