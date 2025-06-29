import argparse
import logging
from multiprocessing import Manager, Pool
import sys
import time

from . import settings


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
        '-l', '--log-level',
        default=logging.INFO,
        type=str,
        help='The logging level. Options are INFO, DEBUG, WARNING, ERROR.',
    )

    args = parser.parse_args()
    logging.basicConfig(
        format='%(asctime)s [%(levelname)s]: %(message)s',
        encoding='utf-8',
        handlers=(
            logging.FileHandler('astronomer.log'),
            logging.StreamHandler(sys.stdout)
        ),
        level=args.log_level,
    )

    # Kick off children

    with Manager() as manager, Pool(7) as pool:
        logger.debug('Configuring shared state...')
        log_queue = manager.Queue()
        event_queue = manager.Queue()
        should_calibrate = manager.Event()
        should_observe = manager.Event()

        results = []

        logger.info('Starting child processes...')
        from .workers.logger import log_events
        results.append(pool.apply_async(
            log_events,
            args=(log_queue, args.log_level)
        ))
        from .workers.io import handle_io
        results.append(pool.apply_async(
            handle_io,
            args=(log_queue, event_queue, should_calibrate, should_observe)
        ))
        from .workers.watch_sky import watch_sky
        results.append(pool.apply_async(
            watch_sky,
            args=(log_queue, event_queue, should_calibrate, should_observe)
        ))
        from .workers.spectrum import analyze_spectra
        results.append(pool.apply_async(
            analyze_spectra,
            args=(log_queue, event_queue)
        ))
        from .workers.downlink import downlink
        results.append(pool.apply_async(
            downlink,
            args=(log_queue, event_queue)
        ))
        from .workers.transmit import transmit
        transmit(log_queue, event_queue)
#         results.append(pool.apply_async(
#             transmit,
#             args=(log_queue, event_queue)
#         ))

        try:
            while not any(result.ready() for result in results):
                time.sleep(settings.Wait.background)
        finally:
            pool.terminate()

        logger.error('Process error with unknown child.')
