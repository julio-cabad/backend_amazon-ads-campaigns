"""
Campaign API serializers.

Serializers for input validation and output formatting.
"""
from rest_framework import serializers

from ..domain.models import Campaign, CampaignStatus


class KeywordsField(serializers.ListField):
    """
    Custom field for keywords that accepts comma-separated strings or lists.
    """

    child = serializers.CharField(max_length=100, trim_whitespace=True)

    def to_internal_value(self, data):
        """Convert input to list of keywords."""
        # If it's a string, split by comma
        if isinstance(data, str):
            data = [kw.strip() for kw in data.split(',') if kw.strip()]
        return super().to_internal_value(data)


class CampaignCreateSerializer(serializers.Serializer):
    """
    Serializer for creating a new campaign.

    Input:
        name: Campaign name (required)
        budget: Campaign budget in USD (required, positive number)
        keywords: List of keywords or comma-separated string (required)
    """

    name = serializers.CharField(
        max_length=255,
        help_text='Name of the campaign.',
    )
    budget = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        min_value=0.01,
        help_text='Campaign budget in USD.',
    )
    keywords = KeywordsField(
        min_length=1,
        help_text='List of keywords for the campaign.',
    )

    def validate_name(self, value):
        """Validate campaign name."""
        if not value.strip():
            raise serializers.ValidationError('Campaign name cannot be empty.')
        return value.strip()

    def validate_keywords(self, value):
        """Validate keywords list."""
        # Remove duplicates while preserving order
        seen = set()
        unique_keywords = []
        for kw in value:
            if kw.lower() not in seen:
                seen.add(kw.lower())
                unique_keywords.append(kw)
        return unique_keywords


class CampaignSerializer(serializers.ModelSerializer):
    """
    Serializer for Campaign model (read operations).

    Provides full campaign details including computed properties.
    """

    has_external_id = serializers.BooleanField(read_only=True)
    is_synced = serializers.BooleanField(read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = Campaign
        fields = [
            'id',
            'name',
            'budget',
            'keywords',
            'status',
            'status_display',
            'external_id',
            'has_external_id',
            'is_synced',
            'error_message',
            'retry_count',
            'synced_at',
            'created_at',
            'updated_at',
        ]
        read_only_fields = fields


class CampaignListSerializer(serializers.ModelSerializer):
    """
    Lightweight serializer for campaign listings.

    Used for list endpoints to reduce payload size.
    """

    has_external_id = serializers.BooleanField(read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = Campaign
        fields = [
            'id',
            'name',
            'budget',
            'keywords',
            'status',
            'status_display',
            'external_id',
            'has_external_id',
            'created_at',
        ]
        read_only_fields = fields


class CampaignStatsSerializer(serializers.Serializer):
    """Serializer for campaign statistics."""

    total = serializers.IntegerField()
    by_status = serializers.DictField(child=serializers.IntegerField())
