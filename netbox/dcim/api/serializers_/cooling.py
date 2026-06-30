from dcim.choices import *
from dcim.models import CoolingFeed, CoolingSource
from netbox.api.fields import ChoiceField, RelatedObjectCountField
from netbox.api.serializers import PrimaryModelSerializer
from netbox.choices import FlowRateUnitChoices, PressureUnitChoices, TemperatureUnitChoices
from tenancy.api.serializers_.tenants import TenantSerializer

from .racks import RackSerializer
from .sites import LocationSerializer, SiteSerializer

__all__ = (
    'CoolingFeedSerializer',
    'CoolingSourceSerializer',
)


class CoolingSourceSerializer(PrimaryModelSerializer):
    site = SiteSerializer(nested=True)
    location = LocationSerializer(
        nested=True,
        required=False,
        allow_null=True,
        default=None
    )
    type = ChoiceField(
        choices=CoolingSourceTypeChoices
    )
    status = ChoiceField(
        choices=CoolingSourceStatusChoices,
        default=lambda: CoolingSourceStatusChoices.STATUS_ACTIVE,
    )
    temperature_unit = ChoiceField(
        choices=TemperatureUnitChoices,
        allow_blank=True,
        required=False,
        allow_null=True
    )

    # Related object counts
    coolingfeed_count = RelatedObjectCountField('cooling_feeds')

    class Meta:
        model = CoolingSource
        fields = [
            'id', 'url', 'display_url', 'display', 'site', 'location', 'name', 'type', 'status', 'cooling_capacity',
            'supply_temperature', 'return_temperature', 'temperature_unit', 'description', 'owner', 'comments', 'tags',
            'custom_fields', 'coolingfeed_count', 'created', 'last_updated',
        ]
        brief_fields = ('id', 'url', 'display', 'name', 'description', 'coolingfeed_count')


class CoolingFeedSerializer(PrimaryModelSerializer):
    cooling_source = CoolingSourceSerializer(nested=True)
    rack = RackSerializer(
        nested=True,
        required=False,
        allow_null=True,
        default=None
    )
    flow_direction = ChoiceField(
        choices=CoolingFlowDirectionChoices,
        default=lambda: CoolingFlowDirectionChoices.TYPE_SUPPLY,
    )
    status = ChoiceField(
        choices=CoolingFeedStatusChoices,
        default=lambda: CoolingFeedStatusChoices.STATUS_ACTIVE,
    )
    fluid_type = ChoiceField(
        choices=FluidTypeChoices,
        allow_blank=True,
        required=False,
        allow_null=True
    )
    flow_rate_unit = ChoiceField(
        choices=FlowRateUnitChoices,
        allow_blank=True,
        required=False,
        allow_null=True
    )
    pressure_unit = ChoiceField(
        choices=PressureUnitChoices,
        allow_blank=True,
        required=False,
        allow_null=True
    )
    temperature_unit = ChoiceField(
        choices=TemperatureUnitChoices,
        allow_blank=True,
        required=False,
        allow_null=True
    )
    tenant = TenantSerializer(
        nested=True,
        required=False,
        allow_null=True
    )

    class Meta:
        model = CoolingFeed
        fields = [
            'id', 'url', 'display_url', 'display', 'cooling_source', 'rack', 'name', 'status', 'flow_direction',
            'fluid_type', 'cooling_capacity', 'flow_rate', 'flow_rate_unit', 'pressure', 'pressure_unit',
            'supply_temperature', 'return_temperature', 'temperature_unit', 'description', 'tenant', 'owner',
            'comments', 'tags', 'custom_fields', 'created', 'last_updated',
        ]
        brief_fields = ('id', 'url', 'display', 'name', 'description')
