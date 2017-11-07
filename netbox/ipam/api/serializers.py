from __future__ import unicode_literals

from collections import OrderedDict

from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from dcim.api.serializers import NestedDeviceSerializer, InterfaceSerializer, NestedSiteSerializer
from extras.api.customfields import CustomFieldModelSerializer
from ipam.constants import (
    IPADDRESS_ROLE_CHOICES, IPADDRESS_STATUS_CHOICES, IP_PROTOCOL_CHOICES, PREFIX_STATUS_CHOICES, VLAN_STATUS_CHOICES,
)
from ipam.models import Aggregate, IPAddress, Prefix, RIR, Role, Service, VLAN, VLANGroup, VRF
from tenancy.api.serializers import NestedTenantSerializer
from utilities.api import ChoiceFieldSerializer, ValidatedModelSerializer
from virtualization.api.serializers import NestedVirtualMachineSerializer


#
# VRFs
#

class VRFSerializer(CustomFieldModelSerializer):
    tenant = NestedTenantSerializer()

    class Meta:
        model = VRF
        fields = ['id', 'name', 'rd', 'tenant', 'enforce_unique', 'description', 'display_name', 'custom_fields']


class NestedVRFSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='ipam-api:vrf-detail')

    class Meta:
        model = VRF
        fields = ['id', 'url', 'name', 'rd']


class WritableVRFSerializer(CustomFieldModelSerializer):

    class Meta:
        model = VRF
        fields = ['id', 'name', 'rd', 'tenant', 'enforce_unique', 'description', 'custom_fields']


#
# Roles
#

class RoleSerializer(ValidatedModelSerializer):

    class Meta:
        model = Role
        fields = ['id', 'name', 'slug', 'weight']


class NestedRoleSerializer(serializers.ModelSerializer):
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


class NestedRIRSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='ipam-api:rir-detail')

    class Meta:
        model = RIR
        fields = ['id', 'url', 'name', 'slug']


#
# Aggregates
#

class AggregateSerializer(CustomFieldModelSerializer):
    rir = NestedRIRSerializer()

    class Meta:
        model = Aggregate
        fields = ['id', 'family', 'prefix', 'rir', 'date_added', 'description', 'custom_fields']


class NestedAggregateSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='ipam-api:aggregate-detail')

    class Meta(AggregateSerializer.Meta):
        model = Aggregate
        fields = ['id', 'url', 'family', 'prefix']


class WritableAggregateSerializer(CustomFieldModelSerializer):

    class Meta:
        model = Aggregate
        fields = ['id', 'prefix', 'rir', 'date_added', 'description', 'custom_fields']


#
# VLAN groups
#

class VLANGroupSerializer(serializers.ModelSerializer):
    site = NestedSiteSerializer()

    class Meta:
        model = VLANGroup
        fields = ['id', 'name', 'slug', 'site']


class NestedVLANGroupSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='ipam-api:vlangroup-detail')

    class Meta:
        model = VLANGroup
        fields = ['id', 'url', 'name', 'slug']


class WritableVLANGroupSerializer(serializers.ModelSerializer):

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
        super(WritableVLANGroupSerializer, self).validate(data)

        return data


#
# VLANs
#

class VLANSerializer(CustomFieldModelSerializer):
    site = NestedSiteSerializer()
    group = NestedVLANGroupSerializer()
    tenant = NestedTenantSerializer()
    status = ChoiceFieldSerializer(choices=VLAN_STATUS_CHOICES)
    role = NestedRoleSerializer()

    class Meta:
        model = VLAN
        fields = [
            'id', 'site', 'group', 'vid', 'name', 'tenant', 'status', 'role', 'description', 'display_name',
            'custom_fields',
        ]


class NestedVLANSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='ipam-api:vlan-detail')

    class Meta:
        model = VLAN
        fields = ['id', 'url', 'vid', 'name', 'display_name']


class WritableVLANSerializer(CustomFieldModelSerializer):

    class Meta:
        model = VLAN
        fields = ['id', 'site', 'group', 'vid', 'name', 'tenant', 'status', 'role', 'description', 'custom_fields']
        validators = []

    def validate(self, data):

        # Validate uniqueness of vid and name if a group has been assigned.
        if data.get('group', None):
            for field in ['vid', 'name']:
                validator = UniqueTogetherValidator(queryset=VLAN.objects.all(), fields=('group', field))
                validator.set_context(self)
                validator(data)

        # Enforce model validation
        super(WritableVLANSerializer, self).validate(data)

        return data


#
# Prefixes
#

class PrefixSerializer(CustomFieldModelSerializer):
    site = NestedSiteSerializer()
    vrf = NestedVRFSerializer()
    tenant = NestedTenantSerializer()
    vlan = NestedVLANSerializer()
    status = ChoiceFieldSerializer(choices=PREFIX_STATUS_CHOICES)
    role = NestedRoleSerializer()

    class Meta:
        model = Prefix
        fields = [
            'id', 'family', 'prefix', 'site', 'vrf', 'tenant', 'vlan', 'status', 'role', 'is_pool', 'description',
            'custom_fields',
        ]


class NestedPrefixSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='ipam-api:prefix-detail')

    class Meta:
        model = Prefix
        fields = ['id', 'url', 'family', 'prefix']


class WritablePrefixSerializer(CustomFieldModelSerializer):

    class Meta:
        model = Prefix
        fields = [
            'id', 'prefix', 'site', 'vrf', 'tenant', 'vlan', 'status', 'role', 'is_pool', 'description',
            'custom_fields',
        ]


#
# IP addresses
#

class IPAddressInterfaceSerializer(InterfaceSerializer):
    virtual_machine = NestedVirtualMachineSerializer()

    class Meta(InterfaceSerializer.Meta):
        fields = [
            'id', 'device', 'virtual_machine', 'name', 'form_factor', 'enabled', 'lag', 'mtu', 'mac_address',
            'mgmt_only', 'description', 'is_connected', 'interface_connection', 'circuit_termination',
        ]


class IPAddressSerializer(CustomFieldModelSerializer):
    vrf = NestedVRFSerializer()
    tenant = NestedTenantSerializer()
    status = ChoiceFieldSerializer(choices=IPADDRESS_STATUS_CHOICES)
    role = ChoiceFieldSerializer(choices=IPADDRESS_ROLE_CHOICES)
    interface = IPAddressInterfaceSerializer()

    class Meta:
        model = IPAddress
        fields = [
            'id', 'family', 'address', 'vrf', 'tenant', 'status', 'role', 'interface', 'description', 'nat_inside',
            'nat_outside', 'custom_fields',
        ]


class NestedIPAddressSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='ipam-api:ipaddress-detail')

    class Meta:
        model = IPAddress
        fields = ['id', 'url', 'family', 'address']


IPAddressSerializer._declared_fields['nat_inside'] = NestedIPAddressSerializer()
IPAddressSerializer._declared_fields['nat_outside'] = NestedIPAddressSerializer()


class WritableIPAddressSerializer(CustomFieldModelSerializer):

    class Meta:
        model = IPAddress
        fields = [
            'id', 'address', 'vrf', 'tenant', 'status', 'role', 'interface', 'description', 'nat_inside',
            'custom_fields',
        ]


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

class ServiceSerializer(serializers.ModelSerializer):
    device = NestedDeviceSerializer()
    virtual_machine = NestedVirtualMachineSerializer()
    protocol = ChoiceFieldSerializer(choices=IP_PROTOCOL_CHOICES)
    ipaddresses = NestedIPAddressSerializer(many=True)

    class Meta:
        model = Service
        fields = ['id', 'device', 'virtual_machine', 'name', 'port', 'protocol', 'ipaddresses', 'description']


# TODO: Figure out how to use model validation with ManyToManyFields. Calling clean() yields a ValueError.
class WritableServiceSerializer(serializers.ModelSerializer):

    class Meta:
        model = Service
        fields = ['id', 'device', 'virtual_machine', 'name', 'port', 'protocol', 'ipaddresses', 'description']
