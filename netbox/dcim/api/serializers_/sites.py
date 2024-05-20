from rest_framework import serializers
from timezone_field.rest_framework import TimeZoneSerializerField

from dcim.choices import *
from dcim.models import Location, Region, Site, SiteGroup
from ipam.api.serializers_.asns import ASNSerializer
from ipam.models import ASN
from netbox.api.fields import ChoiceField, RelatedObjectCountField, SerializedPKRelatedField
from netbox.api.serializers import NestedGroupModelSerializer, NetBoxModelSerializer
from tenancy.api.serializers_.tenants import TenantSerializer
from ..nested_serializers import *

__all__ = (
    'LocationSerializer',
    'RegionSerializer',
    'SiteGroupSerializer',
    'SiteSerializer',
)


class RegionSerializer(NestedGroupModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='dcim-api:region-detail')
    parent = NestedRegionSerializer(required=False, allow_null=True, default=None)
    site_count = serializers.IntegerField(read_only=True, default=0)

    class Meta:
        model = Region
        fields = [
            'id', 'url', 'display', 'name', 'slug', 'parent', 'description', 'tags', 'custom_fields', 'created',
            'last_updated', 'site_count', '_depth',
        ]
        brief_fields = ('id', 'url', 'display', 'name', 'slug', 'description', 'site_count', '_depth')


class SiteGroupSerializer(NestedGroupModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='dcim-api:sitegroup-detail')
    parent = NestedSiteGroupSerializer(required=False, allow_null=True, default=None)
    site_count = serializers.IntegerField(read_only=True, default=0)

    class Meta:
        model = SiteGroup
        fields = [
            'id', 'url', 'display', 'name', 'slug', 'parent', 'description', 'tags', 'custom_fields', 'created',
            'last_updated', 'site_count', '_depth',
        ]
        brief_fields = ('id', 'url', 'display', 'name', 'slug', 'description', 'site_count', '_depth')


class SiteSerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='dcim-api:site-detail')
    status = ChoiceField(choices=SiteStatusChoices, required=False)
    region = RegionSerializer(nested=True, required=False, allow_null=True)
    group = SiteGroupSerializer(nested=True, required=False, allow_null=True)
    tenant = TenantSerializer(nested=True, required=False, allow_null=True)
    time_zone = TimeZoneSerializerField(required=False, allow_null=True)
    asns = SerializedPKRelatedField(
        queryset=ASN.objects.all(),
        serializer=ASNSerializer,
        nested=True,
        required=False,
        many=True
    )

    # Related object counts
    circuit_count = RelatedObjectCountField('circuit_terminations')
    device_count = RelatedObjectCountField('devices')
    prefix_count = RelatedObjectCountField('prefixes')
    rack_count = RelatedObjectCountField('racks')
    vlan_count = RelatedObjectCountField('vlans')
    virtualmachine_count = RelatedObjectCountField('virtual_machines')

    class Meta:
        model = Site
        fields = [
            'id', 'url', 'display', 'name', 'slug', 'status', 'region', 'group', 'tenant', 'facility', 'time_zone',
            'description', 'physical_address', 'shipping_address', 'latitude', 'longitude', 'comments', 'asns', 'tags',
            'custom_fields', 'created', 'last_updated', 'circuit_count', 'device_count', 'prefix_count', 'rack_count',
            'virtualmachine_count', 'vlan_count',
        ]
        brief_fields = ('id', 'url', 'display', 'name', 'description', 'slug')


class LocationSerializer(NestedGroupModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='dcim-api:location-detail')
    site = SiteSerializer(nested=True)
    parent = NestedLocationSerializer(required=False, allow_null=True, default=None)
    status = ChoiceField(choices=LocationStatusChoices, required=False)
    tenant = TenantSerializer(nested=True, required=False, allow_null=True)
    rack_count = serializers.IntegerField(read_only=True, default=0)
    device_count = serializers.IntegerField(read_only=True, default=0)

    class Meta:
        model = Location
        fields = [
            'id', 'url', 'display', 'name', 'slug', 'site', 'parent', 'status', 'tenant', 'facility', 'description',
            'tags', 'custom_fields', 'created', 'last_updated', 'rack_count', 'device_count', '_depth',
        ]
        brief_fields = ('id', 'url', 'display', 'name', 'slug', 'description', 'rack_count', '_depth')
