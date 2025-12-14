"""
Simulated Amazon Ads API Client.

This module provides a mock implementation of the Amazon Ads API client.
It simulates API responses with realistic behavior including:
- Random delays
- 20% error rate (as specified in requirements)
- Realistic response formats
- State transitions (PROCESSING -> ACTIVE)
"""
import random
import time
import uuid
from datetime import datetime
from typing import Optional

import structlog
from django.conf import settings
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
)

from .auth import create_amazon_ads_auth
from .exceptions import (
    AmazonAdsError,
    AmazonAdsRateLimitError,
    AmazonAdsServerError,
)
from .schemas import CampaignCreateResponse, CampaignStatusResponse

logger = structlog.get_logger(__name__)


class AmazonAdsClient:
    """
    Simulated Amazon Ads API Client.

    This client mimics the behavior of the real Amazon Ads API
    for testing and development purposes.

    Features:
        - Campaign creation with simulated external IDs
        - Status checking with state transitions
        - 20% error rate (configurable)
        - Realistic delays
        - Retry logic with exponential backoff
    """

    # Simulated API behavior
    DEFAULT_ERROR_RATE = 0.2  # 20% chance of error
    MIN_DELAY_MS = 100
    MAX_DELAY_MS = 500

    def __init__(
        self,
        client_id: Optional[str] = None,
        client_secret: Optional[str] = None,
        refresh_token: Optional[str] = None,
        profile_id: Optional[str] = None,
        region: str = 'NA',
        error_rate: Optional[float] = None,
    ):
        """
        Initialize the Amazon Ads client.

        Args:
            client_id: Amazon Ads client ID (uses settings if not provided)
            client_secret: Amazon Ads client secret
            refresh_token: OAuth refresh token
            profile_id: Amazon Ads profile ID
            region: API region (NA, EU, FE)
            error_rate: Probability of API errors (0.0 to 1.0)
        """
        config = getattr(settings, 'AMAZON_ADS_CONFIG', {})

        self.client_id = client_id or config.get('CLIENT_ID', 'mock-client-id')
        self.client_secret = client_secret or config.get('CLIENT_SECRET', 'mock-secret')
        self.refresh_token = refresh_token or config.get('REFRESH_TOKEN', 'mock-token')
        self.profile_id = profile_id or config.get('PROFILE_ID', 'mock-profile')
        self.region = region or config.get('REGION', 'NA')
        self.error_rate = error_rate if error_rate is not None else config.get(
            'ERROR_RATE', self.DEFAULT_ERROR_RATE
        )

        logger.info(
            'amazon_ads_client_initialized',
            region=self.region,
            error_rate=self.error_rate,
        )

    def _get_auth_headers(self) -> dict:
        """Get authentication headers for API requests."""
        return create_amazon_ads_auth(
            client_id=self.client_id,
            client_secret=self.client_secret,
            refresh_token=self.refresh_token,
            region=self.region,
        )

    def _simulate_delay(self) -> None:
        """Simulate network delay."""
        delay = random.randint(self.MIN_DELAY_MS, self.MAX_DELAY_MS) / 1000
        time.sleep(delay)

    def _should_fail(self) -> bool:
        """Determine if this request should fail (based on error rate)."""
        return random.random() < self.error_rate

    def _generate_external_id(self) -> str:
        """Generate a realistic Amazon campaign ID."""
        # Format: AMZ-<5 digit number>
        return f'AMZ-{random.randint(10000, 99999)}'

    def _raise_random_error(self) -> None:
        """Raise a random API error."""
        error_types = [
            (AmazonAdsRateLimitError, 'Rate limit exceeded. Retry after 60 seconds.'),
            (AmazonAdsServerError, 'AWS internal server error. Please try again.'),
            (AmazonAdsServerError, 'Service temporarily unavailable.'),
        ]
        # Weight towards rate limit (more common in real APIs)
        weights = [0.6, 0.3, 0.1]
        error_class, message = random.choices(error_types, weights=weights)[0]

        logger.warning(
            'amazon_ads_simulated_error',
            error_type=error_class.__name__,
            message=message,
        )

        raise error_class(message)

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((AmazonAdsRateLimitError,)),
        reraise=True,
    )
    def create_campaign(
        self,
        name: str,
        budget: float,
        keywords: list[str],
    ) -> CampaignCreateResponse:
        """
        Create a campaign on Amazon Ads (simulated).

        This method simulates the API call to create a campaign on Amazon.
        It may randomly fail to simulate real-world API behavior.

        Args:
            name: Campaign name
            budget: Daily budget in USD
            keywords: Target keywords

        Returns:
            CampaignCreateResponse with external campaign ID

        Raises:
            AmazonAdsRateLimitError: If rate limit is exceeded (429)
            AmazonAdsServerError: If server error occurs (500)
        """
        logger.info(
            'amazon_ads_create_campaign_request',
            name=name,
            budget=budget,
            keywords_count=len(keywords),
        )

        # Simulate API latency
        self._simulate_delay()

        # Randomly fail based on error rate
        if self._should_fail():
            self._raise_random_error()

        # Generate response
        external_id = self._generate_external_id()
        response = CampaignCreateResponse(
            campaign_id=external_id,
            status='PROCESSING',
            created_at=datetime.utcnow(),
        )

        logger.info(
            'amazon_ads_campaign_created',
            external_id=external_id,
            name=name,
        )

        return response

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((AmazonAdsRateLimitError,)),
        reraise=True,
    )
    def get_campaign_status(self, external_id: str) -> CampaignStatusResponse:
        """
        Get campaign status from Amazon Ads (simulated).

        Simulates checking the status of a campaign. Campaigns transition
        from PROCESSING to ACTIVE after a random period.

        Args:
            external_id: The Amazon campaign ID

        Returns:
            CampaignStatusResponse with current status

        Raises:
            AmazonAdsRateLimitError: If rate limit is exceeded (429)
            AmazonAdsServerError: If server error occurs (500)
        """
        logger.info(
            'amazon_ads_get_status_request',
            external_id=external_id,
        )

        # Simulate API latency
        self._simulate_delay()

        # Randomly fail based on error rate
        if self._should_fail():
            self._raise_random_error()

        # Simulate status transition (70% chance of being ACTIVE if checked)
        # In reality, campaigns take time to review, but for testing
        # we make them active relatively quickly
        status = random.choices(
            ['ACTIVE', 'PROCESSING'],
            weights=[0.7, 0.3],
        )[0]

        response = CampaignStatusResponse(
            campaign_id=external_id,
            status=status,
            serving_status='ELIGIBLE' if status == 'ACTIVE' else 'PENDING_REVIEW',
            last_updated=datetime.utcnow(),
        )

        logger.info(
            'amazon_ads_status_retrieved',
            external_id=external_id,
            status=status,
        )

        return response

    def health_check(self) -> bool:
        """
        Check if Amazon Ads API is reachable (simulated).

        Returns:
            True if API is healthy, False otherwise
        """
        try:
            self._simulate_delay()
            # Always healthy in simulation (unless we decide to fail)
            return not self._should_fail()
        except Exception:
            return False


# Singleton instance for convenience
_default_client: Optional[AmazonAdsClient] = None


def get_amazon_ads_client() -> AmazonAdsClient:
    """
    Get the default Amazon Ads client instance.

    This provides a singleton pattern for the client.
    """
    global _default_client
    if _default_client is None:
        _default_client = AmazonAdsClient()
    return _default_client
