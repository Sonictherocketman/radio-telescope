import argparse
import logging
import sys

from .downlink import downlink
from .transmit import transmit
from .watch_sky import watch_sky


logger = logging.getLogger('astronomer')


def main():
    parser = argparse.ArgumentParser(
        'astronomer',
        description=(
            'Record signals from an SDR-RTL antenna and transmit '
            'them to a remote service.'
        )
    )
    parser.add_argument(
        'mode',
        type=str,
        default='watchsky',
        help='Which mode to run in. Options are watchsky, downlink, and transmit.',
    )
    parser.add_argument(
        '-l', '--log-level',
        default=logging.INFO,
        type=str,
        help='The logging level. Options are INFO, DEBUG, WARNING, ERROR.',
    )

    args = parser.parse_args()

    if args.mode == 'watchsky':
        logging.basicConfig(
            format='%(asctime)s [%(levelname)s]: %(message)s',
            encoding='utf-8',
            handlers=(
                logging.FileHandler('astronomer-watchsky.log'),
                logging.StreamHandler(sys.stdout)
            ),
            level=args.log_level,
        )
        watch_sky()
    elif args.mode == 'transmit':
        logging.basicConfig(
            format='%(asctime)s [%(levelname)s]: %(message)s',
            encoding='utf-8',
            handlers=(
                logging.FileHandler('astronomer-phonehome.log'),
                logging.StreamHandler(sys.stdout)
            ),
            level=args.log_level,
        )
        transmit()
    elif args.mode == 'downlink':
        logging.basicConfig(
            format='%(asctime)s [%(levelname)s]: %(message)s',
            encoding='utf-8',
            handlers=(
                logging.FileHandler('astronomer-downlink.log'),
                logging.StreamHandler(sys.stdout)
            ),
            level=args.log_level,
        )
        downlink()
    else:
        raise ValueError('Invalid mode selected.')
