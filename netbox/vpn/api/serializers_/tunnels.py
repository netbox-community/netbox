from django.contrib.contenttypes.models import ContentType
from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from ipam.api.serializers_.ip import IPAddressSerializer
from netbox.api.fields import ChoiceField, ContentTypeField, RelatedObjectCountField
from netbox.api.serializers import NetBoxModelSerializer
from tenancy.api.serializers_.tenants import TenantSerializer
from utilities.api import get_serializer_for_model
from vpn.choices import *
from vpn.models import Tunnel, TunnelGroup, TunnelTermination
from .crypto import IPSecProfileSerializer

__all__ = (
    'TunnelGroupSerializer',
    'TunnelSerializer',
    'TunnelTerminationSerializer',
)


#
# Tunnels
#

class TunnelGroupSerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='vpn-api:tunnelgroup-detail')

    # Related object counts
    tunnel_count = RelatedObjectCountField('tunnels')

    class Meta:
        model = TunnelGroup
        fields = [
            'id', 'url', 'display', 'name', 'slug', 'description', 'tags', 'custom_fields', 'created', 'last_updated',
            'tunnel_count',
        ]
        brief_fields = ('id', 'url', 'display', 'name', 'slug', 'description', 'tunnel_count')


class TunnelSerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name='vpn-api:tunnel-detail'
    )
    status = ChoiceField(
        choices=TunnelStatusChoices
    )
    group = TunnelGroupSerializer(
        nested=True,
        required=False,
        allow_null=True,
        default=None
    )
    encapsulation = ChoiceField(
        choices=TunnelEncapsulationChoices
    )
    ipsec_profile = IPSecProfileSerializer(
        nested=True,
        required=False,
        allow_null=True
    )
    tenant = TenantSerializer(
        nested=True,
        required=False,
        allow_null=True
    )

    # Related object counts
    terminations_count = RelatedObjectCountField('terminations')

    class Meta:
        model = Tunnel
        fields = (
            'id', 'url', 'display', 'name', 'status', 'group', 'encapsulation', 'ipsec_profile', 'tenant', 'tunnel_id',
            'description', 'comments', 'tags', 'custom_fields', 'created', 'last_updated', 'terminations_count',
        )
        brief_fields = ('id', 'url', 'display', 'name', 'description')


class TunnelTerminationSerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name='vpn-api:tunneltermination-detail'
    )
    tunnel = TunnelSerializer(
        nested=True
    )
    role = ChoiceField(
        choices=TunnelTerminationRoleChoices
    )
    termination_type = ContentTypeField(
        queryset=ContentType.objects.all()
    )
    termination = serializers.SerializerMethodField(
        read_only=True
    )
    outside_ip = IPAddressSerializer(
        nested=True,
        required=False,
        allow_null=True
    )

    class Meta:
        model = TunnelTermination
        fields = (
            'id', 'url', 'display', 'tunnel', 'role', 'termination_type', 'termination_id', 'termination', 'outside_ip',
            'tags', 'custom_fields', 'created', 'last_updated',
        )
        brief_fields = ('id', 'url', 'display')

    @extend_schema_field(serializers.JSONField(allow_null=True))
    def get_termination(self, obj):
        serializer = get_serializer_for_model(obj.termination)
        context = {'request': self.context['request']}
        return serializer(obj.termination, nested=True, context=context).data
