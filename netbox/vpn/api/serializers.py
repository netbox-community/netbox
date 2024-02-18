from django.contrib.contenttypes.models import ContentType
from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from ipam.api.nested_serializers import NestedIPAddressSerializer, NestedRouteTargetSerializer
from ipam.models import RouteTarget
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
    'L2VPNSerializer',
    'L2VPNTerminationSerializer',
    'TunnelGroupSerializer',
    'TunnelSerializer',
    'TunnelTerminationSerializer',
)


class TunnelGroupSerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='vpn-api:tunnelgroup-detail')
    tunnel_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = TunnelGroup
        fields = [
            'id', 'url', 'display', 'name', 'slug', 'description', 'tags', 'custom_fields', 'created', 'last_updated',
            'tunnel_count',
        ]


class TunnelSerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name='vpn-api:tunnel-detail'
    )
    status = ChoiceField(
        choices=TunnelStatusChoices
    )
    group = NestedTunnelGroupSerializer(
        required=False,
        allow_null=True
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
            'id', 'url', 'display', 'name', 'status', 'group', 'encapsulation', 'ipsec_profile', 'tenant', 'tunnel_id',
            'description', 'comments', 'tags', 'custom_fields', 'created', 'last_updated',
        )


class TunnelTerminationSerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name='vpn-api:tunneltermination-detail'
    )
    tunnel = NestedTunnelSerializer()
    role = ChoiceField(
        choices=TunnelTerminationRoleChoices
    )
    termination_type = ContentTypeField(
        queryset=ContentType.objects.all()
    )
    termination = serializers.SerializerMethodField(
        read_only=True
    )
    outside_ip = NestedIPAddressSerializer(
        required=False,
        allow_null=True
    )

    class Meta:
        model = TunnelTermination
        fields = (
            'id', 'url', 'display', 'tunnel', 'role', 'termination_type', 'termination_id', 'termination', 'outside_ip',
            'tags', 'custom_fields', 'created', 'last_updated',
        )

    @extend_schema_field(serializers.JSONField(allow_null=True))
    def get_termination(self, obj):
        serializer = get_serializer_for_model(obj.termination, prefix=NESTED_SERIALIZER_PREFIX)
        context = {'request': self.context['request']}
        return serializer(obj.termination, context=context).data


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
            'authentication_algorithm', 'group', 'sa_lifetime', 'comments', 'tags', 'custom_fields', 'created',
            'last_updated',
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
    proposals = SerializedPKRelatedField(
        queryset=IKEProposal.objects.all(),
        serializer=NestedIKEProposalSerializer,
        required=False,
        many=True
    )

    class Meta:
        model = IKEPolicy
        fields = (
            'id', 'url', 'display', 'name', 'description', 'version', 'mode', 'proposals', 'preshared_key', 'comments',
            'tags', 'custom_fields', 'created', 'last_updated',
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

    class Meta:
        model = IPSecProposal
        fields = (
            'id', 'url', 'display', 'name', 'description', 'encryption_algorithm', 'authentication_algorithm',
            'sa_lifetime_seconds', 'sa_lifetime_data', 'comments', 'tags', 'custom_fields', 'created', 'last_updated',
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
        choices=DHGroupChoices,
        required=False
    )

    class Meta:
        model = IPSecPolicy
        fields = (
            'id', 'url', 'display', 'name', 'description', 'proposals', 'pfs_group', 'comments', 'tags',
            'custom_fields', 'created', 'last_updated',
        )


class IPSecProfileSerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name='vpn-api:ipsecprofile-detail'
    )
    mode = ChoiceField(
        choices=IPSecModeChoices
    )
    ike_policy = NestedIKEPolicySerializer()
    ipsec_policy = NestedIPSecPolicySerializer()

    class Meta:
        model = IPSecProfile
        fields = (
            'id', 'url', 'display', 'name', 'description', 'mode', 'ike_policy', 'ipsec_policy', 'comments', 'tags',
            'custom_fields', 'created', 'last_updated',
        )


#
# L2VPN
#

class L2VPNSerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='vpn-api:l2vpn-detail')
    type = ChoiceField(choices=L2VPNTypeChoices, required=False)
    import_targets = SerializedPKRelatedField(
        queryset=RouteTarget.objects.all(),
        serializer=NestedRouteTargetSerializer,
        required=False,
        many=True
    )
    export_targets = SerializedPKRelatedField(
        queryset=RouteTarget.objects.all(),
        serializer=NestedRouteTargetSerializer,
        required=False,
        many=True
    )
    tenant = NestedTenantSerializer(required=False, allow_null=True)

    class Meta:
        model = L2VPN
        fields = [
            'id', 'url', 'display', 'identifier', 'name', 'slug', 'type', 'import_targets', 'export_targets',
            'description', 'comments', 'tenant', 'tags', 'custom_fields', 'created', 'last_updated'
        ]


class L2VPNTerminationSerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='vpn-api:l2vpntermination-detail')
    l2vpn = NestedL2VPNSerializer()
    assigned_object_type = ContentTypeField(
        queryset=ContentType.objects.all()
    )
    assigned_object = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = L2VPNTermination
        fields = [
            'id', 'url', 'display', 'l2vpn', 'assigned_object_type', 'assigned_object_id',
            'assigned_object', 'tags', 'custom_fields', 'created', 'last_updated'
        ]

    @extend_schema_field(serializers.JSONField(allow_null=True))
    def get_assigned_object(self, instance):
        serializer = get_serializer_for_model(instance.assigned_object, prefix=NESTED_SERIALIZER_PREFIX)
        context = {'request': self.context['request']}
        return serializer(instance.assigned_object, context=context).data
