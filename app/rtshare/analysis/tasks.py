from datetime import timedelta
import gzip
import logging
import os.path
import shlex
from subprocess import call
import tempfile
import uuid

from celery import group
from django.core.files import File
from django.utils import timezone
import numpy as np
import matplotlib.pyplot as plt
import scipy.fftpack
import scipy.signal

from rtshare.celery import shared_task, Queue, Priority
from rtshare.utils.iqd import get_data, get_header
from observations.models import Configuration
from .models import ConfigurationSummaryResult


logger = logging.getLogger(__name__)


def get_files(samples, workbench):
    files = []
    for sample in samples:
        logger.debug(f'Copying data for {sample.data} to {workbench}')
        filename = os.path.basename(sample.data.name)
        path = os.path.join(workbench, filename)
        with (
            sample.data.open('rb') as source,
            open(path, 'wb') as destination
        ):
            destination.write(source.read())

        files.append(path)
    return files


def generate_fft(data_file, format='png'):
    with open(data_file, 'rb') as f:
        header = get_header(f)
        data = get_data(f)

    image_file = f'{data_file}.fft.{format}'
    sample_rate = int(header['sample rate'])
    center_f = int(header['frequency'])

    yf = scipy.fftpack.fft([i_q for i_q, _ in data])
    xf = scipy.fftpack.fftfreq(yf.size, 1 / sample_rate)

    yplot = scipy.fftpack.fftshift(yf)
    xplot = scipy.fftpack.fftshift(xf)

    fig, ax = plt.subplots()
    ax.plot(center_f + xplot, 1.0 / yplot.size * np.abs(yplot))
    plt.xlabel('frequency [Hz]')
    plt.ylabel('FFT')
    plt.savefig(image_file)
    return image_file


def generate_spectrum(data_file, format='png'):
    with open(data_file, 'rb') as f:
        header = get_header(f)
        data = get_data(f)

    image_file = f'{data_file}.spectrum.{format}'
    sample_rate = int(header['sample rate'])
    center_f = int(header['frequency'])

    f, S = scipy.signal.periodogram([i_q for i_q, _ in data], sample_rate)

    fig, ax = plt.subplots()
    plt.semilogy(center_f + f, np.sqrt(S))
    plt.xlabel('frequency [Hz]')
    plt.ylabel('PSD')
    plt.savefig(image_file)
    return image_file


def generate_video_from_images(file_pattern, workbench, framerate=5, fps=25, pixfmt='yuv420p'):
    filename = f'{uuid.uuid4()}.mp4'
    command = f"""\
        ffmpeg \
            -framerate {framerate} \
            -pattern_type glob \
            -i '{file_pattern}' \
            -c:v libx264 \
            -vf fps={fps} \
            -pix_fmt {pixfmt}
            {filename}
        """
    call(shlex.split(command), cwd=workbench, timeout=60)
    return filename


@shared_task(queue=Queue.default, priority=Priority.default)
def summarize_observation_configuration(configuration_uuid):
    configuration = Configuration.objects.get(uuid=configuration_uuid)
    samples_by_telescope = {
        telescope.id: configuration.samples.filter(telescope=telescope).order_by('captured_at')
        for telescope in configuration.observation.telescopes.all()
        if configuration.samples.filter(telescope=telescope).exists()
    }

    for telescope_id, samples in samples_by_telescope.items():
        with tempfile.TemporaryDirectory() as workbench:
            logger.info(f'Using workbench: {workbench}')
            files = get_files(samples, workbench)
            ffts = [generate_fft(file) for file in files]
            fft_video_file = generate_video_from_images('*fft.png', workbench)

            spectra = [generate_spectrum(file) for file in files]
            spectrum_video_file = generate_video_from_images('*spectrum.png', workbench)

            result = ConfigurationSummaryResult.objects.create(
                configuration=configuration,
                telescope_id=telescope_id,
            )
            with open(os.path.join(workbench, fft_video_file), 'rb') as f:
                result.fft_video_file.save(
                    fft_video_file,
                    File(f),
                )
            with open(os.path.join(workbench, spectrum_video_file), 'rb') as f:
                result.spectrum_video_file.save(
                    spectrum_video_file,
                    File(f),
                )
            result.save()


@shared_task(queue=Queue.default, priority=Priority.default)
def summarize_completed_observations_if_needed(buffer_hours=1):
    logger.info('Attempting to dispatch tasks for analysis if needed...')
    past_configurations = Configuration.objects.filter(
        observation__end_at__lt=timezone.now() - timedelta(hours=buffer_hours)
    )
    past_configurations_lacking_results = (
        configuration for configuration in past_configurations
        if (
            configuration.samples.exists()
            and not configuration.summary_results.exists()
        )
    )

    workflow = group([
        summarize_observation_configuration.si(configuration.uuid)
        for configuration in past_configurations_lacking_results
    ])
    workflow.delay()