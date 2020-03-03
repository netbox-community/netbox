from drf_yasg.utils import swagger_serializer_method
from rest_framework import serializers
from taggit_serializer.serializers import TaggitSerializer, TagListSerializerField

from dcim.api.nested_serializers import NestedDeviceRoleSerializer, NestedPlatformSerializer, NestedSiteSerializer
from dcim.choices import InterfaceModeChoices, InterfaceTypeChoices
from dcim.models import Interface
from extras.api.customfields import CustomFieldModelSerializer
from ipam.api.nested_serializers import NestedIPAddressSerializer, NestedVLANSerializer
from ipam.models import VLAN
from tenancy.api.nested_serializers import NestedTenantSerializer
from utilities.api import ChoiceField, SerializedPKRelatedField, ValidatedModelSerializer
from virtualization.choices import *
from virtualization.models import Cluster, ClusterGroup, ClusterType, VirtualMachine
from .nested_serializers import *


#
# Clusters
#

class ClusterTypeSerializer(ValidatedModelSerializer):
    cluster_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = ClusterType
        fields = ['id', 'name', 'slug', 'cluster_count']


class ClusterGroupSerializer(ValidatedModelSerializer):
    cluster_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = ClusterGroup
        fields = ['id', 'name', 'slug', 'cluster_count']


class ClusterSerializer(TaggitSerializer, CustomFieldModelSerializer):
    type = NestedClusterTypeSerializer()
    group = NestedClusterGroupSerializer(required=False, allow_null=True)
    tenant = NestedTenantSerializer(required=False, allow_null=True)
    site = NestedSiteSerializer(required=False, allow_null=True)
    tags = TagListSerializerField(required=False)
    device_count = serializers.IntegerField(read_only=True)
    virtualmachine_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Cluster
        fields = [
            'id', 'name', 'type', 'group', 'tenant', 'site', 'comments', 'tags', 'custom_fields', 'created', 'last_updated',
            'device_count', 'virtualmachine_count',
        ]


#
# Virtual machines
#

class VirtualMachineSerializer(TaggitSerializer, CustomFieldModelSerializer):
    status = ChoiceField(choices=VirtualMachineStatusChoices, required=False)
    site = NestedSiteSerializer(read_only=True)
    cluster = NestedClusterSerializer()
    role = NestedDeviceRoleSerializer(required=False, allow_null=True)
    tenant = NestedTenantSerializer(required=False, allow_null=True)
    platform = NestedPlatformSerializer(required=False, allow_null=True)
    primary_ip = NestedIPAddressSerializer(read_only=True)
    primary_ip4 = NestedIPAddressSerializer(required=False, allow_null=True)
    primary_ip6 = NestedIPAddressSerializer(required=False, allow_null=True)
    tags = TagListSerializerField(required=False)

    class Meta:
        model = VirtualMachine
        fields = [
            'id', 'name', 'status', 'site', 'cluster', 'role', 'tenant', 'platform', 'primary_ip', 'primary_ip4',
            'primary_ip6', 'vcpus', 'memory', 'disk', 'comments', 'local_context_data', 'tags', 'custom_fields',
            'created', 'last_updated',
        ]
        validators = []


class VirtualMachineWithConfigContextSerializer(VirtualMachineSerializer):
    config_context = serializers.SerializerMethodField()

    class Meta(VirtualMachineSerializer.Meta):
        fields = [
            'id', 'name', 'status', 'site', 'cluster', 'role', 'tenant', 'platform', 'primary_ip', 'primary_ip4',
            'primary_ip6', 'vcpus', 'memory', 'disk', 'comments', 'local_context_data', 'tags', 'custom_fields',
            'config_context', 'created', 'last_updated',
        ]

    @swagger_serializer_method(serializer_or_field=serializers.DictField)
    def get_config_context(self, obj):
        return obj.get_config_context()


#
# VM interfaces
#

class InterfaceSerializer(TaggitSerializer, ValidatedModelSerializer):
    virtual_machine = NestedVirtualMachineSerializer()
    type = ChoiceField(choices=VMInterfaceTypeChoices, default=VMInterfaceTypeChoices.TYPE_VIRTUAL, required=False)
    mode = ChoiceField(choices=InterfaceModeChoices, allow_blank=True, required=False)
    untagged_vlan = NestedVLANSerializer(required=False, allow_null=True)
    tagged_vlans = SerializedPKRelatedField(
        queryset=VLAN.objects.all(),
        serializer=NestedVLANSerializer,
        required=False,
        many=True
    )
    tags = TagListSerializerField(required=False)

    class Meta:
        model = Interface
        fields = [
            'id', 'virtual_machine', 'name', 'type', 'enabled', 'mtu', 'mac_address', 'description', 'mode',
            'untagged_vlan', 'tagged_vlans', 'tags',
        ]
