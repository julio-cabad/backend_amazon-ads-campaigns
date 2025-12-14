"""
Campaigns app configuration.
"""
from django.apps import AppConfig


class CampaignsConfig(AppConfig):
    """Configuration for the campaigns application."""

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.campaigns'
    verbose_name = 'Campaigns'

    def ready(self):
        """Import signals when the app is ready."""
        pass  # No signals needed for now
