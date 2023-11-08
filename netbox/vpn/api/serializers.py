from django.contrib.contenttypes.models import ContentType
from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from ipam.api.nested_serializers import NestedIPAddressSerializer
from netbox.api.fields import ChoiceField, ContentTypeField
from netbox.api.serializers import NetBoxModelSerializer
from netbox.constants import NESTED_SERIALIZER_PREFIX
from tenancy.api.nested_serializers import NestedTenantSerializer
from utilities.api import get_serializer_for_model
from vpn.choices import *
from vpn.models import *
from .nested_serializers import *

__all__ = (
    'IPSecProfileSerializer',
    'TunnelSerializer',
    'TunnelTerminationSerializer',
)


class TunnelSerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name='vpn-api:tunnel-detail'
    )
    status = ChoiceField(
        choices=TunnelStatusChoices
    )
    encapsulation = ChoiceField(
        choices=TunnelEncapsulationChoices
    )
    ipsec_profile = NestedIPSecProfileSerializer(
        required=False,
        allow_null=True
    )
    tenant = NestedTenantSerializer(
        required=False,
        allow_null=True
    )

    class Meta:
        model = Tunnel
        fields = (
            'id', 'url', 'display', 'name', 'status', 'encapsulation', 'ipsec_profile', 'tenant', 'preshared_key',
            'tunnel_id', 'comments', 'tags', 'custom_fields', 'created', 'last_updated',
        )


class TunnelTerminationSerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name='vpn-api:tunneltermination-detail'
    )
    tunnel = NestedTunnelSerializer()
    role = ChoiceField(
        choices=TunnelTerminationRoleChoices
    )
    interface_type = ContentTypeField(
        queryset=ContentType.objects.all()
    )
    interface = serializers.SerializerMethodField(
        read_only=True
    )
    outside_ip = NestedIPAddressSerializer(
        required=False,
        allow_null=True
    )

    class Meta:
        model = TunnelTermination
        fields = (
            'id', 'url', 'display', 'tunnel', 'role', 'interface_type', 'interface_id', 'interface', 'outside_ip',
            'tags', 'custom_fields', 'created', 'last_updated',
        )

    @extend_schema_field(serializers.JSONField(allow_null=True))
    def get_interface(self, obj):
        serializer = get_serializer_for_model(obj.interface, prefix=NESTED_SERIALIZER_PREFIX)
        context = {'request': self.context['request']}
        return serializer(obj.interface, context=context).data


class IPSecProfileSerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name='vpn-api:ipsecprofile-detail'
    )
    protocol = ChoiceField(
        choices=IPSecProtocolChoices
    )
    ike_version = ChoiceField(
        choices=IKEVersionChoices
    )
    phase1_encryption = ChoiceField(
        choices=EncryptionChoices
    )
    phase1_authentication = ChoiceField(
        choices=AuthenticationChoices
    )
    phase1_group = ChoiceField(
        choices=DHGroupChoices
    )
    phase2_encryption = ChoiceField(
        choices=EncryptionChoices
    )
    phase2_authentication = ChoiceField(
        choices=AuthenticationChoices
    )
    phase2_group = ChoiceField(
        choices=DHGroupChoices
    )

    class Meta:
        model = IPSecProfile
        fields = (
            'id', 'url', 'display', 'name', 'protocol', 'ike_version', 'phase1_encryption', 'phase1_authentication',
            'phase1_group', 'phase1_sa_lifetime', 'phase2_encryption', 'phase2_authentication', 'phase2_group',
            'phase2_sa_lifetime', 'comments', 'tags', 'custom_fields', 'created', 'last_updated',
        )
