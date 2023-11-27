import django_filters
from django.db.models import Q
from django.utils.translation import gettext as _

from dcim.models import Interface
from ipam.models import IPAddress
from netbox.filtersets import NetBoxModelFilterSet
from tenancy.filtersets import TenancyFilterSet
from utilities.filters import ContentTypeFilter, MultiValueCharFilter, MultiValueNumberFilter
from virtualization.models import VMInterface
from .choices import *
from .models import *

__all__ = (
    'IKEPolicyFilterSet',
    'IKEProposalFilterSet',
    'IPSecPolicyFilterSet',
    'IPSecProfileFilterSet',
    'IPSecProposalFilterSet',
    'TunnelFilterSet',
    'TunnelTerminationFilterSet',
)


class TunnelFilterSet(NetBoxModelFilterSet, TenancyFilterSet):
    status = django_filters.MultipleChoiceFilter(
        choices=TunnelStatusChoices
    )
    encapsulation = django_filters.MultipleChoiceFilter(
        choices=TunnelEncapsulationChoices
    )
    ipsec_profile_id = django_filters.ModelMultipleChoiceFilter(
        queryset=IPSecProfile.objects.all(),
        label=_('IPSec profile (ID)'),
    )
    ipsec_profile = django_filters.ModelMultipleChoiceFilter(
        field_name='ipsec_profile__name',
        queryset=IPSecProfile.objects.all(),
        to_field_name='name',
        label=_('IPSec profile (name)'),
    )

    class Meta:
        model = Tunnel
        fields = ['id', 'name', 'tunnel_id']

    def search(self, queryset, name, value):
        if not value.strip():
            return queryset
        return queryset.filter(
            Q(name__icontains=value) |
            Q(description__icontains=value) |
            Q(comments__icontains=value)
        )


class TunnelTerminationFilterSet(NetBoxModelFilterSet):
    tunnel_id = django_filters.ModelMultipleChoiceFilter(
        field_name='tunnel',
        queryset=Tunnel.objects.all(),
        label=_('Tunnel (ID)'),
    )
    tunnel = django_filters.ModelMultipleChoiceFilter(
        field_name='tunnel__name',
        queryset=Tunnel.objects.all(),
        to_field_name='name',
        label=_('Tunnel (name)'),
    )
    role = django_filters.MultipleChoiceFilter(
        choices=TunnelTerminationRoleChoices
    )
    interface = django_filters.ModelMultipleChoiceFilter(
        field_name='interface__name',
        queryset=Interface.objects.all(),
        to_field_name='name',
        label=_('Interface (name)'),
    )
    interface_id = django_filters.ModelMultipleChoiceFilter(
        field_name='interface',
        queryset=Interface.objects.all(),
        label=_('Interface (ID)'),
    )
    vminterface = django_filters.ModelMultipleChoiceFilter(
        field_name='vminterface__name',
        queryset=VMInterface.objects.all(),
        to_field_name='name',
        label=_('VM interface (name)'),
    )
    vminterface_id = django_filters.ModelMultipleChoiceFilter(
        field_name='vminterface',
        queryset=VMInterface.objects.all(),
        label=_('VM interface (ID)'),
    )
    outside_ip_id = django_filters.ModelMultipleChoiceFilter(
        field_name='outside_ip',
        queryset=IPAddress.objects.all(),
        label=_('Outside IP (ID)'),
    )

    class Meta:
        model = TunnelTermination
        fields = ['id']


class IKEProposalFilterSet(NetBoxModelFilterSet):
    authentication_method = django_filters.MultipleChoiceFilter(
        choices=AuthenticationMethodChoices
    )
    encryption_algorithm = django_filters.MultipleChoiceFilter(
        choices=EncryptionAlgorithmChoices
    )
    authentication_algorithm = django_filters.MultipleChoiceFilter(
        choices=AuthenticationAlgorithmChoices
    )
    group = django_filters.MultipleChoiceFilter(
        choices=DHGroupChoices
    )

    class Meta:
        model = IKEProposal
        fields = ['id', 'name', 'sa_lifetime']

    def search(self, queryset, name, value):
        if not value.strip():
            return queryset
        return queryset.filter(
            Q(name__icontains=value) |
            Q(description__icontains=value)
        )


class IKEPolicyFilterSet(NetBoxModelFilterSet):
    version = django_filters.MultipleChoiceFilter(
        choices=IKEVersionChoices
    )
    mode = django_filters.MultipleChoiceFilter(
        choices=IKEModeChoices
    )
    proposal_id = MultiValueNumberFilter(
        field_name='proposals__id'
    )
    proposal = MultiValueCharFilter(
        field_name='proposals__name'
    )

    class Meta:
        model = IKEPolicy
        fields = ['id', 'name', 'preshared_key']

    def search(self, queryset, name, value):
        if not value.strip():
            return queryset
        return queryset.filter(
            Q(name__icontains=value) |
            Q(description__icontains=value)
        )


class IPSecProposalFilterSet(NetBoxModelFilterSet):
    encryption_algorithm = django_filters.MultipleChoiceFilter(
        choices=EncryptionAlgorithmChoices
    )
    authentication_algorithm = django_filters.MultipleChoiceFilter(
        choices=AuthenticationAlgorithmChoices
    )

    class Meta:
        model = IPSecProposal
        fields = ['id', 'name', 'sa_lifetime_seconds', 'sa_lifetime_data']

    def search(self, queryset, name, value):
        if not value.strip():
            return queryset
        return queryset.filter(
            Q(name__icontains=value) |
            Q(description__icontains=value)
        )


class IPSecPolicyFilterSet(NetBoxModelFilterSet):
    pfs_group = django_filters.MultipleChoiceFilter(
        choices=DHGroupChoices
    )
    proposal_id = MultiValueNumberFilter(
        field_name='proposals__id'
    )
    proposal = MultiValueCharFilter(
        field_name='proposals__name'
    )

    class Meta:
        model = IPSecPolicy
        fields = ['id', 'name']

    def search(self, queryset, name, value):
        if not value.strip():
            return queryset
        return queryset.filter(
            Q(name__icontains=value) |
            Q(description__icontains=value)
        )


class IPSecProfileFilterSet(NetBoxModelFilterSet):
    mode = django_filters.MultipleChoiceFilter(
        choices=IPSecModeChoices
    )
    ike_policy_id = django_filters.ModelMultipleChoiceFilter(
        queryset=IKEPolicy.objects.all(),
        label=_('IKE policy (ID)'),
    )
    ike_policy = django_filters.ModelMultipleChoiceFilter(
        field_name='ike_policy__name',
        queryset=IKEPolicy.objects.all(),
        to_field_name='name',
        label=_('IKE policy (name)'),
    )
    ipsec_policy_id = django_filters.ModelMultipleChoiceFilter(
        queryset=IPSecPolicy.objects.all(),
        label=_('IPSec policy (ID)'),
    )
    ipsec_policy = django_filters.ModelMultipleChoiceFilter(
        field_name='ipsec_policy__name',
        queryset=IPSecPolicy.objects.all(),
        to_field_name='name',
        label=_('IPSec policy (name)'),
    )

    class Meta:
        model = IPSecProfile
        fields = ['id', 'name']

    def search(self, queryset, name, value):
        if not value.strip():
            return queryset
        return queryset.filter(
            Q(name__icontains=value) |
            Q(description__icontains=value) |
            Q(comments__icontains=value)
        )
