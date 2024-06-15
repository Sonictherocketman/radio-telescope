import binascii
from datetime import timedelta
import os

from django.conf import settings
from django.core.files.storage import storages
from django.core.validators import MaxValueValidator
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from observations.models import Sample
from rtshare.utils.models import BaseModel


def get_storage():
    return (
        storages['default']
        if settings.DEBUG else
        storages['remote']
    )


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
