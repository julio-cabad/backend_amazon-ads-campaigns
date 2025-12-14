"""
Campaign API filters.

Filter configurations for campaign queries.
"""
import django_filters

from ..domain.models import Campaign, CampaignStatus


class CampaignFilter(django_filters.FilterSet):
    """
    Filter set for Campaign queries.

    Allows filtering by:
        - status: Campaign status (exact match)
        - name: Campaign name (case-insensitive contains)
        - has_external_id: Whether campaign has been synced with Amazon
        - created_after: Campaigns created after date
        - created_before: Campaigns created before date
        - min_budget: Minimum budget
        - max_budget: Maximum budget
    """

    name = django_filters.CharFilter(lookup_expr='icontains')
    status = django_filters.ChoiceFilter(choices=CampaignStatus.choices)
    has_external_id = django_filters.BooleanFilter(
        field_name='external_id',
        method='filter_has_external_id',
    )
    created_after = django_filters.DateTimeFilter(
        field_name='created_at',
        lookup_expr='gte',
    )
    created_before = django_filters.DateTimeFilter(
        field_name='created_at',
        lookup_expr='lte',
    )
    min_budget = django_filters.NumberFilter(
        field_name='budget',
        lookup_expr='gte',
    )
    max_budget = django_filters.NumberFilter(
        field_name='budget',
        lookup_expr='lte',
    )

    class Meta:
        model = Campaign
        fields = ['status', 'name']

    def filter_has_external_id(self, queryset, name, value):
        """Filter by presence of external_id."""
        if value is True:
            return queryset.exclude(external_id__isnull=True).exclude(external_id='')
        elif value is False:
            return queryset.filter(external_id__isnull=True) | queryset.filter(external_id='')
        return queryset
