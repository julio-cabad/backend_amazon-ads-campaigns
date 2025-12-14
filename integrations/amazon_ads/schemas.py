"""
Amazon Ads API response schemas.

Data classes for typed responses from the Amazon Ads API.
"""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class CampaignCreateResponse:
    """
    Response from Amazon Ads API when creating a campaign.

    Attributes:
        campaign_id: The Amazon-assigned campaign ID (e.g., 'AMZ-12345')
        status: Initial status ('PROCESSING')
        created_at: Timestamp when created on Amazon's side
    """

    campaign_id: str
    status: str
    created_at: datetime

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            'campaignId': self.campaign_id,
            'status': self.status,
            'createdAt': self.created_at.isoformat(),
        }


@dataclass
class CampaignStatusResponse:
    """
    Response from Amazon Ads API when checking campaign status.

    Attributes:
        campaign_id: The Amazon-assigned campaign ID
        status: Current status ('PROCESSING' or 'ACTIVE')
        serving_status: Delivery status (optional)
        last_updated: Last update timestamp
    """

    campaign_id: str
    status: str
    serving_status: Optional[str] = None
    last_updated: Optional[datetime] = None

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        result = {
            'campaignId': self.campaign_id,
            'status': self.status,
        }
        if self.serving_status:
            result['servingStatus'] = self.serving_status
        if self.last_updated:
            result['lastUpdated'] = self.last_updated.isoformat()
        return result


@dataclass
class AmazonAdsCredentials:
    """
    Credentials for Amazon Ads API authentication.

    These would be used for real API authentication.
    In this mock implementation, they are simulated.
    """

    client_id: str
    client_secret: str
    refresh_token: str
    profile_id: str
    region: str = 'NA'

    @property
    def base_url(self) -> str:
        """Get the base URL for the API based on region."""
        urls = {
            'NA': 'https://advertising-api.amazon.com',
            'EU': 'https://advertising-api-eu.amazon.com',
            'FE': 'https://advertising-api-fe.amazon.com',
        }
        return urls.get(self.region, urls['NA'])
