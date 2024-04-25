from django.contrib import admin

from .models import Telescope, Observation, Token, Configuration, Sample


@admin.register(Telescope)
class TelescopeAdmin(admin.ModelAdmin):

    list_display = (
        'id',
        'name',
        'status',
        'state',
        'created_at',
        'updated_at',
    )

    readonly_fields = (
        'uuid',
        'created_at',
        'updated_at',
    )

    list_filter = (
        'status',
        'state',
    )

    search_fields = (
        'name',
        'description',
    )


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


@admin.register(Token)
class TokenAdmin(admin.ModelAdmin):

    list_display = (
        'id',
        'key',
        'created_at',
        'updated_at',
    )

    readonly_fields = (
        'uuid',
        'key',
        'created_at',
        'updated_at',
    )

    search_fields = (
        'telescope__name',
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


