"""
Integration tests for Campaign API.
"""
import pytest
from django.urls import reverse
from rest_framework import status

from apps.campaigns.domain.models import CampaignStatus


@pytest.mark.django_db
class TestCampaignAPI:

    def test_list_campaigns(self, api_client, campaign_factory):
        """Test listing campaigns."""
        campaign_factory(name="C1")
        campaign_factory(name="C2")
        
        url = reverse('campaign-list')
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 2

    def test_create_campaign(self, api_client):
        """Test creating a campaign via API."""
        url = reverse('campaign-list')
        data = {
            "name": "API Test",
            "budget": "150.00",
            "keywords": ["api", "integration"]
        }
        
        response = api_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['name'] == "API Test"
        assert response.data['status'] == CampaignStatus.PENDING

    def test_retrieve_campaign(self, api_client, campaign_factory):
        """Test retrieving a single campaign."""
        campaign = campaign_factory(name="Detail Test")
        
        url = reverse('campaign-detail', args=[campaign.id])
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['name'] == "Detail Test"

    def test_filter_campaigns(self, api_client, campaign_factory):
        """Test filtering campaigns by status."""
        campaign_factory(name="Active Camp", status=CampaignStatus.ACTIVE)
        campaign_factory(name="Pending Camp", status=CampaignStatus.PENDING)
        
        url = reverse('campaign-list')
        response = api_client.get(url, {'status': 'ACTIVE'})
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 1
        assert response.data['results'][0]['status'] == CampaignStatus.ACTIVE
