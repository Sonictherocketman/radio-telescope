import uuid

from django.db import models
from django.utils import timezone
from django.db.models.signals import pre_save
from django.dispatch import receiver


class AuditableModelMixin(models.Model):
    created_at = models.DateTimeField(
        default=timezone.now,
        help_text=(
            'The exact time when a record was created.'
        ),
    )
    updated_at = models.DateTimeField(
        default=timezone.now,
        help_text=(
            'The exact time when a record was last updated.'
        ),
    )

    class Meta:
        abstract = True


@receiver(pre_save)
def update_auditable_record(sender, instance, *args, **kwargs):
    """ Anytime an instance of any AuditableModel is about to be saved, we
    need to update the `updated_at` field with the current time information.
    """
    if issubclass(sender, AuditableModelMixin):
        instance.updated_at = timezone.now()


class BaseModel(AuditableModelMixin, models.Model):
    """ The base model that adds core internal/external ID/UUIDs as well
    as auditing to all models that inherit from it.
    """
    id = models.BigAutoField(primary_key=True)
    uuid = models.UUIDField(
        default=uuid.uuid4,
        unique=True,
        help_text=(
            'The unique identifier for this record.'
        ),
    )

    class Meta:
        abstract = True

    def __repr__(self):
        if BaseModel.__str__(self) != self.__str__():
            return f'<{self.__class__.__name__}: {str(self)}>'
        return f'<{self.__class__.__name__}>'
