from rest_framework import serializers

from netbox.api.fields import ChoiceField, SerializedPKRelatedField
from netbox.api.serializers import NetBoxModelSerializer
from vpn.choices import *
from vpn.models import IKEPolicy, IKEProposal, IPSecPolicy, IPSecProfile, IPSecProposal

__all__ = (
    'IKEPolicySerializer',
    'IKEProposalSerializer',
    'IPSecPolicySerializer',
    'IPSecProfileSerializer',
    'IPSecProposalSerializer',
)


class IKEProposalSerializer(NetBoxModelSerializer):
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
            'id', 'url', 'display_url', 'display', 'name', 'description', 'authentication_method',
            'encryption_algorithm', 'authentication_algorithm', 'group', 'sa_lifetime', 'comments', 'tags',
            'custom_fields', 'created', 'last_updated',
        )
        brief_fields = ('id', 'url', 'display', 'name', 'description')


class IKEPolicySerializer(NetBoxModelSerializer):
    version = ChoiceField(
        choices=IKEVersionChoices
    )
    mode = ChoiceField(
        choices=IKEModeChoices
    )
    proposals = SerializedPKRelatedField(
        queryset=IKEProposal.objects.all(),
        serializer=IKEProposalSerializer,
        nested=True,
        required=False,
        many=True
    )

    class Meta:
        model = IKEPolicy
        fields = (
            'id', 'url', 'display_url', 'display', 'name', 'description', 'version', 'mode', 'proposals',
            'preshared_key', 'comments', 'tags', 'custom_fields', 'created', 'last_updated',
        )
        brief_fields = ('id', 'url', 'display', 'name', 'description')


class IPSecProposalSerializer(NetBoxModelSerializer):
    encryption_algorithm = ChoiceField(
        choices=EncryptionAlgorithmChoices
    )
    authentication_algorithm = ChoiceField(
        choices=AuthenticationAlgorithmChoices
    )

    class Meta:
        model = IPSecProposal
        fields = (
            'id', 'url', 'display_url', 'display', 'name', 'description', 'encryption_algorithm',
            'authentication_algorithm', 'sa_lifetime_seconds', 'sa_lifetime_data', 'comments', 'tags', 'custom_fields', 'created', 'last_updated',
        )
        brief_fields = ('id', 'url', 'display', 'name', 'description')


class IPSecPolicySerializer(NetBoxModelSerializer):
    proposals = SerializedPKRelatedField(
        queryset=IPSecProposal.objects.all(),
        serializer=IPSecProposalSerializer,
        nested=True,
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
            'id', 'url', 'display_url', 'display', 'name', 'description', 'proposals', 'pfs_group', 'comments', 'tags',
            'custom_fields', 'created', 'last_updated',
        )
        brief_fields = ('id', 'url', 'display', 'name', 'description')


class IPSecProfileSerializer(NetBoxModelSerializer):
    mode = ChoiceField(
        choices=IPSecModeChoices
    )
    ike_policy = IKEPolicySerializer(
        nested=True
    )
    ipsec_policy = IPSecPolicySerializer(
        nested=True
    )

    class Meta:
        model = IPSecProfile
        fields = (
            'id', 'url', 'display_url', 'display', 'name', 'description', 'mode', 'ike_policy', 'ipsec_policy',
            'comments', 'tags', 'custom_fields', 'created', 'last_updated',
        )
        brief_fields = ('id', 'url', 'display', 'name', 'description')
