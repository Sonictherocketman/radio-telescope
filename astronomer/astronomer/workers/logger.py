import logging
import sys


logger = logging.getLogger('astronomer.worker')


def log_events(log, log_level):
    """ Log events from other workers """
    logging.basicConfig(
        format='%(asctime)s [%(levelname)s]: %(message)s',
        encoding='utf-8',
        handlers=(
            logging.FileHandler('astronomer.log'),
            logging.StreamHandler(sys.stdout)
        ),
        level=log_level,
    )

    logger.info('[Log Worker] Listening...')
    while True:
        try:
            level, message = log.get()
            getattr(logger, level)(message)
        except Exception as e:
            logger.error(f'[Log Worker] Unexpected exception: {e}')

