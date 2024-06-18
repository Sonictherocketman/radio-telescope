from django.conf import settings
from django.core.files.storage import storages
from django.db import models

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
        upload_to='starsweep/results/',
        default=None,
        null=True,
        blank=True,
    )

    spectrum_video_file = models.FileField(
        storage=get_storage(),
        upload_to='starsweep/results/',
        default=None,
        null=True,
        blank=True,
    )

    class Meta:
        ordering = ('-id',)
