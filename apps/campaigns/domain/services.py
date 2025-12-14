"""
Campaign domain services.

This module contains the business logic for campaign operations.
"""
from typing import Optional
from uuid import UUID

import structlog

from .exceptions import CampaignNotFoundError, MaxRetriesExceededError
from .models import Campaign, CampaignStatus

logger = structlog.get_logger(__name__)


class CampaignService:
    """
    Service class for campaign business logic.

    This service encapsulates all business rules and operations
    related to campaigns, keeping the views thin.
    """

    MAX_RETRIES = 3

    @staticmethod
    def create_campaign(name: str, budget: float, keywords: list[str]) -> Campaign:
        """
        Create a new campaign.

        Args:
            name: Campaign name.
            budget: Campaign budget in USD.
            keywords: List of keywords for the campaign.

        Returns:
            The created Campaign instance.
        """
        campaign = Campaign.objects.create(
            name=name,
            budget=budget,
            keywords=keywords,
            status=CampaignStatus.PENDING,
        )

        logger.info(
            'campaign_created',
            campaign_id=str(campaign.id),
            name=name,
            budget=float(budget),
            keywords_count=len(keywords),
        )

        return campaign

    @staticmethod
    def get_campaign(campaign_id: UUID) -> Campaign:
        """
        Get a campaign by ID.

        Args:
            campaign_id: The campaign UUID.

        Returns:
            The Campaign instance.

        Raises:
            CampaignNotFoundError: If campaign doesn't exist.
        """
        try:
            return Campaign.objects.get(id=campaign_id)
        except Campaign.DoesNotExist:
            raise CampaignNotFoundError(str(campaign_id))

    @staticmethod
    def get_campaigns_for_sync() -> list[Campaign]:
        """
        Get campaigns that need status synchronization.

        Returns campaigns that have an external_id but are not yet ACTIVE.
        """
        return list(
            Campaign.objects.filter(
                external_id__isnull=False,
                status=CampaignStatus.PROCESSING,
            )
        )

    @staticmethod
    def get_pending_campaigns() -> list[Campaign]:
        """
        Get campaigns that are pending initial sync.

        Returns campaigns with PENDING status that can still be retried.
        """
        return list(
            Campaign.objects.filter(
                status=CampaignStatus.PENDING,
            )
        )

    @staticmethod
    def get_failed_campaigns_for_retry() -> list[Campaign]:
        """
        Get failed campaigns that can be retried.

        Returns campaigns with FAILED status and retry_count < MAX_RETRIES.
        """
        return list(
            Campaign.objects.filter(
                status=CampaignStatus.FAILED,
                retry_count__lt=CampaignService.MAX_RETRIES,
            )
        )

    @staticmethod
    def update_campaign_status(
        campaign: Campaign,
        new_status: str,
        external_id: Optional[str] = None,
        error_message: Optional[str] = None,
    ) -> Campaign:
        """
        Update campaign status based on Amazon sync result.

        Args:
            campaign: The campaign to update.
            new_status: New status from Amazon ('ACTIVE', 'PROCESSING').
            external_id: External ID from Amazon (for initial sync).
            error_message: Error message if sync failed.

        Returns:
            Updated campaign instance.
        """
        if external_id:
            campaign.mark_as_processing(external_id)
            logger.info(
                'campaign_processing',
                campaign_id=str(campaign.id),
                external_id=external_id,
            )

        elif new_status == CampaignStatus.ACTIVE:
            campaign.mark_as_active()
            logger.info(
                'campaign_activated',
                campaign_id=str(campaign.id),
                external_id=campaign.external_id,
            )

        elif error_message:
            if campaign.retry_count >= CampaignService.MAX_RETRIES:
                raise MaxRetriesExceededError(str(campaign.id), CampaignService.MAX_RETRIES)

            campaign.mark_as_failed(error_message)
            logger.warning(
                'campaign_failed',
                campaign_id=str(campaign.id),
                error=error_message,
                retry_count=campaign.retry_count,
            )

        return campaign

    @staticmethod
    def get_campaign_stats() -> dict:
        """
        Get statistics about campaigns.

        Returns:
            Dictionary with campaign counts by status.
        """
        from django.db.models import Count

        stats = Campaign.objects.values('status').annotate(count=Count('id'))
        return {
            'total': Campaign.objects.count(),
            'by_status': {item['status']: item['count'] for item in stats},
        }
