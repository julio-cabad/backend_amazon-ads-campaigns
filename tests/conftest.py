"""
Pytest configuration and fixtures.
"""
import pytest
from rest_framework.test import APIClient

from apps.campaigns.domain.models import Campaign, CampaignStatus


@pytest.fixture
def api_client():
    """Fixture for APIClient."""
    return APIClient()


@pytest.fixture
def campaign_factory(db):
    """Fixture to create campaigns easily."""
    def create_campaign(**kwargs):
        defaults = {
            'name': 'Test Campaign',
            'budget': 100.00,
            'keywords': ['test', 'keyword'],
            'status': CampaignStatus.PENDING,
        }
        defaults.update(kwargs)
        return Campaign.objects.create(**defaults)
    return create_campaign
