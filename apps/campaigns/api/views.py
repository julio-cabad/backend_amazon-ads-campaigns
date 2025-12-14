"""
Campaign API views.

ViewSets for campaign CRUD operations.
"""
import structlog
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter

from ..domain.models import Campaign
from ..domain.services import CampaignService
from ..tasks.campaign_tasks import sync_campaign_with_amazon
from .filters import CampaignFilter
from .serializers import (
    CampaignCreateSerializer,
    CampaignListSerializer,
    CampaignSerializer,
    CampaignStatsSerializer,
)

logger = structlog.get_logger(__name__)


@extend_schema_view(
    list=extend_schema(
        summary='List all campaigns',
        description='Retrieve a paginated list of all campaigns with optional filtering.',
        tags=['Campaigns'],
        parameters=[
            OpenApiParameter(name='status', description='Filter by status'),
            OpenApiParameter(name='name', description='Filter by name (contains)'),
            OpenApiParameter(name='has_external_id', description='Filter by sync status'),
        ],
    ),
    create=extend_schema(
        summary='Create a new campaign',
        description='Create a new campaign and trigger async sync with Amazon Ads.',
        tags=['Campaigns'],
    ),
    retrieve=extend_schema(
        summary='Get campaign details',
        description='Retrieve detailed information about a specific campaign.',
        tags=['Campaigns'],
    ),
    destroy=extend_schema(
        summary='Delete a campaign',
        description='Delete a campaign (only if not synced with Amazon).',
        tags=['Campaigns'],
    ),
)
class CampaignViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Campaign CRUD operations.

    Endpoints:
        GET    /api/campaigns/         - List all campaigns
        POST   /api/campaigns/         - Create a new campaign
        GET    /api/campaigns/{id}/    - Get campaign details
        DELETE /api/campaigns/{id}/    - Delete a campaign

    Custom Actions:
        GET    /api/campaigns/stats/   - Get campaign statistics
        POST   /api/campaigns/{id}/retry/  - Retry failed campaign sync
    """

    queryset = Campaign.objects.all()
    filterset_class = CampaignFilter
    search_fields = ['name']
    ordering_fields = ['created_at', 'name', 'budget', 'status']
    ordering = ['-created_at']

    # Disable update operations - campaigns are created and synced, not updated
    http_method_names = ['get', 'post', 'delete', 'head', 'options']

    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.action == 'create':
            return CampaignCreateSerializer
        elif self.action == 'list':
            return CampaignListSerializer
        elif self.action == 'stats':
            return CampaignStatsSerializer
        return CampaignSerializer

    def create(self, request, *args, **kwargs):
        """
        Create a new campaign and trigger async sync.

        1. Validates input data
        2. Creates campaign with PENDING status
        3. Dispatches Celery task to sync with Amazon
        4. Returns created campaign
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Create campaign using service
        campaign = CampaignService.create_campaign(
            name=serializer.validated_data['name'],
            budget=serializer.validated_data['budget'],
            keywords=serializer.validated_data['keywords'],
        )

        # Dispatch async task to sync with Amazon
        sync_campaign_with_amazon.delay(str(campaign.id))

        logger.info(
            'campaign_create_requested',
            campaign_id=str(campaign.id),
            name=campaign.name,
        )

        # Return full campaign details
        output_serializer = CampaignSerializer(campaign)
        return Response(
            output_serializer.data,
            status=status.HTTP_201_CREATED,
        )

    def destroy(self, request, *args, **kwargs):
        """
        Delete a campaign.

        Only allows deletion if:
        - Campaign is not synced with Amazon (no external_id)
        - Campaign is in PENDING or FAILED status
        """
        campaign = self.get_object()

        if campaign.has_external_id:
            return Response(
                {
                    'error': {
                        'code': 'cannot_delete_synced',
                        'message': 'No se puede eliminar una campaña que ya está sincronizada con Amazon.',
                    }
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        logger.info(
            'campaign_deleted',
            campaign_id=str(campaign.id),
            name=campaign.name,
        )

        return super().destroy(request, *args, **kwargs)

    @extend_schema(
        summary='Get campaign statistics',
        description='Retrieve aggregate statistics about campaigns.',
        tags=['Campaigns'],
        responses={200: CampaignStatsSerializer},
    )
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Get campaign statistics."""
        stats = CampaignService.get_campaign_stats()
        serializer = self.get_serializer(stats)
        return Response(serializer.data)

    @extend_schema(
        summary='Retry failed campaign sync',
        description='Retry synchronization for a failed campaign.',
        tags=['Campaigns'],
        responses={
            200: CampaignSerializer,
            400: {'description': 'Campaign cannot be retried'},
        },
    )
    @action(detail=True, methods=['post'])
    def retry(self, request, pk=None):
        """Retry sync for a failed campaign."""
        campaign = self.get_object()

        if not campaign.can_retry:
            return Response(
                {
                    'error': {
                        'code': 'cannot_retry',
                        'message': f'Campaign cannot be retried. Status: {campaign.status}, '
                        f'Retries: {campaign.retry_count}/3',
                    }
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Dispatch retry task
        sync_campaign_with_amazon.delay(str(campaign.id))

        logger.info(
            'campaign_retry_requested',
            campaign_id=str(campaign.id),
            retry_count=campaign.retry_count,
        )

        serializer = CampaignSerializer(campaign)
        return Response(serializer.data)
