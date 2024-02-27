from django.contrib.contenttypes.models import ContentType
from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from dcim.api.serializers_.sites import SiteSerializer
from ipam.choices import *
from ipam.constants import IPADDRESS_ASSIGNMENT_MODELS
from ipam.models import Aggregate, IPAddress, IPRange, Prefix
from netbox.api.fields import ChoiceField, ContentTypeField
from netbox.api.serializers import NetBoxModelSerializer
from tenancy.api.serializers_.tenants import TenantSerializer
from utilities.api import get_serializer_for_model
from .asns import RIRSerializer
from .roles import RoleSerializer
from .vlans import VLANSerializer
from .vrfs import VRFSerializer
from ..field_serializers import IPAddressField, IPNetworkField
from ..nested_serializers import *

__all__ = (
    'AggregateSerializer',
    'AvailableIPSerializer',
    'AvailablePrefixSerializer',
    'IPAddressSerializer',
    'IPRangeSerializer',
    'PrefixLengthSerializer',
    'PrefixSerializer',
)


class AggregateSerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='ipam-api:aggregate-detail')
    family = ChoiceField(choices=IPAddressFamilyChoices, read_only=True)
    rir = RIRSerializer(nested=True)
    tenant = TenantSerializer(nested=True, required=False, allow_null=True)
    prefix = IPNetworkField()

    class Meta:
        model = Aggregate
        fields = [
            'id', 'url', 'display', 'family', 'prefix', 'rir', 'tenant', 'date_added', 'description', 'comments',
            'tags', 'custom_fields', 'created', 'last_updated',
        ]
        brief_fields = ('id', 'url', 'display', 'family', 'prefix', 'description')


class PrefixSerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='ipam-api:prefix-detail')
    family = ChoiceField(choices=IPAddressFamilyChoices, read_only=True)
    site = SiteSerializer(nested=True, required=False, allow_null=True)
    vrf = VRFSerializer(nested=True, required=False, allow_null=True)
    tenant = TenantSerializer(nested=True, required=False, allow_null=True)
    vlan = VLANSerializer(nested=True, required=False, allow_null=True)
    status = ChoiceField(choices=PrefixStatusChoices, required=False)
    role = RoleSerializer(nested=True, required=False, allow_null=True)
    children = serializers.IntegerField(read_only=True)
    _depth = serializers.IntegerField(read_only=True)
    prefix = IPNetworkField()

    class Meta:
        model = Prefix
        fields = [
            'id', 'url', 'display', 'family', 'prefix', 'site', 'vrf', 'tenant', 'vlan', 'status', 'role', 'is_pool',
            'mark_utilized', 'description', 'comments', 'tags', 'custom_fields', 'created', 'last_updated', 'children',
            '_depth',
        ]
        brief_fields = ('id', 'url', 'display', 'family', 'prefix', 'description', '_depth')


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
                'prefix_length': 'Invalid prefix length ({}) for IPv4'.format(requested_prefix)
            })
        elif prefix.family == 6 and requested_prefix > 128:
            raise serializers.ValidationError({
                'prefix_length': 'Invalid prefix length ({}) for IPv6'.format(requested_prefix)
            })
        return data


class AvailablePrefixSerializer(serializers.Serializer):
    """
    Representation of a prefix which does not exist in the database.
    """
    family = serializers.IntegerField(read_only=True)
    prefix = serializers.CharField(read_only=True)
    vrf = VRFSerializer(nested=True, read_only=True)

    def to_representation(self, instance):
        if self.context.get('vrf'):
            vrf = VRFSerializer(self.context['vrf'], nested=True, context={'request': self.context['request']}).data
        else:
            vrf = None
        return {
            'family': instance.version,
            'prefix': str(instance),
            'vrf': vrf,
        }


#
# IP ranges
#

class IPRangeSerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='ipam-api:iprange-detail')
    family = ChoiceField(choices=IPAddressFamilyChoices, read_only=True)
    start_address = IPAddressField()
    end_address = IPAddressField()
    vrf = VRFSerializer(nested=True, required=False, allow_null=True)
    tenant = TenantSerializer(nested=True, required=False, allow_null=True)
    status = ChoiceField(choices=IPRangeStatusChoices, required=False)
    role = RoleSerializer(nested=True, required=False, allow_null=True)

    class Meta:
        model = IPRange
        fields = [
            'id', 'url', 'display', 'family', 'start_address', 'end_address', 'size', 'vrf', 'tenant', 'status', 'role',
            'description', 'comments', 'tags', 'custom_fields', 'created', 'last_updated',
            'mark_utilized', 'description', 'comments', 'tags', 'custom_fields', 'created', 'last_updated',
        ]
        brief_fields = ('id', 'url', 'display', 'family', 'start_address', 'end_address', 'description')


#
# IP addresses
#

class IPAddressSerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='ipam-api:ipaddress-detail')
    family = ChoiceField(choices=IPAddressFamilyChoices, read_only=True)
    address = IPAddressField()
    vrf = VRFSerializer(nested=True, required=False, allow_null=True)
    tenant = TenantSerializer(nested=True, required=False, allow_null=True)
    status = ChoiceField(choices=IPAddressStatusChoices, required=False)
    role = ChoiceField(choices=IPAddressRoleChoices, allow_blank=True, required=False)
    assigned_object_type = ContentTypeField(
        queryset=ContentType.objects.filter(IPADDRESS_ASSIGNMENT_MODELS),
        required=False,
        allow_null=True
    )
    assigned_object = serializers.SerializerMethodField(read_only=True)
    nat_inside = NestedIPAddressSerializer(required=False, allow_null=True)
    nat_outside = NestedIPAddressSerializer(many=True, read_only=True)

    class Meta:
        model = IPAddress
        fields = [
            'id', 'url', 'display', 'family', 'address', 'vrf', 'tenant', 'status', 'role', 'assigned_object_type',
            'assigned_object_id', 'assigned_object', 'nat_inside', 'nat_outside', 'dns_name', 'description', 'comments',
            'tags', 'custom_fields', 'created', 'last_updated',
        ]
        brief_fields = ('id', 'url', 'display', 'family', 'address', 'description')

    @extend_schema_field(serializers.JSONField(allow_null=True))
    def get_assigned_object(self, obj):
        if obj.assigned_object is None:
            return None
        serializer = get_serializer_for_model(obj.assigned_object)
        context = {'request': self.context['request']}
        return serializer(obj.assigned_object, nested=True, context=context).data


class AvailableIPSerializer(serializers.Serializer):
    """
    Representation of an IP address which does not exist in the database.
    """
    family = serializers.IntegerField(read_only=True)
    address = serializers.CharField(read_only=True)
    vrf = VRFSerializer(nested=True, read_only=True)
    description = serializers.CharField(required=False)

    def to_representation(self, instance):
        if self.context.get('vrf'):
            vrf = VRFSerializer(self.context['vrf'], nested=True, context={'request': self.context['request']}).data
        else:
            vrf = None
        return {
            'family': self.context['parent'].family,
            'address': f"{instance}/{self.context['parent'].mask_length}",
            'vrf': vrf,
        }
