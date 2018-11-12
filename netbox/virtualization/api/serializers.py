from rest_framework import serializers
from taggit_serializer.serializers import TaggitSerializer, TagListSerializerField

from dcim.api.nested_serializers import NestedDeviceRoleSerializer, NestedPlatformSerializer, NestedSiteSerializer
from dcim.constants import IFACE_FF_CHOICES, IFACE_FF_VIRTUAL, IFACE_MODE_CHOICES
from dcim.models import Interface
from extras.api.customfields import CustomFieldModelSerializer
from ipam.api.nested_serializers import NestedIPAddressSerializer, NestedVLANSerializer
from ipam.models import VLAN
from tenancy.api.nested_serializers import NestedTenantSerializer
from utilities.api import ChoiceField, SerializedPKRelatedField, ValidatedModelSerializer
from virtualization.constants import VM_STATUS_CHOICES
from virtualization.models import Cluster, ClusterGroup, ClusterType, VirtualMachine
from .nested_serializers import *


#
# Clusters
#

class ClusterTypeSerializer(ValidatedModelSerializer):

    class Meta:
        model = ClusterType
        fields = ['id', 'name', 'slug']


class ClusterGroupSerializer(ValidatedModelSerializer):

    class Meta:
        model = ClusterGroup
        fields = ['id', 'name', 'slug']


class ClusterSerializer(TaggitSerializer, CustomFieldModelSerializer):
    type = NestedClusterTypeSerializer()
    group = NestedClusterGroupSerializer(required=False, allow_null=True)
    site = NestedSiteSerializer(required=False, allow_null=True)
    tags = TagListSerializerField(required=False)

    class Meta:
        model = Cluster
        fields = [
            'id', 'name', 'type', 'group', 'site', 'comments', 'tags', 'custom_fields', 'created', 'last_updated',
        ]


#
# Virtual machines
#

class VirtualMachineSerializer(TaggitSerializer, CustomFieldModelSerializer):
    status = ChoiceField(choices=VM_STATUS_CHOICES, required=False)
    site = NestedSiteSerializer(read_only=True)
    cluster = NestedClusterSerializer(required=False, allow_null=True)
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


class VirtualMachineWithConfigContextSerializer(VirtualMachineSerializer):
    config_context = serializers.SerializerMethodField()

    class Meta(VirtualMachineSerializer.Meta):
        fields = [
            'id', 'name', 'status', 'site', 'cluster', 'role', 'tenant', 'platform', 'primary_ip', 'primary_ip4',
            'primary_ip6', 'vcpus', 'memory', 'disk', 'comments', 'local_context_data', 'tags', 'custom_fields',
            'config_context', 'created', 'last_updated',
        ]

    def get_config_context(self, obj):
        return obj.get_config_context()


#
# VM interfaces
#

class InterfaceSerializer(TaggitSerializer, ValidatedModelSerializer):
    virtual_machine = NestedVirtualMachineSerializer()
    form_factor = ChoiceField(choices=IFACE_FF_CHOICES, default=IFACE_FF_VIRTUAL, required=False)
    mode = ChoiceField(choices=IFACE_MODE_CHOICES, required=False, allow_null=True)
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
            'id', 'virtual_machine', 'name', 'form_factor', 'enabled', 'mtu', 'mac_address', 'description', 'mode',
            'untagged_vlan', 'tagged_vlans', 'tags',
        ]
