from django.contrib import admin

from .models import Telescope, Token


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
