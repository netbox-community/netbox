from rest_framework import serializers

from core.api.serializers_.data import DataFileSerializer, DataSourceSerializer
from dcim.api.serializers_.devicetypes import DeviceTypeSerializer
from dcim.api.serializers_.platforms import PlatformSerializer
from dcim.api.serializers_.roles import DeviceRoleSerializer
from dcim.api.serializers_.sites import LocationSerializer, RegionSerializer, SiteSerializer, SiteGroupSerializer
from dcim.models import DeviceRole, DeviceType, Location, Platform, Region, Site, SiteGroup
from extras.models import ConfigContext, Tag
from netbox.api.fields import SerializedPKRelatedField
from netbox.api.serializers import ValidatedModelSerializer
from tenancy.api.serializers_.tenants import TenantSerializer, TenantGroupSerializer
from tenancy.models import Tenant, TenantGroup
from virtualization.api.serializers_.clusters import ClusterSerializer, ClusterGroupSerializer, ClusterTypeSerializer
from virtualization.models import Cluster, ClusterGroup, ClusterType

__all__ = (
    'ConfigContextSerializer',
)


class ConfigContextSerializer(ValidatedModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='extras-api:configcontext-detail')
    regions = SerializedPKRelatedField(
        queryset=Region.objects.all(),
        serializer=RegionSerializer,
        nested=True,
        required=False,
        many=True
    )
    site_groups = SerializedPKRelatedField(
        queryset=SiteGroup.objects.all(),
        serializer=SiteGroupSerializer,
        nested=True,
        required=False,
        many=True
    )
    sites = SerializedPKRelatedField(
        queryset=Site.objects.all(),
        serializer=SiteSerializer,
        nested=True,
        required=False,
        many=True
    )
    locations = SerializedPKRelatedField(
        queryset=Location.objects.all(),
        serializer=LocationSerializer,
        nested=True,
        required=False,
        many=True
    )
    device_types = SerializedPKRelatedField(
        queryset=DeviceType.objects.all(),
        serializer=DeviceTypeSerializer,
        nested=True,
        required=False,
        many=True
    )
    roles = SerializedPKRelatedField(
        queryset=DeviceRole.objects.all(),
        serializer=DeviceRoleSerializer,
        nested=True,
        required=False,
        many=True
    )
    platforms = SerializedPKRelatedField(
        queryset=Platform.objects.all(),
        serializer=PlatformSerializer,
        nested=True,
        required=False,
        many=True
    )
    cluster_types = SerializedPKRelatedField(
        queryset=ClusterType.objects.all(),
        serializer=ClusterTypeSerializer,
        nested=True,
        required=False,
        many=True
    )
    cluster_groups = SerializedPKRelatedField(
        queryset=ClusterGroup.objects.all(),
        serializer=ClusterGroupSerializer,
        nested=True,
        required=False,
        many=True
    )
    clusters = SerializedPKRelatedField(
        queryset=Cluster.objects.all(),
        serializer=ClusterSerializer,
        nested=True,
        required=False,
        many=True
    )
    tenant_groups = SerializedPKRelatedField(
        queryset=TenantGroup.objects.all(),
        serializer=TenantGroupSerializer,
        nested=True,
        required=False,
        many=True
    )
    tenants = SerializedPKRelatedField(
        queryset=Tenant.objects.all(),
        serializer=TenantSerializer,
        nested=True,
        required=False,
        many=True
    )
    tags = serializers.SlugRelatedField(
        queryset=Tag.objects.all(),
        slug_field='slug',
        required=False,
        many=True
    )
    data_source = DataSourceSerializer(
        nested=True,
        required=False
    )
    data_file = DataFileSerializer(
        nested=True,
        read_only=True
    )

    class Meta:
        model = ConfigContext
        fields = [
            'id', 'url', 'display', 'name', 'weight', 'description', 'is_active', 'regions', 'site_groups', 'sites',
            'locations', 'device_types', 'roles', 'platforms', 'cluster_types', 'cluster_groups', 'clusters',
            'tenant_groups', 'tenants', 'tags', 'data_source', 'data_path', 'data_file', 'data_synced', 'data',
            'created', 'last_updated',
        ]
        brief_fields = ('id', 'url', 'display', 'name', 'description')
