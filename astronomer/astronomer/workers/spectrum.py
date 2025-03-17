from datetime import datetime
import os
import time
import pickle
import tempfile

from matplotlib import pyplot as plt

from .. import settings
from ..utils import iqdp


cache = {}


def setup(log):
    os.makedirs(settings.CAPTURE_DATA_PATH, exist_ok=True)
    os.makedirs(settings.SPECTRUM_DATA_PATH, exist_ok=True)
    return True


def process_spectrum(observation, NFFT=1024):
    values = plt.psd(
        observation.signal,
        NFFT=1024,
        Fs=observation.sample_rate/1e6,
        Fc=observation.frequency/1e6
    )
    plt.close()
    return values


def plot_to_image(log, values, freq, observation):
    with tempfile.NamedTemporaryFile('wb+', suffix='.png') as f:
        log.put(('debug', f'Using NTF: {f.name}'))
        plt.title(observation.identifier)
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
    cvalues,
    freq,
    image,
    output_directory,
):
    image_path = os.path.join(output_directory, f'{observation.identifier}.png')
    with open(image_path, 'wb') as f:
        f.write(image)
    # TODO: write data




def check_calibration(
    log,
    input_directory=settings.CALIBRATION_PATH,
    output_directory=settings.CALIBRATION_PATH,
):
    check_observations(
        log,
        input_directory=input_directory,
        output_directory=output_directory,
        batch_size=1,
    )


def check_observations(
    log,
    input_directory=settings.CAPTURE_DATA_PATH,
    output_directory=settings.SPECTRUM_DATA_PATH,
    batch_size=settings.SPECTRUM_BATCH_SIZE,
):
    files = [
        (os.path.join(input_directory, filename), filename)
        for filename in os.listdir(input_directory)
        if filename.endswith('.iqdp')
    ]

    if not batch_size:
        batch_size = len(files)

    for path, filename in files[:batch_size]:
        log.put(('info', f'Processing {filename}...'))
        try:
            observation = iqdp.read(path)
        except pickle.PickleError as e:
            log.put(('error', 'Unable to unpickle {filename}. Purging.'))
            os.remove(path)
            continue

        values, freq = process_spectrum(observation)

        if calibration := observation.calibration:
            if calibration.identifier not in cache:
                log.put(('info', f'Processing uncached calibration: {calibration.identifier}'))
                cache[calibration.identifier] = process_spectrum(calibration)

            cvalues, _ = cache[calibration.identifier]
            # Subtract out the values for the calibration.
            values -= cvalues
        else:
            cvalues = []

        write_spectrum(
            log,
            observation,
            values,
            cvalues,
            freq,
            plot_to_image(log, values, freq, observation),
            output_directory,
        )
        log.put(('info', f'Finished processing {filename}. Purging.'))
        os.remove(path)


def loop(log):
    check_observations(log)


def analyze_spectra(log, *args):
    """ Continuously watch the sky and record values to disk. """
    if setup(log):
        log.put(('info', 'Analyzing spectra...'))
        try:
            while True:
                log.put(('debug', 'Begin spectra iteration...'))
                loop(log)
                log.put(('debug', 'End spectra iteration. Sleeping...'))
                time.sleep(settings.STEP_DURATION_SECONDS)
        except Exception as e:
            log.put(('error', f'Encountered error during analysis. {e}. Exiting...'))
    else:
        log.put(('error', 'Setup failed. Exiting.'))

    log.put(('info', 'Done.'))
