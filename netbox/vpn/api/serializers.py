from django.contrib.contenttypes.models import ContentType
from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from ipam.api.nested_serializers import NestedIPAddressSerializer
from netbox.api.fields import ChoiceField, ContentTypeField, SerializedPKRelatedField
from netbox.api.serializers import NetBoxModelSerializer
from netbox.constants import NESTED_SERIALIZER_PREFIX
from tenancy.api.nested_serializers import NestedTenantSerializer
from utilities.api import get_serializer_for_model
from vpn.choices import *
from vpn.models import *
from .nested_serializers import *

__all__ = (
    'IKEPolicySerializer',
    'IKEProposalSerializer',
    'IPSecPolicySerializer',
    'IPSecProfileSerializer',
    'IPSecProposalSerializer',
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
            'id', 'url', 'display', 'name', 'status', 'encapsulation', 'ipsec_profile', 'tenant', 'tunnel_id',
            'comments', 'tags', 'custom_fields', 'created', 'last_updated',
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


class IKEProposalSerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name='vpn-api:ikeproposal-detail'
    )
    authentication_method = ChoiceField(
        choices=AuthenticationMethodChoices
    )
    encryption_algorithm = ChoiceField(
        choices=EncryptionAlgorithmChoices
    )
    authentication_algorithm = ChoiceField(
        choices=AuthenticationAlgorithmChoices
    )
    group = ChoiceField(
        choices=DHGroupChoices
    )

    class Meta:
        model = IKEProposal
        fields = (
            'id', 'url', 'display', 'name', 'description', 'authentication_method', 'encryption_algorithm',
            'authentication_algorithm', 'group', 'sa_lifetime', 'tags', 'custom_fields', 'created', 'last_updated',
        )


class IKEPolicySerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name='vpn-api:ikepolicy-detail'
    )
    version = ChoiceField(
        choices=IKEVersionChoices
    )
    mode = ChoiceField(
        choices=IKEModeChoices
    )
    authentication_algorithm = ChoiceField(
        choices=AuthenticationAlgorithmChoices
    )
    group = ChoiceField(
        choices=DHGroupChoices
    )
    proposals = SerializedPKRelatedField(
        queryset=IKEProposal.objects.all(),
        serializer=NestedIKEProposalSerializer,
        required=False,
        many=True
    )

    class Meta:
        model = IKEPolicy
        fields = (
            'id', 'url', 'display', 'name', 'description', 'version', 'mode', 'proposals', 'preshared_key',
            'certificate', 'tags', 'custom_fields', 'created', 'last_updated',
        )


class IPSecProposalSerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name='vpn-api:ipsecproposal-detail'
    )
    encryption_algorithm = ChoiceField(
        choices=EncryptionAlgorithmChoices
    )
    authentication_algorithm = ChoiceField(
        choices=AuthenticationAlgorithmChoices
    )
    group = ChoiceField(
        choices=DHGroupChoices
    )

    class Meta:
        model = IPSecProposal
        fields = (
            'id', 'url', 'display', 'name', 'description', 'encryption_algorithm', 'authentication_algorithm',
            'sa_lifetime_data', 'sa_lifetime_seconds', 'tags', 'custom_fields', 'created', 'last_updated',
        )


class IPSecPolicySerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name='vpn-api:ipsecpolicy-detail'
    )
    proposals = SerializedPKRelatedField(
        queryset=IPSecProposal.objects.all(),
        serializer=NestedIPSecProposalSerializer,
        required=False,
        many=True
    )
    pfs_group = ChoiceField(
        choices=DHGroupChoices
    )

    class Meta:
        model = IPSecPolicy
        fields = (
            'id', 'url', 'display', 'name', 'description', 'proposals', 'pfs_group', 'tags', 'custom_fields', 'created',
            'last_updated',
        )


class IPSecProfileSerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name='vpn-api:ipsecprofile-detail'
    )
    protocol = ChoiceField(
        choices=IPSecModeChoices
    )
    ike_version = ChoiceField(
        choices=IKEVersionChoices
    )
    phase1_encryption = ChoiceField(
        choices=EncryptionAlgorithmChoices
    )
    phase1_authentication = ChoiceField(
        choices=AuthenticationAlgorithmChoices
    )
    phase1_group = ChoiceField(
        choices=DHGroupChoices
    )
    phase2_encryption = ChoiceField(
        choices=EncryptionAlgorithmChoices
    )
    phase2_authentication = ChoiceField(
        choices=AuthenticationAlgorithmChoices
    )
    phase2_group = ChoiceField(
        choices=DHGroupChoices
    )

    class Meta:
        model = IPSecProfile
        fields = (
            'id', 'url', 'display', 'name', 'protocol', 'ike_version', 'phase1_encryption', 'phase1_authentication',
            'phase1_group', 'phase1_sa_lifetime', 'phase2_encryption', 'phase2_authentication', 'phase2_group',
            'phase2_sa_lifetime', 'phase2_sa_lifetime_data', 'comments', 'tags', 'custom_fields', 'created',
            'last_updated',
        )
