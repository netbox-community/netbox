from rest_framework import serializers

from dcim.choices import *
from dcim.models import PowerFeed, PowerPanel
from netbox.api.fields import ChoiceField, RelatedObjectCountField
from netbox.api.serializers import NetBoxModelSerializer
from tenancy.api.serializers_.tenants import TenantSerializer
from .base import ConnectedEndpointsSerializer
from .cables import CabledObjectSerializer
from .racks import RackSerializer
from .sites import LocationSerializer, SiteSerializer

__all__ = (
    'PowerFeedSerializer',
    'PowerPanelSerializer',
)


class PowerPanelSerializer(NetBoxModelSerializer):
    site = SiteSerializer(nested=True)
    location = LocationSerializer(
        nested=True,
        required=False,
        allow_null=True,
        default=None
    )

    # Related object counts
    powerfeed_count = RelatedObjectCountField('powerfeeds')

    class Meta:
        model = PowerPanel
        fields = [
            'id', 'url', 'display_url', 'display', 'site', 'location', 'name', 'description', 'comments', 'tags',
            'custom_fields', 'powerfeed_count', 'created', 'last_updated',
        ]
        brief_fields = ('id', 'url', 'display', 'name', 'description', 'powerfeed_count')


class PowerFeedSerializer(NetBoxModelSerializer, CabledObjectSerializer, ConnectedEndpointsSerializer):
    power_panel = PowerPanelSerializer(nested=True)
    rack = RackSerializer(
        nested=True,
        required=False,
        allow_null=True,
        default=None
    )
    type = ChoiceField(
        choices=PowerFeedTypeChoices,
        default=lambda: PowerFeedTypeChoices.TYPE_PRIMARY,
    )
    status = ChoiceField(
        choices=PowerFeedStatusChoices,
        default=lambda: PowerFeedStatusChoices.STATUS_ACTIVE,
    )
    supply = ChoiceField(
        choices=PowerFeedSupplyChoices,
        default=lambda: PowerFeedSupplyChoices.SUPPLY_AC,
    )
    phase = ChoiceField(
        choices=PowerFeedPhaseChoices,
        default=lambda: PowerFeedPhaseChoices.PHASE_SINGLE,
    )
    tenant = TenantSerializer(
        nested=True,
        required=False,
        allow_null=True
    )

    class Meta:
        model = PowerFeed
        fields = [
            'id', 'url', 'display_url', 'display', 'power_panel', 'rack', 'name', 'status', 'type', 'supply',
            'phase', 'voltage', 'amperage', 'max_utilization', 'mark_connected', 'cable', 'cable_end', 'link_peers',
            'link_peers_type', 'connected_endpoints', 'connected_endpoints_type', 'connected_endpoints_reachable',
            'description', 'tenant', 'comments', 'tags', 'custom_fields', 'created', 'last_updated', '_occupied',
        ]
        brief_fields = ('id', 'url', 'display', 'name', 'description', 'cable', '_occupied')
