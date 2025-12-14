"""
Admin configuration for the Campaigns app.
"""
from django.contrib import admin

from .domain.models import Campaign


@admin.register(Campaign)
class CampaignAdmin(admin.ModelAdmin):
    """Admin configuration for Campaign model."""

    list_display = [
        'id',
        'name',
        'status',
        'budget',
        'external_id',
        'retry_count',
        'created_at',
    ]
    list_filter = ['status', 'created_at']
    search_fields = ['name', 'external_id']
    readonly_fields = ['id', 'external_id', 'created_at', 'updated_at', 'synced_at']
    ordering = ['-created_at']

    fieldsets = (
        ('Basic Information', {
            'fields': ('id', 'name', 'budget', 'keywords'),
        }),
        ('Status', {
            'fields': ('status', 'external_id', 'error_message', 'retry_count'),
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'synced_at'),
            'classes': ('collapse',),
        }),
    )
