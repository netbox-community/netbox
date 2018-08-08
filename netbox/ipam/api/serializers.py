from __future__ import unicode_literals

from collections import OrderedDict

from rest_framework import serializers
from rest_framework.reverse import reverse
from rest_framework.validators import UniqueTogetherValidator
from taggit_serializer.serializers import TaggitSerializer, TagListSerializerField

from dcim.api.serializers import NestedDeviceSerializer, InterfaceSerializer, NestedSiteSerializer
from dcim.models import Interface
from extras.api.customfields import CustomFieldModelSerializer
from ipam.constants import (
    IPADDRESS_ROLE_CHOICES, IPADDRESS_STATUS_CHOICES, IP_PROTOCOL_CHOICES, PREFIX_STATUS_CHOICES, VLAN_STATUS_CHOICES,
)
from ipam.models import Aggregate, IPAddress, Prefix, RIR, Role, Service, VLAN, VLANGroup, VRF
from tenancy.api.serializers import NestedTenantSerializer
from utilities.api import (
    ChoiceField, SerializedPKRelatedField, ValidatedModelSerializer, WritableNestedSerializer,
)
from virtualization.api.serializers import NestedVirtualMachineSerializer


#
# VRFs
#

class VRFSerializer(TaggitSerializer, CustomFieldModelSerializer):
    tenant = NestedTenantSerializer(required=False, allow_null=True)
    tags = TagListSerializerField(required=False)

    class Meta:
        model = VRF
        fields = [
            'id', 'name', 'rd', 'tenant', 'enforce_unique', 'description', 'tags', 'display_name', 'custom_fields',
            'created', 'last_updated',
        ]


class NestedVRFSerializer(WritableNestedSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='ipam-api:vrf-detail')

    class Meta:
        model = VRF
        fields = ['id', 'url', 'name', 'rd']


#
# Roles
#

class RoleSerializer(ValidatedModelSerializer):

    class Meta:
        model = Role
        fields = ['id', 'name', 'slug', 'weight']


class NestedRoleSerializer(WritableNestedSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='ipam-api:role-detail')

    class Meta:
        model = Role
        fields = ['id', 'url', 'name', 'slug']


#
# RIRs
#

class RIRSerializer(ValidatedModelSerializer):

    class Meta:
        model = RIR
        fields = ['id', 'name', 'slug', 'is_private']


class NestedRIRSerializer(WritableNestedSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='ipam-api:rir-detail')

    class Meta:
        model = RIR
        fields = ['id', 'url', 'name', 'slug']


#
# Aggregates
#

class AggregateSerializer(TaggitSerializer, CustomFieldModelSerializer):
    rir = NestedRIRSerializer()
    tags = TagListSerializerField(required=False)

    class Meta:
        model = Aggregate
        fields = [
            'id', 'family', 'prefix', 'rir', 'date_added', 'description', 'tags', 'custom_fields', 'created',
            'last_updated',
        ]
        read_only_fields = ['family']


class NestedAggregateSerializer(WritableNestedSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='ipam-api:aggregate-detail')

    class Meta(AggregateSerializer.Meta):
        model = Aggregate
        fields = ['id', 'url', 'family', 'prefix']


#
# VLAN groups
#

class VLANGroupSerializer(ValidatedModelSerializer):
    site = NestedSiteSerializer(required=False, allow_null=True)

    class Meta:
        model = VLANGroup
        fields = ['id', 'name', 'slug', 'site']
        validators = []

    def validate(self, data):

        # Validate uniqueness of name and slug if a site has been assigned.
        if data.get('site', None):
            for field in ['name', 'slug']:
                validator = UniqueTogetherValidator(queryset=VLANGroup.objects.all(), fields=('site', field))
                validator.set_context(self)
                validator(data)

        # Enforce model validation
        super(VLANGroupSerializer, self).validate(data)

        return data


class NestedVLANGroupSerializer(WritableNestedSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='ipam-api:vlangroup-detail')

    class Meta:
        model = VLANGroup
        fields = ['id', 'url', 'name', 'slug']


#
# VLANs
#

class VLANSerializer(TaggitSerializer, CustomFieldModelSerializer):
    site = NestedSiteSerializer(required=False, allow_null=True)
    group = NestedVLANGroupSerializer(required=False, allow_null=True)
    tenant = NestedTenantSerializer(required=False, allow_null=True)
    status = ChoiceField(choices=VLAN_STATUS_CHOICES, required=False)
    role = NestedRoleSerializer(required=False, allow_null=True)
    tags = TagListSerializerField(required=False)

    class Meta:
        model = VLAN
        fields = [
            'id', 'site', 'group', 'vid', 'name', 'tenant', 'status', 'role', 'description', 'tags', 'display_name',
            'custom_fields', 'created', 'last_updated',
        ]
        validators = []

    def validate(self, data):

        # Validate uniqueness of vid and name if a group has been assigned.
        if data.get('group', None):
            for field in ['vid', 'name']:
                validator = UniqueTogetherValidator(queryset=VLAN.objects.all(), fields=('group', field))
                validator.set_context(self)
                validator(data)

        # Enforce model validation
        super(VLANSerializer, self).validate(data)

        return data


class NestedVLANSerializer(WritableNestedSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='ipam-api:vlan-detail')

    class Meta:
        model = VLAN
        fields = ['id', 'url', 'vid', 'name', 'display_name']


#
# Prefixes
#

class PrefixSerializer(TaggitSerializer, CustomFieldModelSerializer):
    site = NestedSiteSerializer(required=False, allow_null=True)
    vrf = NestedVRFSerializer(required=False, allow_null=True)
    tenant = NestedTenantSerializer(required=False, allow_null=True)
    vlan = NestedVLANSerializer(required=False, allow_null=True)
    status = ChoiceField(choices=PREFIX_STATUS_CHOICES, required=False)
    role = NestedRoleSerializer(required=False, allow_null=True)
    tags = TagListSerializerField(required=False)

    class Meta:
        model = Prefix
        fields = [
            'id', 'family', 'prefix', 'site', 'vrf', 'tenant', 'vlan', 'status', 'role', 'is_pool', 'description',
            'tags', 'custom_fields', 'created', 'last_updated',
        ]
        read_only_fields = ['family']


class NestedPrefixSerializer(WritableNestedSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='ipam-api:prefix-detail')

    class Meta:
        model = Prefix
        fields = ['id', 'url', 'family', 'prefix']


class AvailablePrefixSerializer(serializers.Serializer):

    def to_representation(self, instance):
        if self.context.get('vrf'):
            vrf = NestedVRFSerializer(self.context['vrf'], context={'request': self.context['request']}).data
        else:
            vrf = None
        return OrderedDict([
            ('family', instance.version),
            ('prefix', str(instance)),
            ('vrf', vrf),
        ])


#
# IP addresses
#

class IPAddressInterfaceSerializer(WritableNestedSerializer):
    url = serializers.SerializerMethodField()  # We're imitating a HyperlinkedIdentityField here
    device = NestedDeviceSerializer(read_only=True)
    virtual_machine = NestedVirtualMachineSerializer(read_only=True)

    class Meta(InterfaceSerializer.Meta):
        model = Interface
        fields = [
            'id', 'url', 'device', 'virtual_machine', 'name',
        ]

    def get_url(self, obj):
        """
        Return a link to the Interface via either the DCIM API if the parent is a Device, or via the virtualization API
        if the parent is a VirtualMachine.
        """
        url_name = 'dcim-api:interface-detail' if obj.device else 'virtualization-api:interface-detail'
        return reverse(url_name, kwargs={'pk': obj.pk}, request=self.context['request'])


class IPAddressSerializer(TaggitSerializer, CustomFieldModelSerializer):
    vrf = NestedVRFSerializer(required=False, allow_null=True)
    tenant = NestedTenantSerializer(required=False, allow_null=True)
    status = ChoiceField(choices=IPADDRESS_STATUS_CHOICES, required=False)
    role = ChoiceField(choices=IPADDRESS_ROLE_CHOICES, required=False, allow_null=True)
    interface = IPAddressInterfaceSerializer(required=False, allow_null=True)
    tags = TagListSerializerField(required=False)

    class Meta:
        model = IPAddress
        fields = [
            'id', 'family', 'address', 'vrf', 'tenant', 'status', 'role', 'interface', 'description', 'nat_inside',
            'nat_outside', 'tags', 'custom_fields', 'created', 'last_updated',
        ]
        read_only_fields = ['family']


class NestedIPAddressSerializer(WritableNestedSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='ipam-api:ipaddress-detail')

    class Meta:
        model = IPAddress
        fields = ['id', 'url', 'family', 'address']


IPAddressSerializer._declared_fields['nat_inside'] = NestedIPAddressSerializer(required=False, allow_null=True)
IPAddressSerializer._declared_fields['nat_outside'] = NestedIPAddressSerializer(read_only=True)


class AvailableIPSerializer(serializers.Serializer):

    def to_representation(self, instance):
        if self.context.get('vrf'):
            vrf = NestedVRFSerializer(self.context['vrf'], context={'request': self.context['request']}).data
        else:
            vrf = None
        return OrderedDict([
            ('family', self.context['prefix'].version),
            ('address', '{}/{}'.format(instance, self.context['prefix'].prefixlen)),
            ('vrf', vrf),
        ])


#
# Services
#

class ServiceSerializer(CustomFieldModelSerializer):
    device = NestedDeviceSerializer(required=False, allow_null=True)
    virtual_machine = NestedVirtualMachineSerializer(required=False, allow_null=True)
    protocol = ChoiceField(choices=IP_PROTOCOL_CHOICES)
    ipaddresses = SerializedPKRelatedField(
        queryset=IPAddress.objects.all(),
        serializer=NestedIPAddressSerializer,
        required=False,
        many=True
    )

    class Meta:
        model = Service
        fields = [
            'id', 'device', 'virtual_machine', 'name', 'port', 'protocol', 'ipaddresses', 'description',
            'custom_fields', 'created', 'last_updated',
        ]
