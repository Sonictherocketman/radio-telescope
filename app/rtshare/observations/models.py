from datetime import timedelta

from django.conf import settings
from django.core.files.storage import storages
from django.core.validators import MaxValueValidator
from django.db import models
from django.utils import timezone

from rtshare.utils.models import BaseModel
from rtshare.utils.units import display_hz


def get_storage():
    return (
        storages['default']
        if settings.DEBUG else
        storages['remote']
    )


class Sample(BaseModel):

    observation = models.ForeignKey(
        'observations.Observation',
        related_name='samples',
        on_delete=models.CASCADE,
    )

    telescope = models.ForeignKey(
        'telescope.Telescope',
        related_name='samples',
        on_delete=models.SET_NULL,
        default=None,
        null=True,
        blank=True,
    )

    configuration = models.ForeignKey(
        'observations.Configuration',
        related_name='samples',
        on_delete=models.SET_NULL,
        default=None,
        null=True,
        blank=True,
    )

    frequency = models.PositiveBigIntegerField(
        default=None,
        null=True,
        blank=True,
        help_text=(
            'The center frequency that was captured (in Hz).'
        )
    )

    sample_rate = models.PositiveBigIntegerField(
        default=None,
        null=True,
        blank=True,
        help_text=(
            'The sample rate at which data was collected.'
        )
    )

    sample_size = models.PositiveBigIntegerField(
        default=None,
        null=True,
        blank=True,
        help_text=(
            'The number of samples in the record.'
        )
    )

    ppm = models.PositiveSmallIntegerField(
        default=None,
        null=True,
        blank=True,
        help_text=(
            'The PPM offset used for the device (0 is none).'
        )
    )

    gain = models.PositiveSmallIntegerField(
        default=None,
        null=True,
        blank=True,
        validators=[
            MaxValueValidator(100),
        ],
        help_text=(
            'The amount of gain applied to the SDR.'
        )
    )

    captured_at = models.DateTimeField(
        default=None,
        null=True,
        blank=True,
        help_text=(
            'The timestamp when the data was collected.'
        )
    )

    data = models.FileField(
        storage=get_storage(),
        upload_to='starsweep/data/'
    )

    class Meta:
        ordering = ('-id',)


class Configuration(BaseModel):

    class ProcessingState:
        IN_PROGRESS = 'in-progress'
        ERROR = 'error'
        COMPLETE = 'complete'

        choices = (
            (IN_PROGRESS, 'In Progress'),
            (ERROR, 'Error'),
            (COMPLETE, 'Complete'),
        )

    name = models.CharField(
        max_length=256,
        help_text=(
            'The human-recognizable name for the observation configuration.'
        )
    )

    observation = models.ForeignKey(
        'observations.Observation',
        related_name='configurations',
        on_delete=models.CASCADE,
    )

    processing_state = models.CharField(
        max_length=12,
        choices=ProcessingState.choices,
        blank=True,
        null=True,
        help_text=(
            'The current state of the analysis for this configuration data.'
        )
    )

    frequency = models.PositiveBigIntegerField(
        default=89_500_000,
        help_text=(
            'The center frequency to capture (in Hz).'
        )
    )

    sample_rate = models.PositiveBigIntegerField(
        default=2_048_000,
        help_text=(
            'The sample rate at which to collect data.'
        )
    )

    sample_size = models.PositiveBigIntegerField(
        default=1_024,
        help_text=(
            'How many data points to collect per sample.'
        )
    )

    ppm = models.PositiveSmallIntegerField(
        default=0,
        help_text=(
            'What PPM offset to use for the device (0 is none).'
        )
    )

    gain = models.PositiveSmallIntegerField(
        default=0,
        validators=[
            MaxValueValidator(100),
        ],
        help_text=(
            'The amount of gain to apply via the SDR.'
        )
    )

    class Meta:
        ordering = ('-id',)

    def get_identifier(self, telescope):
        return f'{telescope.id}-{self.observation.id}-{self.id}'

    def parse_identifier(self, identifier):
        return identifier.split('-')

    @property
    def hz(self):
        return display_hz(self.frequency)

    def is_complete(self):
        return self.processing_state == self.ProcessingState.COMPLETE

    def is_error(self):
        return self.processing_state == self.ProcessingState.ERROR


class Observation(BaseModel):

    name = models.CharField(
        max_length=256,
        help_text=(
            'The human-recognizable name for the device.'
        )
    )

    telescopes = models.ManyToManyField(
        'telescope.Telescope',
        related_name='observations',
        help_text=(
            'The telescopes that are involved in the observation and collection of data.'
        )
    )

    # Observation Configuration Fields

    start_at = models.DateTimeField(
        blank=True,
        null=True,
        help_text=(
            'When the given observation should begin?'
        )
    )

    end_at = models.DateTimeField(
        blank=True,
        null=True,
        help_text=(
            'When the given observation should begin?'
        )
    )

#     azimuth_degrees = models.DecimalField(
#         max_digits=8,
#         decimal_places=5,
#         blank=True,
#         null=True,
#         default=None,
#     )
#
#     elevation_degrees = models.DecimalField(
#         max_digits=8,
#         decimal_places=5,
#         blank=True,
#         null=True,
#         default=None,
#     )
#
#     right_ascention_degrees = models.DecimalField(
#         max_digits=10,
#         decimal_places=7,
#         blank=True,
#         null=True,
#         default=None,
#     )
#
#     declination_degrees = models.DecimalField(
#         max_digits=10,
#         decimal_places=7,
#         blank=True,
#         null=True,
#         default=None,
#     )

    class Meta:
        ordering = ('-start_at', '-end_at')

#     @property
#     def is_celestial(self):
#         return self.right_ascention_degrees and self.declination_degrees
#
#     @property
#     def is_local(self):
#         return self.azimuth_degrees and self.elevation_degrees

    @property
    def recent_samples(self):
        threshold = timezone.now() - timedelta(days=7)
        return self.samples.filter(created_at__gte=threshold)

    @property
    def last_upload_at(self):
        if sample := self.samples.order_by('-id').first():
            return sample.created_at

    @property
    def is_valid(self):
        return self.start_at and self.end_at

    @property
    def is_in_progress(self):
        if self.is_valid:
            now = timezone.now()
            return now > self.start_at and now <= self.end_at

    @property
    def is_complete(self):
        if self.is_valid:
            now = timezone.now()
            return now > self.end_at

    @property
    def is_pending(self):
        if self.is_valid:
            now = timezone.now()
            return now < self.start_at

    @property
    def is_sharing(self):
        other_concurrent_observations = Observation.objects.filter(
            start_at__lte=self.end_at,
            end_at__gte=self.start_at,
            telescopes__in=self.telescopes.all()
        ).exclude(id=self.id)
        return other_concurrent_observations.exists()
