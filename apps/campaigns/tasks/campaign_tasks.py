"""
Async tasks for campaigns.

This module contains Celery tasks for handling long-running operations
like synchronizing with the Amazon Ads API.
"""
from celery import shared_task
import structlog
from django.db import transaction

from apps.campaigns.domain.models import Campaign, CampaignStatus
from apps.campaigns.domain.services import CampaignService
from integrations.amazon_ads.client import get_amazon_ads_client
from integrations.amazon_ads.exceptions import AmazonAdsError

logger = structlog.get_logger(__name__)


@shared_task(
    bind=True,
    max_retries=3,
    default_retry_delay=60,
    name='apps.campaigns.tasks.campaign_tasks.sync_campaign_with_amazon',
)
def sync_campaign_with_amazon(self, campaign_id: str):
    """
    Sync a locally created campaign with Amazon Ads.

    1. Get campaign from DB
    2. Call Amazon Ads API to create campaign
    3. Update local campaign with external ID
    4. Handle errors and retries

    Args:
        campaign_id: UUID of the campaign to sync
    """
    logger.info('task_sync_campaign_started', campaign_id=campaign_id)

    try:
        # 1. Get campaign
        campaign = CampaignService.get_campaign(campaign_id)

        # Skip if already synced or not in valid state
        if campaign.is_synced:
            logger.info('campaign_already_synced', campaign_id=campaign_id)
            return

        # 2. Call Amazon API
        client = get_amazon_ads_client()
        response = client.create_campaign(
            name=campaign.name,
            budget=float(campaign.budget),
            keywords=campaign.keywords,
        )

        # 3. Update local status
        CampaignService.update_campaign_status(
            campaign=campaign,
            new_status=response.status,
            external_id=response.campaign_id,
        )

        logger.info(
            'task_sync_campaign_success',
            campaign_id=campaign_id,
            external_id=response.campaign_id,
        )

    except AmazonAdsError as e:
        logger.error(
            'task_sync_campaign_failed',
            campaign_id=campaign_id,
            error=str(e),
        )

        # Update campaign status to FAILED
        try:
            campaign = CampaignService.get_campaign(campaign_id)
            CampaignService.update_campaign_status(
                campaign=campaign,
                new_status=CampaignStatus.FAILED,
                error_message=str(e),
            )
        except Exception as db_error:
            logger.error('db_update_failed', error=str(db_error))

        # Retry logic is handled by the API client (tenacity),
        # but if we get here, it means all retries failed.
        # We can optionally use Celery's retry here too.
        # self.retry(exc=e)

    except Exception as e:
        logger.exception(
            'task_sync_campaign_unexpected_error',
            campaign_id=campaign_id,
            error=str(e),
        )
        # Fail safe
        try:
            campaign = CampaignService.get_campaign(campaign_id)
            campaign.mark_as_failed(f"Unexpected error: {str(e)}")
        except Exception:
            pass


@shared_task(
    name='apps.campaigns.tasks.campaign_tasks.sync_all_campaign_statuses',
)
def sync_all_campaign_statuses():
    """
    Periodic task to update statuses of all processing campaigns.

    Iterates through all campaigns that are in PROCESSING state
    and checks their status with Amazon Ads API.
    """
    logger.info('task_sync_all_statuses_started')

    # Get campaigns that need update
    campaigns = CampaignService.get_campaigns_for_sync()
    
    if not campaigns:
        logger.info('no_campaigns_to_sync')
        return

    logger.info('campaigns_to_sync_count', count=len(campaigns))

    client = get_amazon_ads_client()
    success_count = 0
    error_count = 0

    for campaign in campaigns:
        try:
            # Check status with Amazon
            response = client.get_campaign_status(campaign.external_id)

            # Update local status if changed
            if response.status != campaign.status:
                CampaignService.update_campaign_status(
                    campaign=campaign,
                    new_status=response.status,
                )
                logger.info(
                    'campaign_status_updated',
                    campaign_id=str(campaign.id),
                    old_status=campaign.status,
                    new_status=response.status,
                )
            
            success_count += 1

        except Exception as e:
            error_count += 1
            logger.error(
                'sync_status_failed_for_campaign',
                campaign_id=str(campaign.id),
                error=str(e),
            )

    logger.info(
        'task_sync_all_statuses_completed',
        total=len(campaigns),
        success=success_count,
        error=error_count,
    )
