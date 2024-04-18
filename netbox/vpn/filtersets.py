import django_filters
from django.db.models import Q
from django.utils.translation import gettext as _

from dcim.models import Device, Interface
from ipam.models import IPAddress, RouteTarget, VLAN
from netbox.filtersets import NetBoxModelFilterSet, OrganizationalModelFilterSet
from tenancy.filtersets import TenancyFilterSet
from utilities.filters import ContentTypeFilter, MultiValueCharFilter, MultiValueNumberFilter
from virtualization.models import VirtualMachine, VMInterface
from .choices import *
from .models import *

__all__ = (
    'IKEPolicyFilterSet',
    'IKEProposalFilterSet',
    'IPSecPolicyFilterSet',
    'IPSecProfileFilterSet',
    'IPSecProposalFilterSet',
    'L2VPNFilterSet',
    'L2VPNTerminationFilterSet',
    'TunnelFilterSet',
    'TunnelGroupFilterSet',
    'TunnelTerminationFilterSet',
)


class TunnelGroupFilterSet(OrganizationalModelFilterSet):

    class Meta:
        model = TunnelGroup
        fields = ['id', 'name', 'slug', 'description']


class TunnelFilterSet(NetBoxModelFilterSet, TenancyFilterSet):
    status = django_filters.MultipleChoiceFilter(
        choices=TunnelStatusChoices
    )
    group_id = django_filters.ModelMultipleChoiceFilter(
        queryset=TunnelGroup.objects.all(),
        label=_('Tunnel group (ID)'),
    )
    group = django_filters.ModelMultipleChoiceFilter(
        field_name='group__slug',
        queryset=TunnelGroup.objects.all(),
        to_field_name='slug',
        label=_('Tunnel group (slug)'),
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
        fields = ['id', 'name', 'tunnel_id', 'description']

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
    termination_type = ContentTypeFilter()
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
    ike_policy_id = django_filters.ModelMultipleChoiceFilter(
        field_name='ike_policies',
        queryset=IKEPolicy.objects.all(),
        label=_('IKE policy (ID)'),
    )
    ike_policy = django_filters.ModelMultipleChoiceFilter(
        field_name='ike_policies__name',
        queryset=IKEPolicy.objects.all(),
        to_field_name='name',
        label=_('IKE policy (name)'),
    )

    class Meta:
        model = IKEProposal
        fields = ['id', 'name', 'sa_lifetime', 'description']

    def search(self, queryset, name, value):
        if not value.strip():
            return queryset
        return queryset.filter(
            Q(name__icontains=value) |
            Q(description__icontains=value) |
            Q(comments__icontains=value)
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
        fields = ['id', 'name', 'preshared_key', 'description']

    def search(self, queryset, name, value):
        if not value.strip():
            return queryset
        return queryset.filter(
            Q(name__icontains=value) |
            Q(description__icontains=value) |
            Q(comments__icontains=value)
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
        fields = ['id', 'name', 'sa_lifetime_seconds', 'sa_lifetime_data', 'description']

    def search(self, queryset, name, value):
        if not value.strip():
            return queryset
        return queryset.filter(
            Q(name__icontains=value) |
            Q(description__icontains=value) |
            Q(comments__icontains=value)
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
        fields = ['id', 'name', 'description']

    def search(self, queryset, name, value):
        if not value.strip():
            return queryset
        return queryset.filter(
            Q(name__icontains=value) |
            Q(description__icontains=value) |
            Q(comments__icontains=value)
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
        fields = ['id', 'name', 'description']

    def search(self, queryset, name, value):
        if not value.strip():
            return queryset
        return queryset.filter(
            Q(name__icontains=value) |
            Q(description__icontains=value) |
            Q(comments__icontains=value)
        )


class L2VPNFilterSet(NetBoxModelFilterSet, TenancyFilterSet):
    type = django_filters.MultipleChoiceFilter(
        choices=L2VPNTypeChoices,
        null_value=None
    )
    import_target_id = django_filters.ModelMultipleChoiceFilter(
        field_name='import_targets',
        queryset=RouteTarget.objects.all(),
        label=_('Import target'),
    )
    import_target = django_filters.ModelMultipleChoiceFilter(
        field_name='import_targets__name',
        queryset=RouteTarget.objects.all(),
        to_field_name='name',
        label=_('Import target (name)'),
    )
    export_target_id = django_filters.ModelMultipleChoiceFilter(
        field_name='export_targets',
        queryset=RouteTarget.objects.all(),
        label=_('Export target'),
    )
    export_target = django_filters.ModelMultipleChoiceFilter(
        field_name='export_targets__name',
        queryset=RouteTarget.objects.all(),
        to_field_name='name',
        label=_('Export target (name)'),
    )

    class Meta:
        model = L2VPN
        fields = ['id', 'identifier', 'name', 'slug', 'type', 'description']

    def search(self, queryset, name, value):
        if not value.strip():
            return queryset
        qs_filter = Q(name__icontains=value) | Q(description__icontains=value)
        try:
            qs_filter |= Q(identifier=int(value))
        except ValueError:
            pass
        return queryset.filter(qs_filter)


class L2VPNTerminationFilterSet(NetBoxModelFilterSet):
    l2vpn_id = django_filters.ModelMultipleChoiceFilter(
        queryset=L2VPN.objects.all(),
        label=_('L2VPN (ID)'),
    )
    l2vpn = django_filters.ModelMultipleChoiceFilter(
        field_name='l2vpn__slug',
        queryset=L2VPN.objects.all(),
        to_field_name='slug',
        label=_('L2VPN (slug)'),
    )
    region = MultiValueCharFilter(
        method='filter_region',
        field_name='slug',
        label=_('Region (slug)'),
    )
    region_id = MultiValueNumberFilter(
        method='filter_region',
        field_name='pk',
        label=_('Region (ID)'),
    )
    site = MultiValueCharFilter(
        method='filter_site',
        field_name='slug',
        label=_('Site (slug)'),
    )
    site_id = MultiValueNumberFilter(
        method='filter_site',
        field_name='pk',
        label=_('Site (ID)'),
    )
    device = django_filters.ModelMultipleChoiceFilter(
        field_name='interface__device__name',
        queryset=Device.objects.all(),
        to_field_name='name',
        label=_('Device (name)'),
    )
    device_id = django_filters.ModelMultipleChoiceFilter(
        field_name='interface__device',
        queryset=Device.objects.all(),
        label=_('Device (ID)'),
    )
    virtual_machine = django_filters.ModelMultipleChoiceFilter(
        field_name='vminterface__virtual_machine__name',
        queryset=VirtualMachine.objects.all(),
        to_field_name='name',
        label=_('Virtual machine (name)'),
    )
    virtual_machine_id = django_filters.ModelMultipleChoiceFilter(
        field_name='vminterface__virtual_machine',
        queryset=VirtualMachine.objects.all(),
        label=_('Virtual machine (ID)'),
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
        label=_('VM Interface (ID)'),
    )
    vlan = django_filters.ModelMultipleChoiceFilter(
        field_name='vlan__name',
        queryset=VLAN.objects.all(),
        to_field_name='name',
        label=_('VLAN (name)'),
    )
    vlan_vid = django_filters.NumberFilter(
        field_name='vlan__vid',
        label=_('VLAN number (1-4094)'),
    )
    vlan_id = django_filters.ModelMultipleChoiceFilter(
        field_name='vlan',
        queryset=VLAN.objects.all(),
        label=_('VLAN (ID)'),
    )
    assigned_object_type = ContentTypeFilter()

    class Meta:
        model = L2VPNTermination
        fields = ('id', 'assigned_object_type_id')

    def search(self, queryset, name, value):
        if not value.strip():
            return queryset
        qs_filter = Q(l2vpn__name__icontains=value)
        return queryset.filter(qs_filter)

    def filter_assigned_object(self, queryset, name, value):
        qs = queryset.filter(
            Q(**{'{}__in'.format(name): value})
        )
        return qs

    def filter_site(self, queryset, name, value):
        qs = queryset.filter(
            Q(
                Q(**{'vlan__site__{}__in'.format(name): value}) |
                Q(**{'interface__device__site__{}__in'.format(name): value}) |
                Q(**{'vminterface__virtual_machine__site__{}__in'.format(name): value})
            )
        )
        return qs

    def filter_region(self, queryset, name, value):
        qs = queryset.filter(
            Q(
                Q(**{'vlan__site__region__{}__in'.format(name): value}) |
                Q(**{'interface__device__site__region__{}__in'.format(name): value}) |
                Q(**{'vminterface__virtual_machine__site__region__{}__in'.format(name): value})
            )
        )
        return qs
