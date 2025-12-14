"""
Tests for CampaignService.
"""
import pytest
from apps.campaigns.domain.services import CampaignService
from apps.campaigns.domain.models import CampaignStatus


@pytest.mark.django_db
class TestCampaignService:
    
    def test_create_campaign(self):
        """Test creating a campaign via service."""
        campaign = CampaignService.create_campaign(
            name="Service Test",
            budget=50.00,
            keywords=["service", "test"]
        )
        
        assert campaign.name == "Service Test"
        assert campaign.budget == 50.00
        assert campaign.status == CampaignStatus.PENDING
        assert campaign.keywords == ["service", "test"]

    def test_mark_as_processing(self, campaign_factory):
        """Test status transition to PROCESSING."""
        campaign = campaign_factory(status=CampaignStatus.PENDING)
        
        CampaignService.update_campaign_status(
            campaign=campaign,
            new_status="PROCESSING",
            external_id="AMZ-123"
        )
        
        campaign.refresh_from_db()
        assert campaign.status == CampaignStatus.PROCESSING
        assert campaign.external_id == "AMZ-123"

    def test_mark_as_active(self, campaign_factory):
        """Test status transition to ACTIVE."""
        campaign = campaign_factory(
            status=CampaignStatus.PROCESSING,
            external_id="AMZ-123"
        )
        
        CampaignService.update_campaign_status(
            campaign=campaign,
            new_status=CampaignStatus.ACTIVE
        )
        
        campaign.refresh_from_db()
        assert campaign.status == CampaignStatus.ACTIVE
        assert campaign.synced_at is not None

    def test_mark_as_failed(self, campaign_factory):
        """Test status transition to FAILED."""
        campaign = campaign_factory(status=CampaignStatus.PROCESSING)
        
        CampaignService.update_campaign_status(
            campaign=campaign,
            new_status=CampaignStatus.FAILED,
            error_message="Sync failed"
        )
        
        campaign.refresh_from_db()
        assert campaign.status == CampaignStatus.FAILED
        assert campaign.error_message == "Sync failed"
        assert campaign.retry_count == 1
