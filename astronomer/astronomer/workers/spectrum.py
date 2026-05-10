from collections import defaultdict
from datetime import datetime
from multiprocessing import get_logger
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
from ..models.observation import BufferStatus, SpectrumObservation
from ..mpsafe import managed_status


logger = get_logger()


cache = {}
signal_buffers = defaultdict(lambda: FixedBuffer(settings.SIGNAL_BUFFER_LENGTH))
default_identifier = 'default'


def setup():
    os.makedirs(settings.CAPTURE_DATA_PATH, exist_ok=True)
    os.makedirs(settings.SPECTRUM_DATA_PATH, exist_ok=True)
    return True


def process_spectrum(observation, signal, c_signal, NFFT=1024, pad=1e6):
    Fc = observation.frequency / pad

    pxx, freqs = mlab.psd(
        signal,
        NFFT=NFFT,
        Fs=observation.sample_rate / pad,
    )
    freqs += Fc
    pxx /= np.max(pxx)

    if c_signal is not None:
        c_pxx, c_freqs = mlab.psd(
            c_signal,
            NFFT=NFFT,
            Fs=observation.sample_rate / pad,
        )
        c_freqs += Fc
        c_pxx /= np.max(c_pxx)

        pxx -= c_pxx
        pxx = np.maximum(pxx, 0)

    return pxx, freqs


def rolling_mean(x, window_length):
    # https://stackoverflow.com/a/22621523/12131013
    return np.convolve(x, np.ones(window_length) / window_length, mode='same')


def plot_to_image(values, freq, observation, buff_percent, y_scale_factor=2):
    with tempfile.NamedTemporaryFile('wb+', suffix='.png') as f:
        logger.debug(f'Using NTF: {f.name}')

        # TODO: Temp hack to remove DC offset spike
#         if observation.calibration:
#             identifier = observation.calibration.identifier
#         else:
#             identifier = default_identifier
#
#         signal_buffer = signal_buffers[identifier]
#         if len(signal_buffer.get_data()) > 1:
#             prevous_values = signal_buffer.get_data()[1]
#             l = len(values)
#             center = l // 2
#             width = 10
#             values[center-width:center+width] = (
#                 values[center-width:center+width]
#                 / (prevous_values[center-width:center+width] * signal_buffer.length)
#             )
        # END HACK

        title = observation.identifier
        if observation.calibration:
            title += ' (Calibrated)'
        title += f' (Buffer {int(buff_percent*100)}%)'

        plt.title(title)
        plt.plot(freq[5:-5], values[5:-5])
        bottom, top = plt.ylim()
        plt.ylim(0, y_scale_factor*max(top, settings.MIN_CHART_Y_SCALE))
        plt.xlabel('Frequency (MHz)')
        plt.ylabel('Relative power (dB)')
        plt.savefig(f.name)
        plt.close()
        f.seek(0)
        return f.file.read()


def write_spectrum(
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
    event_queue,
    input_directory=settings.CAPTURE_DATA_PATH,
    output_directory=settings.SPECTRUM_DATA_PATH,
    batch_size=settings.SPECTRUM_BATCH_SIZE,
    smoothed=settings.SMOOTHING_ENABLED,
    smoothing_window=settings.SMOOTHING_WINDOW_LENGTH,
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
            logger.info(f'Processing {filename}...')
            try:
                observation, get_signal, get_c_signal = iqd.read(path)
            except Exception as e:
                logger.error(f'Unable to fetch data for {filename}. {e=}. Purging.')
                iqd.remove(path)
                continue

            logger.info(f'Processing {observation.summary}')

            signal = get_signal()

            if calibration := observation.calibration:
                c_signal = get_c_signal()
                c_identifier = observation.calibration.identifier
            else:
                c_signal = None
                c_identifier = default_identifier

            if c_signal is not None and len(c_signal) != len(signal):
                logger.warning(f'Signal length differed from calibration length. Skipping...')
                iqd.remove(path)
                continue

            values, freq = process_spectrum(observation, signal, c_signal)

            signal_buffer = signal_buffers[c_identifier]
            signal_buffer.add(values)

            pxx = np.sum(signal_buffer.get_data(), axis=0)
            if smoothed:
                pxx = rolling_mean(pxx, smoothing_window)

            write_spectrum(
                observation,
                pxx,
                None,
                freq,
                plot_to_image(pxx, freq, observation, signal_buffer.percent_full),
                output_directory,
            )

            # Add spectrum analysis info to the observation meta and persist
            config_output_path = os.path.join(output_directory, os.path.basename(path))
            buffered_observation = SpectrumObservation(
                **observation.meta,
                buffer_status=BufferStatus(signal_buffer.percent_full)
            )

            # Write to tempfile then mv so the action is atomic.
            # Actions are taken on this file so it needs to be 100% valid
            # as soon as it exists.
            tmp_file = f'{config_output_path}.tmp'
            iqd.write_config(tmp_file, buffered_observation)
            shutil.move(tmp_file, config_output_path)
            logger.info(f'Finished processing {filename}. Purging.')
            iqd.remove(path)


def loop(event_queue):
    check_observations(event_queue)


def analyze_spectra(event_queue):
    """ Continuously watch the sky and record values to disk. """
    if setup():
        logger.info('Analyzing spectra...')
        logger.info(f'[Spectra] pid: {os.getpid()} [P: {os.getppid()}]')
        try:
            while True:
                logger.debug('Begin spectra iteration...')
                loop(event_queue)
                logger.debug('End spectra iteration. Sleeping...')
                time.sleep(settings.Wait.processing)
        except Exception as e:
            logger.error(f'Encountered error during analysis. {e}. Exiting...')
            event_queue.put(('light', StatusLight.analysis, 'flash_error'))
    else:
        logger.error('Setup failed. Exiting.')

    logger.info('Done.')
