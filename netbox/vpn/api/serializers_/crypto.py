from netbox.api.fields import ChoiceField, SerializedPKRelatedField
from netbox.api.serializers import PrimaryModelSerializer
from vpn.choices import *
from vpn.models import IKEPolicy, IKEProposal, IPSecPolicy, IPSecProfile, IPSecProposal

__all__ = (
    'IKEPolicySerializer',
    'IKEProposalSerializer',
    'IPSecPolicySerializer',
    'IPSecProfileSerializer',
    'IPSecProposalSerializer',
)


class IKEProposalSerializer(PrimaryModelSerializer):
    authentication_method = ChoiceField(
        choices=AuthenticationMethodChoices
    )
    encryption_algorithm = ChoiceField(
        choices=EncryptionAlgorithmChoices
    )
    authentication_algorithm = ChoiceField(
        choices=AuthenticationAlgorithmChoices,
        required=False
    )
    group = ChoiceField(
        choices=DHGroupChoices
    )

    class Meta:
        model = IKEProposal
        fields = (
            'id', 'url', 'display_url', 'display', 'name', 'description', 'authentication_method',
            'encryption_algorithm', 'authentication_algorithm', 'group', 'sa_lifetime', 'owner', 'comments', 'tags',
            'custom_fields', 'created', 'last_updated',
        )
        brief_fields = ('id', 'url', 'display', 'name', 'description')


class IKEPolicySerializer(PrimaryModelSerializer):
    version = ChoiceField(
        choices=IKEVersionChoices
    )
    mode = ChoiceField(
        choices=IKEModeChoices,
        required=False
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
            'preshared_key', 'owner', 'comments', 'tags', 'custom_fields', 'created', 'last_updated',
        )
        brief_fields = ('id', 'url', 'display', 'name', 'description')


class IPSecProposalSerializer(PrimaryModelSerializer):
    encryption_algorithm = ChoiceField(
        choices=EncryptionAlgorithmChoices,
        required=False
    )
    authentication_algorithm = ChoiceField(
        choices=AuthenticationAlgorithmChoices,
        required=False
    )

    class Meta:
        model = IPSecProposal
        fields = (
            'id', 'url', 'display_url', 'display', 'name', 'description', 'encryption_algorithm',
            'authentication_algorithm', 'sa_lifetime_seconds', 'sa_lifetime_data', 'owner', 'comments', 'tags',
            'custom_fields', 'created', 'last_updated',
        )
        brief_fields = ('id', 'url', 'display', 'name', 'description')


class IPSecPolicySerializer(PrimaryModelSerializer):
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
            'id', 'url', 'display_url', 'display', 'name', 'description', 'proposals', 'pfs_group', 'owner', 'comments',
            'tags', 'custom_fields', 'created', 'last_updated',
        )
        brief_fields = ('id', 'url', 'display', 'name', 'description')


class IPSecProfileSerializer(PrimaryModelSerializer):
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
            'id', 'url', 'display_url', 'display', 'name', 'description', 'mode', 'ike_policy', 'ipsec_policy', 'owner',
            'comments', 'tags', 'custom_fields', 'created', 'last_updated',
        )
        brief_fields = ('id', 'url', 'display', 'name', 'description')
