import os
import os.path
import urllib.parse


# General Settings

USER_AGENT = 'astronomer/1.0'
DEFAULT_REQUEST_TIMEOUT = 15

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


# Phone Home Settings

HOME_URL = os.environ['HOME_URL']
HOME_AUTHORIZATION_TOKEN = os.environ['HOME_AUTHORIZATION_TOKEN']
HOME_API_HEALTH_CHECK_URL = os.environ.get(
    'HOME_API_HEALTH_CHECK_URL',
    urllib.parse.urljoin(HOME_URL, '/health-check'),
)
HOME_API_LAST_ENTRY_URL = os.environ.get(
    'HOME_API_LAST_ENTRY_URL',
    urllib.parse.urljoin(HOME_URL, '/last-entry'),
)
HOME_API_TRANSMIT_URL = os.environ.get(
    'HOME_API_TRANSMIT_URL',
    urllib.parse.urljoin(HOME_URL, '/transmit'),
)
TRANSMIT_WAIT_SECONDS = 60
TRANSMIT_BATCH_SIZE = 1_000

# Lackey Configuration Settings

# STEP_ANGLE =
STEP_DURATION_SECONDS = 0.25
