from datetime import datetime
import os
import time
import shutil
import tempfile

import numpy as np
from matplotlib import pyplot as plt
from matplotlib import mlab

from .. import settings
from ..utils import iqd
from ..models.lights import StatusLight
from ..models.buffer import FixedBuffer
from ..mpsafe import managed_status


cache = {}
signal_buffer = FixedBuffer(settings.SIGNAL_BUFFER_LENGTH)


def setup(log):
    os.makedirs(settings.CAPTURE_DATA_PATH, exist_ok=True)
    os.makedirs(settings.SPECTRUM_DATA_PATH, exist_ok=True)
    return True


def process_spectrum(observation, signal, c_signal, NFFT=1024):
    Fc = observation.frequency / 1e6

    if c_signal is not None:
        pxx, freqs = mlab.csd(
            signal,
            c_signal,
            NFFT=1024,
            Fs=observation.sample_rate/1e6,
        )
        freqs += Fc
    else:
        pxx, freqs = mlab.psd(
            signal,
            NFFT=1024,
            Fs=observation.sample_rate/1e6,
        )

    return pxx, freqs


def plot_to_image(log, values, freq, observation, buff_percent):
    with tempfile.NamedTemporaryFile('wb+', suffix='.png') as f:
        log.put(('debug', f'Using NTF: {f.name}'))

        # TODO: Temp hack to remove DC offset spike
        l = len(values)
        center = l // 2
        width = 4
        values[center-width:center+width] = values[center-width:center+width] / (signal_buffer.length * 10)
        # END HACK

        title = observation.identifier
        if observation.calibration:
            title += ' (Calibrated)'
        title += f' (Buffer {int(buff_percent*100)}%)'

        plt.title(title)
        plt.plot(freq, values)
        plt.xlabel('Frequency (MHz)')
        plt.ylabel('Relative power (dB)')
        plt.savefig(f.name)
        plt.close()
        f.seek(0)
        return f.file.read()


def write_spectrum(
    log,
    observation,
    values,
    c_values,
    freq,
    image,
    output_directory,
):
    image_path = os.path.join(output_directory, f'{observation.identifier}.png')
    with open(image_path, 'wb') as f:
        f.write(image)

    data_path = os.path.join(output_directory, f'{observation.identifier}.dat')
    if c_values is not None:
        data = np.array([freq, values, c_values])
    else:
        data = np.array([freq, values])
    with open(data_path, 'wb') as f:
        f.write(data.tobytes())


def check_observations(
    log,
    event_queue,
    input_directory=settings.CAPTURE_DATA_PATH,
    output_directory=settings.SPECTRUM_DATA_PATH,
    batch_size=settings.SPECTRUM_BATCH_SIZE,
):
    config_files = [
        (os.path.join(input_directory, filename), filename)
        for filename in os.listdir(input_directory)
        if filename.endswith('.json')
    ]

    if not batch_size:
        batch_size = len(config_files)

    for path, filename in config_files[:batch_size]:
        with managed_status(event_queue, StatusLight.analysis):
            log.put(('info', f'Processing {filename}...'))
            try:
                observation, get_signal, get_c_signal = iqd.read(path)
            except Exception as e:
                log.put(('error', f'Unable to fetch data for {filename}. {e=}. Purging.'))
                continue

            log.put(('info', f'Processing {observation.summary}'))

            signal = get_signal()

            if calibration := observation.calibration:
                c_signal = get_c_signal()
            else:
                c_signal = None

            if c_signal and len(c_signal) != len(signal):
                log.put(('warning', f'Signal length differed from calibration length. Skipping...'))
                iqd.remove(path)
                continue

            values, freq = process_spectrum(observation, signal, c_signal)
            signal_buffer.add(values)
            pxx = np.sum(signal_buffer.get_data(), axis=0)

            write_spectrum(
                log,
                observation,
                pxx,
                None,
                freq,
                plot_to_image(log, pxx, freq, observation, signal_buffer.percent_full),
                output_directory,
            )
            config_output_path = os.path.join(output_directory, os.path.basename(path))
            shutil.copyfile(path, config_output_path)
            log.put(('info', f'Finished processing {filename}. Purging.'))
            iqd.remove(path)


def loop(log, event_queue):
    check_observations(log, event_queue)


def analyze_spectra(log, event_queue):
    """ Continuously watch the sky and record values to disk. """
    if setup(log):
        log.put(('info', 'Analyzing spectra...'))
        try:
            while True:
                log.put(('debug', 'Begin spectra iteration...'))
                loop(log, event_queue)
                log.put(('debug', 'End spectra iteration. Sleeping...'))
                time.sleep(settings.Wait.processing)
        except Exception as e:
            log.put(('error', f'Encountered error during analysis. {e}. Exiting...'))
            event_queue.put((StatusLight.analysis, 'flash_error'))
    else:
        log.put(('error', 'Setup failed. Exiting.'))

    log.put(('info', 'Done.'))
