from rest_framework import serializers

from core.api.serializers_.data import DataFileSerializer, DataSourceSerializer
from dcim.api.nested_serializers import (
    NestedDeviceRoleSerializer, NestedDeviceTypeSerializer, NestedLocationSerializer, NestedPlatformSerializer,
    NestedRegionSerializer, NestedSiteSerializer, NestedSiteGroupSerializer,
)
from dcim.models import DeviceRole, DeviceType, Location, Platform, Region, Site, SiteGroup
from extras.models import ConfigContext, ConfigTemplate, Tag
from netbox.api.fields import SerializedPKRelatedField
from netbox.api.serializers import ValidatedModelSerializer
from netbox.api.serializers.features import TaggableModelSerializer
from tenancy.api.nested_serializers import NestedTenantSerializer, NestedTenantGroupSerializer
from tenancy.models import Tenant, TenantGroup
from virtualization.api.nested_serializers import (
    NestedClusterGroupSerializer, NestedClusterSerializer, NestedClusterTypeSerializer,
)
from virtualization.models import Cluster, ClusterGroup, ClusterType

__all__ = (
    'ConfigContextSerializer',
    'ConfigTemplateSerializer',
)


class ConfigContextSerializer(ValidatedModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='extras-api:configcontext-detail')
    regions = SerializedPKRelatedField(
        queryset=Region.objects.all(),
        serializer=NestedRegionSerializer,
        required=False,
        many=True
    )
    site_groups = SerializedPKRelatedField(
        queryset=SiteGroup.objects.all(),
        serializer=NestedSiteGroupSerializer,
        required=False,
        many=True
    )
    sites = SerializedPKRelatedField(
        queryset=Site.objects.all(),
        serializer=NestedSiteSerializer,
        required=False,
        many=True
    )
    locations = SerializedPKRelatedField(
        queryset=Location.objects.all(),
        serializer=NestedLocationSerializer,
        required=False,
        many=True
    )
    device_types = SerializedPKRelatedField(
        queryset=DeviceType.objects.all(),
        serializer=NestedDeviceTypeSerializer,
        required=False,
        many=True
    )
    roles = SerializedPKRelatedField(
        queryset=DeviceRole.objects.all(),
        serializer=NestedDeviceRoleSerializer,
        required=False,
        many=True
    )
    platforms = SerializedPKRelatedField(
        queryset=Platform.objects.all(),
        serializer=NestedPlatformSerializer,
        required=False,
        many=True
    )
    cluster_types = SerializedPKRelatedField(
        queryset=ClusterType.objects.all(),
        serializer=NestedClusterTypeSerializer,
        required=False,
        many=True
    )
    cluster_groups = SerializedPKRelatedField(
        queryset=ClusterGroup.objects.all(),
        serializer=NestedClusterGroupSerializer,
        required=False,
        many=True
    )
    clusters = SerializedPKRelatedField(
        queryset=Cluster.objects.all(),
        serializer=NestedClusterSerializer,
        required=False,
        many=True
    )
    tenant_groups = SerializedPKRelatedField(
        queryset=TenantGroup.objects.all(),
        serializer=NestedTenantGroupSerializer,
        required=False,
        many=True
    )
    tenants = SerializedPKRelatedField(
        queryset=Tenant.objects.all(),
        serializer=NestedTenantSerializer,
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


#
# Config templates
#

class ConfigTemplateSerializer(TaggableModelSerializer, ValidatedModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='extras-api:configtemplate-detail')
    data_source = DataSourceSerializer(
        nested=True,
        required=False
    )
    data_file = DataFileSerializer(
        nested=True,
        required=False
    )

    class Meta:
        model = ConfigTemplate
        fields = [
            'id', 'url', 'display', 'name', 'description', 'environment_params', 'template_code', 'data_source',
            'data_path', 'data_file', 'data_synced', 'tags', 'created', 'last_updated',
        ]
        brief_fields = ('id', 'url', 'display', 'name', 'description')
