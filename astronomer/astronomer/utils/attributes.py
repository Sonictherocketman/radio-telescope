from datetime import datetime
import json
from multiprocessing import get_logger

from .. import settings


logger = get_logger()


def is_relevant(observation_entry):
    now, start, end = (
        datetime.utcnow(),
        datetime.fromisoformat(observation_entry['start']),
        datetime.fromisoformat(observation_entry['end']),
    )
    return now > start and now <= end


def load_relevant_attributes(
    observation_attributes_config_path=settings.DOWNLINK_CONFIGURATION_FILE,
):
    try:
        with open(observation_attributes_config_path) as f:
            config = json.load(f)

        logger.debug(f'Found config:\n{json.dumps(config, indent=2)}')

        try:
            relevant_observation = next(
                observation
                for observation in config['observations']
                if is_relevant(observation)
            )
        except StopIteration:
            print('[WARNING] No relevant observation found')
            relevant_observation = {}

        return {
            'device-identifier': config['device-identifier'],
            **relevant_observation,
        }
    except Exception as e:
        print(f'[ERROR] failed to load attributes for remote config: {e}')
        return None
