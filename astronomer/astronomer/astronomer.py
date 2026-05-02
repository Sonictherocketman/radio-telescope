import argparse
import logging
from multiprocessing import Manager, Pool, get_logger
import sys
import time

from . import settings


logger = get_logger()


def _configure_logger(log_level):
    formatter = logging.Formatter(fmt='%(asctime)s [%(levelname)s]: %(message)s')
    worker_logger = get_logger()
    if not worker_logger.handlers:
        file_handler = logging.FileHandler('astronomer.log')
        file_handler.setFormatter(formatter)
        worker_logger.addHandler(file_handler)
        stream_handler = logging.StreamHandler(sys.stdout)
        stream_handler.setFormatter(formatter)
        worker_logger.addHandler(stream_handler)
    worker_logger.setLevel(log_level)


def get_child_exception_logger(prefix: str):
    return lambda e: logger.error(f'[{prefix}] Child exception detected: {e}')


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

    _configure_logger(args.log_level)
    logger.propagate = True

    # Kick off children

    with Manager() as manager, Pool(7, initializer=_configure_logger, initargs=(args.log_level,)) as pool:
        logger.debug('Configuring shared state...')
        event_queue = manager.Queue()
        should_calibrate = manager.Event()
        should_observe = manager.Event()

        results = []

        logger.info('Starting child processes...')
        from .workers.io import handle_io
        results.append(pool.apply_async(
            handle_io,
            args=(event_queue, should_calibrate, should_observe),
            error_callback=get_child_exception_logger('I/O'),
        ))
        from .workers.watch_sky import watch_sky
        results.append(pool.apply_async(
            watch_sky,
            args=(event_queue, should_calibrate, should_observe),
            error_callback=get_child_exception_logger('WatchSky'),
        ))
        from .workers.spectrum import analyze_spectra
        results.append(pool.apply_async(
            analyze_spectra,
            args=(event_queue,),
            error_callback=get_child_exception_logger('Spectra'),
        ))
        from .workers.downlink import downlink
        results.append(pool.apply_async(
            downlink,
            args=(event_queue,),
            error_callback=get_child_exception_logger('Downlink'),
        ))
        from .workers.transmit import transmit
        results.append(pool.apply_async(
            transmit,
            args=(event_queue,),
            error_callback=get_child_exception_logger('Transmit'),
        ))

        try:
            while not any(result.ready() for result in results):
                time.sleep(settings.Wait.background)
        finally:
            # Terminate and other stuff is called by the pool.
            pass

        logger.error('Process error with unknown child.')
