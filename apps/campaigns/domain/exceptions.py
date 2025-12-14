"""
Campaign domain exceptions.

Custom exceptions for the campaigns domain.
"""


class CampaignError(Exception):
    """Base exception for campaign-related errors."""

    pass


class CampaignNotFoundError(CampaignError):
    """Raised when a campaign is not found."""

    def __init__(self, campaign_id: str):
        self.campaign_id = campaign_id
        super().__init__(f'Campaign with ID {campaign_id} not found.')


class CampaignSyncError(CampaignError):
    """Raised when campaign sync with Amazon fails."""

    def __init__(self, campaign_id: str, reason: str):
        self.campaign_id = campaign_id
        self.reason = reason
        super().__init__(f'Failed to sync campaign {campaign_id}: {reason}')


class CampaignAlreadySyncedError(CampaignError):
    """Raised when trying to sync an already synced campaign."""

    def __init__(self, campaign_id: str):
        self.campaign_id = campaign_id
        super().__init__(f'Campaign {campaign_id} is already synced with Amazon.')


class MaxRetriesExceededError(CampaignError):
    """Raised when maximum retry attempts have been exceeded."""

    def __init__(self, campaign_id: str, max_retries: int):
        self.campaign_id = campaign_id
        self.max_retries = max_retries
        super().__init__(
            f'Campaign {campaign_id} has exceeded maximum retries ({max_retries}).'
        )
