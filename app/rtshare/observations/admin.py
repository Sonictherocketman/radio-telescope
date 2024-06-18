from django.contrib import admin

from .models import Observation, Configuration, Sample


@admin.register(Observation)
class ObservationAdmin(admin.ModelAdmin):

    list_display = (
        'id',
        'name',
        'created_at',
        'updated_at',
    )

    readonly_fields = (
        'uuid',
        'created_at',
        'updated_at',
    )

    list_filter = (
        'telescopes',
    )

    search_fields = (
        'name',
    )


@admin.register(Sample)
class SampleAdmin(admin.ModelAdmin):

    list_display = (
        'id',
        'observation',
        'created_at',
        'updated_at',
    )

    readonly_fields = (
        'uuid',
        'created_at',
        'updated_at',
    )

    search_fields = (
        'observation__name',
    )


@admin.register(Configuration)
class ConfigurationAdmin(admin.ModelAdmin):

    list_display = (
        'id',
        'observation',
        'processing_state',
        'created_at',
        'updated_at',
    )

    readonly_fields = (
        'uuid',
        'created_at',
        'updated_at',
    )

    search_fields = (
        'observation__name',
    )

    list_filter = (
        'processing_state',
    )
