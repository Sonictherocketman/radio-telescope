import binascii
from datetime import timedelta
import os

from django.conf import settings
from django.core.files.storage import storages
from django.core.validators import MaxValueValidator
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from rtshare.utils.models import BaseModel


def get_storage():
    return (
        storages['default']
        if settings.DEBUG else
        storages['remote']
    )


class ConfigurationSummaryResult(BaseModel):

    telescope = models.ForeignKey(
        'telescope.Telescope',
        related_name='summary_results',
        on_delete=models.SET_NULL,
        default=None,
        null=True,
        blank=True,
    )

    configuration = models.ForeignKey(
        'observations.Configuration',
        related_name='summary_results',
        on_delete=models.SET_NULL,
        default=None,
        null=True,
        blank=True,
    )

    fft_video_file = models.FileField(
        storage=get_storage(),
        upload_to='starsweep/results/'
    )

    spectrum_video_file = models.FileField(
        storage=get_storage(),
        upload_to='starsweep/results/'
    )

    class Meta:
        ordering = ('-id',)
