from collections import OrderedDict

from rest_framework import serializers
from rest_framework.reverse import reverse
from rest_framework.validators import UniqueTogetherValidator
from taggit_serializer.serializers import TaggitSerializer, TagListSerializerField

from dcim.api.nested_serializers import NestedDeviceSerializer, NestedSiteSerializer
from dcim.models import Interface
from extras.api.customfields import CustomFieldModelSerializer
from ipam.choices import *
from ipam.models import Aggregate, IPAddress, Prefix, RIR, Role, Service, VLAN, VLANGroup, VRF
from tenancy.api.nested_serializers import NestedTenantSerializer
from utilities.api import (
    ChoiceField, SerializedPKRelatedField, ValidatedModelSerializer, WritableNestedSerializer,
)
from virtualization.api.nested_serializers import NestedVirtualMachineSerializer
from .nested_serializers import *


#
# VRFs
#

class VRFSerializer(TaggitSerializer, CustomFieldModelSerializer):
    tenant = NestedTenantSerializer(required=False, allow_null=True)
    tags = TagListSerializerField(required=False)
    ipaddress_count = serializers.IntegerField(read_only=True)
    prefix_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = VRF
        fields = [
            'id', 'name', 'rd', 'tenant', 'enforce_unique', 'description', 'tags', 'display_name', 'custom_fields',
            'created', 'last_updated', 'ipaddress_count', 'prefix_count',
        ]


#
# RIRs/aggregates
#

class RIRSerializer(ValidatedModelSerializer):
    aggregate_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = RIR
        fields = ['id', 'name', 'slug', 'is_private', 'description', 'aggregate_count']


class AggregateSerializer(TaggitSerializer, CustomFieldModelSerializer):
    family = ChoiceField(choices=IPAddressFamilyChoices, read_only=True)
    rir = NestedRIRSerializer()
    tags = TagListSerializerField(required=False)

    class Meta:
        model = Aggregate
        fields = [
            'id', 'family', 'prefix', 'rir', 'date_added', 'description', 'tags', 'custom_fields', 'created',
            'last_updated',
        ]
        read_only_fields = ['family']


#
# VLANs
#

class RoleSerializer(ValidatedModelSerializer):
    prefix_count = serializers.IntegerField(read_only=True)
    vlan_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Role
        fields = ['id', 'name', 'slug', 'weight', 'description', 'prefix_count', 'vlan_count']


class VLANGroupSerializer(ValidatedModelSerializer):
    site = NestedSiteSerializer(required=False, allow_null=True)
    vlan_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = VLANGroup
        fields = ['id', 'name', 'slug', 'site', 'description', 'vlan_count']
        validators = []

    def validate(self, data):

        # Validate uniqueness of name and slug if a site has been assigned.
        if data.get('site', None):
            for field in ['name', 'slug']:
                validator = UniqueTogetherValidator(queryset=VLANGroup.objects.all(), fields=('site', field))
                validator.set_context(self)
                validator(data)

        # Enforce model validation
        super().validate(data)

        return data


class VLANSerializer(TaggitSerializer, CustomFieldModelSerializer):
    site = NestedSiteSerializer(required=False, allow_null=True)
    group = NestedVLANGroupSerializer(required=False, allow_null=True)
    tenant = NestedTenantSerializer(required=False, allow_null=True)
    status = ChoiceField(choices=VLANStatusChoices, required=False)
    role = NestedRoleSerializer(required=False, allow_null=True)
    tags = TagListSerializerField(required=False)
    prefix_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = VLAN
        fields = [
            'id', 'site', 'group', 'vid', 'name', 'tenant', 'status', 'role', 'description', 'tags', 'display_name',
            'custom_fields', 'created', 'last_updated', 'prefix_count',
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
        super().validate(data)

        return data


#
# Prefixes
#

class PrefixSerializer(TaggitSerializer, CustomFieldModelSerializer):
    family = ChoiceField(choices=IPAddressFamilyChoices, read_only=True)
    site = NestedSiteSerializer(required=False, allow_null=True)
    vrf = NestedVRFSerializer(required=False, allow_null=True)
    tenant = NestedTenantSerializer(required=False, allow_null=True)
    vlan = NestedVLANSerializer(required=False, allow_null=True)
    status = ChoiceField(choices=PrefixStatusChoices, required=False)
    role = NestedRoleSerializer(required=False, allow_null=True)
    tags = TagListSerializerField(required=False)

    class Meta:
        model = Prefix
        fields = [
            'id', 'family', 'prefix', 'site', 'vrf', 'tenant', 'vlan', 'status', 'role', 'is_pool', 'description',
            'tags', 'custom_fields', 'created', 'last_updated',
        ]
        read_only_fields = ['family']


class PrefixLengthSerializer(serializers.Serializer):

    prefix_length = serializers.IntegerField()

    def to_internal_value(self, data):
        requested_prefix = data.get('prefix_length')
        if requested_prefix is None:
            raise serializers.ValidationError({
                'prefix_length': 'this field can not be missing'
            })
        if not isinstance(requested_prefix, int):
            raise serializers.ValidationError({
                'prefix_length': 'this field must be int type'
            })

        prefix = self.context.get('prefix')
        if prefix.family == 4 and requested_prefix > 32:
            raise serializers.ValidationError({
                'prefix_length': 'Invalid prefix length ({}) for IPv4'.format((requested_prefix))
            })
        elif prefix.family == 6 and requested_prefix > 128:
            raise serializers.ValidationError({
                'prefix_length': 'Invalid prefix length ({}) for IPv6'.format((requested_prefix))
            })
        return data


class AvailablePrefixSerializer(serializers.Serializer):
    """
    Representation of a prefix which does not exist in the database.
    """
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
    """
    Nested representation of an Interface which may belong to a Device *or* a VirtualMachine.
    """
    url = serializers.SerializerMethodField()  # We're imitating a HyperlinkedIdentityField here
    device = NestedDeviceSerializer(read_only=True)
    virtual_machine = NestedVirtualMachineSerializer(read_only=True)

    class Meta:
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
    family = ChoiceField(choices=IPAddressFamilyChoices, read_only=True)
    vrf = NestedVRFSerializer(required=False, allow_null=True)
    tenant = NestedTenantSerializer(required=False, allow_null=True)
    status = ChoiceField(choices=IPAddressStatusChoices, required=False)
    role = ChoiceField(choices=IPAddressRoleChoices, allow_blank=True, required=False)
    interface = IPAddressInterfaceSerializer(required=False, allow_null=True)
    nat_inside = NestedIPAddressSerializer(required=False, allow_null=True)
    nat_outside = NestedIPAddressSerializer(read_only=True)
    tags = TagListSerializerField(required=False)

    class Meta:
        model = IPAddress
        fields = [
            'id', 'family', 'address', 'vrf', 'tenant', 'status', 'role', 'interface', 'nat_inside',
            'nat_outside', 'dns_name', 'description', 'tags', 'custom_fields', 'created', 'last_updated',
        ]
        read_only_fields = ['family']


class AvailableIPSerializer(serializers.Serializer):
    """
    Representation of an IP address which does not exist in the database.
    """
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

class ServiceSerializer(TaggitSerializer, CustomFieldModelSerializer):
    device = NestedDeviceSerializer(required=False, allow_null=True)
    virtual_machine = NestedVirtualMachineSerializer(required=False, allow_null=True)
    protocol = ChoiceField(choices=ServiceProtocolChoices, required=False)
    ipaddresses = SerializedPKRelatedField(
        queryset=IPAddress.objects.all(),
        serializer=NestedIPAddressSerializer,
        required=False,
        many=True
    )
    tags = TagListSerializerField(required=False)

    class Meta:
        model = Service
        fields = [
            'id', 'device', 'virtual_machine', 'name', 'port', 'protocol', 'ipaddresses', 'description', 'tags',
            'custom_fields', 'created', 'last_updated',
        ]
