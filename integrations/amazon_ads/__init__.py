"""
Amazon Ads integration package.

This package provides a simulated client for Amazon Ads API.
"""
from .client import AmazonAdsClient
from .exceptions import (
    AmazonAdsError,
    AmazonAdsRateLimitError,
    AmazonAdsServerError,
    AmazonAdsAuthError,
)
from .schemas import CampaignCreateResponse, CampaignStatusResponse

__all__ = [
    'AmazonAdsClient',
    'AmazonAdsError',
    'AmazonAdsRateLimitError',
    'AmazonAdsServerError',
    'AmazonAdsAuthError',
    'CampaignCreateResponse',
    'CampaignStatusResponse',
]
