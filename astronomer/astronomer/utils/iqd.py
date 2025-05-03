import base64
import json
import os
import os.path
from typing import List, Optional

import numpy as np

from ..models.observation import Observation


def write_config(path, observation: Observation):
    with open(path, 'w') as f:
        json.dump(observation.meta, f, indent=2)


def read(config_path, sig_ext='.iq', cal_ext='.ciq'):
    with open(config_path, 'r') as f:
        config = json.load(f)

    if 'calibration' in config:
        calibration = Observation(**config['calibration'])
        del config['calibration']
    else:
        calibration = None

    observation = Observation(**config, calibration=calibration)

    directory = os.path.dirname(config_path)
    name, _ = os.path.splitext(os.path.basename(config_path))

    def _get_signal():
        signal_path = os.path.join(directory, f'{name}{sig_ext}')
        return (
            np.fromfile(signal_path, np.int16)
            .astype(np.float32)
            .view(np.complex64)
        )

    def _get_csignal():
        calibration_path = os.path.join(directory, f'{name}{cal_ext}')
        if os.path.exists(calibration_path):
            return (
                np.fromfile(calibration_path, np.int16)
                .astype(np.float32)
                .view(np.complex64)
            )
        else:
            return None

    return observation, _get_signal, _get_csignal


def remove(config_path, sig_ext='.iq', cal_ext='.ciq'):
    directory = os.path.dirname(config_path)
    name, _ = os.path.splitext(os.path.basename(config_path))
    signal_path = os.path.join(directory, f'{name}{sig_ext}')
    os.remove(signal_path)

    calibration_path = os.path.join(directory, f'{name}{cal_ext}')
    if os.path.exists(calibration_path):
        os.remove(calibration_path)

    os.remove(config_path)
