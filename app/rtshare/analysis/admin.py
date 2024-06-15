from django.contrib import admin

from .models import ConfigurationSummaryResult


@admin.register(ConfigurationSummaryResult)
class ConfigurationSummaryResultAdmin(admin.ModelAdmin):

    list_display = (
        'id',
        'configuration',
        'created_at',
        'updated_at',
    )

    readonly_fields = (
        'uuid',
        'created_at',
        'updated_at',
    )

    list_filter = (
        'telescope',
        'configuration',
    )
