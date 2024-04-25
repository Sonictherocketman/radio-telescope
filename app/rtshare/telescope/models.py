import binascii
from datetime import timedelta
import os

from django.conf import settings
from django.core.validators import MaxValueValidator
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from rtshare.utils.models import BaseModel


class Token(BaseModel):

    telescope = models.OneToOneField(
        'telescope.Telescope',
        on_delete=models.CASCADE,
    )

    key = models.CharField(
        max_length=40,
        unique=True,
        blank=True,
    )

    def save(self, *args, **kwargs):
        if not self.key:
            self.key = self.generate_key()
        return super().save(*args, **kwargs)

    @classmethod
    def generate_key(cls):
        return binascii.hexlify(os.urandom(20)).decode()

    def __str__(self):
        return self.key

    class Meta:
        ordering = ('-id',)


class Sample(BaseModel):

    observation = models.ForeignKey(
        'telescope.Observation',
        related_name='samples',
        on_delete=models.CASCADE,
    )

    data = models.FileField(
        upload_to='samples/%Y/%m/'
    )

    class Meta:
        ordering = ('-id',)


class Configuration(BaseModel):

    name = models.CharField(
        max_length=256,
        help_text=(
            'The human-recognizable name for the observation configuration.'
        )
    )

    observation = models.ForeignKey(
        'telescope.Observation',
        related_name='configurations',
        on_delete=models.CASCADE,
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

    hz_conversion = (
        ('Hz', 1),
        ('KHz', 1_000),
        ('MHz', 1_000_000),
        ('GHz', 1_000_000_000),
    )

    @property
    def hz(self):
        unit, value = sorted([
            (unit, (self.frequency / mod))
            for unit, mod in self.hz_conversion
            if mod >= 1
        ], reverse=True)[0]
        return f'{value}{unit}'


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


class Telescope(BaseModel):

    class Status:
        ACTIVE = 'active'
        INACTIVE = 'inactive'

        choices = (
            (ACTIVE, 'Active'),
            (INACTIVE, 'Inactive'),
        )

    class State:
        ONLINE = 'online'
        OFFLINE = 'offline'

        choices = (
            (ONLINE, 'Online'),
            (OFFLINE, 'Offline'),
        )

    name = models.CharField(
        max_length=256,
        help_text=(
            'The human-recognizable name for the device.'
        )
    )

    description = models.TextField(
        default='',
        blank=True,
        help_text=(
            'Any helpful text for the user of this device.'
        )
    )

    latitude = models.DecimalField(
        max_digits=20,
        decimal_places=17,
        blank=True,
        null=True,
        default=None,
        help_text=(
            'The device\'s current latitude.'
        )
    )

    longitude = models.DecimalField(
        max_digits=20,
        decimal_places=17,
        blank=True,
        null=True,
        default=None,
        help_text=(
            'The device\'s current longitude.'
        )
    )

    elevation = models.IntegerField(
        default=0,
        help_text=(
            'The device\'s current elevation above sea level.'
        )
    )

    status = models.CharField(
        max_length=30,
        choices=Status.choices,
        default=Status.INACTIVE,
        help_text=(
            'The status of the device and whether it is actively being used.'
        )
    )

    state = models.CharField(
        max_length=30,
        choices=State.choices,
        default=State.OFFLINE,
        help_text=(
            'The current state of the device as reported by that device.'
        )
    )

    state_updated_at = models.DateTimeField(
        default=None,
        blank=True,
        null=True,
        help_text=(
            'The exact time when the state was last updated.'
        ),
    )

    class Meta:
        ordering = ('-created_at',)

    def __str__(self):
        return f'{self.name} ({self.id})'

    @property
    def public_id(self):
        return f'TEL-{self.id}'

    @property
    def current_location(self):
        return self.latitude, self.longitude

    @property
    def is_active(self):
        return self.status == self.Status.ACTIVE

    @property
    def is_online(self):
        return self.state == self.State.ONLINE

    @property
    def recent_observations(self):
        threshold = timezone.now() - timedelta(days=7)
        return self.observations.filter(start_at__gte=threshold, end_at__lte=timezone.now())

    @property
    def last_upload_at(self):
        qs = Sample.objects.filter(
            observation__in=self.observations.all()
        ).order_by('-id').first()

        if sample := qs:
            return sample.created_at

    @property
    def tasks(self):
        yesterday = timezone.now() - timedelta(days=1)
        return (
            Configuration.objects
            .filter(observation__telescopes=self)
            .filter(observation__end_at__gte=yesterday)
        )
