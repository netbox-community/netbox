import django_filters
from django.db.models import Q
from django.utils.translation import gettext as _

from dcim.filtersets import CabledObjectFilterSet
from dcim.models import Interface, Location, Region, Site, SiteGroup
from ipam.models import ASN
from netbox.filtersets import NetBoxModelFilterSet, OrganizationalModelFilterSet
from tenancy.filtersets import ContactModelFilterSet, TenancyFilterSet
from utilities.filters import ContentTypeFilter, TreeNodeMultipleChoiceFilter
from .choices import *
from .models import *

__all__ = (
    'CircuitFilterSet',
    'CircuitGroupAssignmentFilterSet',
    'CircuitGroupFilterSet',
    'CircuitTerminationFilterSet',
    'CircuitTypeFilterSet',
    'ProviderNetworkFilterSet',
    'ProviderAccountFilterSet',
    'ProviderFilterSet',
    'VirtualCircuitFilterSet',
    'VirtualCircuitTerminationFilterSet',
)


class ProviderFilterSet(NetBoxModelFilterSet, ContactModelFilterSet):
    region_id = TreeNodeMultipleChoiceFilter(
        queryset=Region.objects.all(),
        field_name='circuits__terminations___region',
        lookup_expr='in',
        label=_('Region (ID)'),
    )
    region = TreeNodeMultipleChoiceFilter(
        queryset=Region.objects.all(),
        field_name='circuits__terminations___region',
        lookup_expr='in',
        to_field_name='slug',
        label=_('Region (slug)'),
    )
    site_group_id = TreeNodeMultipleChoiceFilter(
        queryset=SiteGroup.objects.all(),
        field_name='circuits__terminations___site_group',
        lookup_expr='in',
        label=_('Site group (ID)'),
    )
    site_group = TreeNodeMultipleChoiceFilter(
        queryset=SiteGroup.objects.all(),
        field_name='circuits__terminations___site_group',
        lookup_expr='in',
        to_field_name='slug',
        label=_('Site group (slug)'),
    )
    site_id = django_filters.ModelMultipleChoiceFilter(
        field_name='circuits__terminations___site',
        queryset=Site.objects.all(),
        label=_('Site'),
    )
    site = django_filters.ModelMultipleChoiceFilter(
        field_name='circuits__terminations___site__slug',
        queryset=Site.objects.all(),
        to_field_name='slug',
        label=_('Site (slug)'),
    )
    asn_id = django_filters.ModelMultipleChoiceFilter(
        field_name='asns',
        queryset=ASN.objects.all(),
        label=_('ASN (ID)'),
    )
    asn = django_filters.ModelMultipleChoiceFilter(
        field_name='asns__asn',
        queryset=ASN.objects.all(),
        to_field_name='asn',
        label=_('ASN'),
    )

    class Meta:
        model = Provider
        fields = ('id', 'name', 'slug', 'description')

    def search(self, queryset, name, value):
        if not value.strip():
            return queryset
        return queryset.filter(
            Q(name__icontains=value) |
            Q(description__icontains=value) |
            Q(accounts__account__icontains=value) |
            Q(accounts__name__icontains=value) |
            Q(comments__icontains=value)
        )


class ProviderAccountFilterSet(NetBoxModelFilterSet):
    provider_id = django_filters.ModelMultipleChoiceFilter(
        queryset=Provider.objects.all(),
        label=_('Provider (ID)'),
    )
    provider = django_filters.ModelMultipleChoiceFilter(
        field_name='provider__slug',
        queryset=Provider.objects.all(),
        to_field_name='slug',
        label=_('Provider (slug)'),
    )

    class Meta:
        model = ProviderAccount
        fields = ('id', 'name', 'account', 'description')

    def search(self, queryset, name, value):
        if not value.strip():
            return queryset
        return queryset.filter(
            Q(name__icontains=value) |
            Q(description__icontains=value) |
            Q(account__icontains=value) |
            Q(comments__icontains=value)
        ).distinct()


class ProviderNetworkFilterSet(NetBoxModelFilterSet):
    provider_id = django_filters.ModelMultipleChoiceFilter(
        queryset=Provider.objects.all(),
        label=_('Provider (ID)'),
    )
    provider = django_filters.ModelMultipleChoiceFilter(
        field_name='provider__slug',
        queryset=Provider.objects.all(),
        to_field_name='slug',
        label=_('Provider (slug)'),
    )

    class Meta:
        model = ProviderNetwork
        fields = ('id', 'name', 'service_id', 'description')

    def search(self, queryset, name, value):
        if not value.strip():
            return queryset
        return queryset.filter(
            Q(name__icontains=value) |
            Q(service_id__icontains=value) |
            Q(description__icontains=value) |
            Q(comments__icontains=value)
        ).distinct()


class CircuitTypeFilterSet(OrganizationalModelFilterSet):

    class Meta:
        model = CircuitType
        fields = ('id', 'name', 'slug', 'color', 'description')


class CircuitFilterSet(NetBoxModelFilterSet, TenancyFilterSet, ContactModelFilterSet):
    provider_id = django_filters.ModelMultipleChoiceFilter(
        queryset=Provider.objects.all(),
        label=_('Provider (ID)'),
    )
    provider = django_filters.ModelMultipleChoiceFilter(
        field_name='provider__slug',
        queryset=Provider.objects.all(),
        to_field_name='slug',
        label=_('Provider (slug)'),
    )
    provider_account_id = django_filters.ModelMultipleChoiceFilter(
        field_name='provider_account',
        queryset=ProviderAccount.objects.all(),
        label=_('Provider account (ID)'),
    )
    provider_account = django_filters.ModelMultipleChoiceFilter(
        field_name='provider_account__account',
        queryset=Provider.objects.all(),
        to_field_name='account',
        label=_('Provider account (account)'),
    )
    provider_network_id = django_filters.ModelMultipleChoiceFilter(
        field_name='terminations___provider_network',
        queryset=ProviderNetwork.objects.all(),
        label=_('Provider network (ID)'),
    )
    type_id = django_filters.ModelMultipleChoiceFilter(
        queryset=CircuitType.objects.all(),
        label=_('Circuit type (ID)'),
    )
    type = django_filters.ModelMultipleChoiceFilter(
        field_name='type__slug',
        queryset=CircuitType.objects.all(),
        to_field_name='slug',
        label=_('Circuit type (slug)'),
    )
    status = django_filters.MultipleChoiceFilter(
        choices=CircuitStatusChoices,
        null_value=None
    )
    region_id = TreeNodeMultipleChoiceFilter(
        queryset=Region.objects.all(),
        field_name='terminations___region',
        lookup_expr='in',
        label=_('Region (ID)'),
    )
    region = TreeNodeMultipleChoiceFilter(
        queryset=Region.objects.all(),
        field_name='terminations___region',
        lookup_expr='in',
        to_field_name='slug',
        label=_('Region (slug)'),
    )
    site_group_id = TreeNodeMultipleChoiceFilter(
        queryset=SiteGroup.objects.all(),
        field_name='terminations___site_group',
        lookup_expr='in',
        label=_('Site group (ID)'),
    )
    site_group = TreeNodeMultipleChoiceFilter(
        queryset=SiteGroup.objects.all(),
        field_name='terminations___site_group',
        lookup_expr='in',
        to_field_name='slug',
        label=_('Site group (slug)'),
    )
    site_id = django_filters.ModelMultipleChoiceFilter(
        field_name='terminations___site',
        queryset=Site.objects.all(),
        label=_('Site (ID)'),
    )
    site = django_filters.ModelMultipleChoiceFilter(
        field_name='terminations___site__slug',
        queryset=Site.objects.all(),
        to_field_name='slug',
        label=_('Site (slug)'),
    )
    termination_a_id = django_filters.ModelMultipleChoiceFilter(
        queryset=CircuitTermination.objects.all(),
        label=_('Termination A (ID)'),
    )
    termination_z_id = django_filters.ModelMultipleChoiceFilter(
        queryset=CircuitTermination.objects.all(),
        label=_('Termination A (ID)'),
    )

    class Meta:
        model = Circuit
        fields = ('id', 'cid', 'description', 'install_date', 'termination_date', 'commit_rate', 'distance', 'distance_unit')

    def search(self, queryset, name, value):
        if not value.strip():
            return queryset
        return queryset.filter(
            Q(cid__icontains=value) |
            Q(terminations__xconnect_id__icontains=value) |
            Q(terminations__pp_info__icontains=value) |
            Q(terminations__description__icontains=value) |
            Q(description__icontains=value) |
            Q(comments__icontains=value)
        ).distinct()


class CircuitTerminationFilterSet(NetBoxModelFilterSet, CabledObjectFilterSet):
    q = django_filters.CharFilter(
        method='search',
        label=_('Search'),
    )
    circuit_id = django_filters.ModelMultipleChoiceFilter(
        queryset=Circuit.objects.all(),
        label=_('Circuit'),
    )
    termination_type = ContentTypeFilter()
    region_id = TreeNodeMultipleChoiceFilter(
        queryset=Region.objects.all(),
        field_name='_region',
        lookup_expr='in',
        label=_('Region (ID)'),
    )
    region = TreeNodeMultipleChoiceFilter(
        queryset=Region.objects.all(),
        field_name='_region',
        lookup_expr='in',
        to_field_name='slug',
        label=_('Region (slug)'),
    )
    site_group_id = TreeNodeMultipleChoiceFilter(
        queryset=SiteGroup.objects.all(),
        field_name='_site_group',
        lookup_expr='in',
        label=_('Site group (ID)'),
    )
    site_group = TreeNodeMultipleChoiceFilter(
        queryset=SiteGroup.objects.all(),
        field_name='_site_group',
        lookup_expr='in',
        to_field_name='slug',
        label=_('Site group (slug)'),
    )
    site_id = django_filters.ModelMultipleChoiceFilter(
        queryset=Site.objects.all(),
        field_name='_site',
        label=_('Site (ID)'),
    )
    site = django_filters.ModelMultipleChoiceFilter(
        field_name='_site__slug',
        queryset=Site.objects.all(),
        to_field_name='slug',
        label=_('Site (slug)'),
    )
    location_id = TreeNodeMultipleChoiceFilter(
        queryset=Location.objects.all(),
        field_name='_location',
        lookup_expr='in',
        label=_('Location (ID)'),
    )
    location = TreeNodeMultipleChoiceFilter(
        queryset=Location.objects.all(),
        field_name='_location',
        lookup_expr='in',
        to_field_name='slug',
        label=_('Location (slug)'),
    )
    provider_network_id = django_filters.ModelMultipleChoiceFilter(
        queryset=ProviderNetwork.objects.all(),
        field_name='_provider_network',
        label=_('ProviderNetwork (ID)'),
    )
    provider_id = django_filters.ModelMultipleChoiceFilter(
        field_name='circuit__provider_id',
        queryset=Provider.objects.all(),
        label=_('Provider (ID)'),
    )
    provider = django_filters.ModelMultipleChoiceFilter(
        field_name='circuit__provider__slug',
        queryset=Provider.objects.all(),
        to_field_name='slug',
        label=_('Provider (slug)'),
    )

    class Meta:
        model = CircuitTermination
        fields = (
            'id', 'termination_id', 'term_side', 'port_speed', 'upstream_speed', 'xconnect_id', 'description', 'mark_connected',
            'pp_info', 'cable_end',
        )

    def search(self, queryset, name, value):
        if not value.strip():
            return queryset
        return queryset.filter(
            Q(circuit__cid__icontains=value) |
            Q(xconnect_id__icontains=value) |
            Q(pp_info__icontains=value) |
            Q(description__icontains=value)
        ).distinct()


class CircuitGroupFilterSet(OrganizationalModelFilterSet, TenancyFilterSet):

    class Meta:
        model = CircuitGroup
        fields = ('id', 'name', 'slug', 'description')


class CircuitGroupAssignmentFilterSet(NetBoxModelFilterSet):
    q = django_filters.CharFilter(
        method='search',
        label=_('Search'),
    )
    provider_id = django_filters.ModelMultipleChoiceFilter(
        field_name='circuit__provider',
        queryset=Provider.objects.all(),
        label=_('Provider (ID)'),
    )
    provider = django_filters.ModelMultipleChoiceFilter(
        field_name='circuit__provider__slug',
        queryset=Provider.objects.all(),
        to_field_name='slug',
        label=_('Provider (slug)'),
    )
    circuit_id = django_filters.ModelMultipleChoiceFilter(
        queryset=Circuit.objects.all(),
        label=_('Circuit (ID)'),
    )
    circuit = django_filters.ModelMultipleChoiceFilter(
        field_name='circuit__cid',
        queryset=Circuit.objects.all(),
        to_field_name='cid',
        label=_('Circuit (CID)'),
    )
    group_id = django_filters.ModelMultipleChoiceFilter(
        queryset=CircuitGroup.objects.all(),
        label=_('Circuit group (ID)'),
    )
    group = django_filters.ModelMultipleChoiceFilter(
        field_name='group__slug',
        queryset=CircuitGroup.objects.all(),
        to_field_name='slug',
        label=_('Circuit group (slug)'),
    )

    class Meta:
        model = CircuitGroupAssignment
        fields = ('id', 'priority')

    def search(self, queryset, name, value):
        if not value.strip():
            return queryset
        return queryset.filter(
            Q(circuit__cid__icontains=value) |
            Q(group__name__icontains=value)
        )


class VirtualCircuitFilterSet(NetBoxModelFilterSet, TenancyFilterSet):
    provider_id = django_filters.ModelMultipleChoiceFilter(
        field_name='provider_network__provider',
        queryset=Provider.objects.all(),
        label=_('Provider (ID)'),
    )
    provider = django_filters.ModelMultipleChoiceFilter(
        field_name='provider_network__provider__slug',
        queryset=Provider.objects.all(),
        to_field_name='slug',
        label=_('Provider (slug)'),
    )
    provider_account_id = django_filters.ModelMultipleChoiceFilter(
        field_name='provider_account',
        queryset=ProviderAccount.objects.all(),
        label=_('Provider account (ID)'),
    )
    provider_account = django_filters.ModelMultipleChoiceFilter(
        field_name='provider_account__account',
        queryset=Provider.objects.all(),
        to_field_name='account',
        label=_('Provider account (account)'),
    )
    provider_network_id = django_filters.ModelMultipleChoiceFilter(
        queryset=ProviderNetwork.objects.all(),
        label=_('Provider network (ID)'),
    )
    status = django_filters.MultipleChoiceFilter(
        choices=CircuitStatusChoices,
        null_value=None
    )

    class Meta:
        model = VirtualCircuit
        fields = ('id', 'cid', 'description')

    def search(self, queryset, name, value):
        if not value.strip():
            return queryset
        return queryset.filter(
            Q(cid__icontains=value) |
            Q(description__icontains=value) |
            Q(comments__icontains=value)
        ).distinct()


class VirtualCircuitTerminationFilterSet(NetBoxModelFilterSet):
    q = django_filters.CharFilter(
        method='search',
        label=_('Search'),
    )
    virtual_circuit_id = django_filters.ModelMultipleChoiceFilter(
        queryset=VirtualCircuit.objects.all(),
        label=_('Virtual circuit'),
    )
    role = django_filters.MultipleChoiceFilter(
        choices=VirtualCircuitTerminationRoleChoices,
        null_value=None
    )
    provider_id = django_filters.ModelMultipleChoiceFilter(
        field_name='virtual_circuit__provider_network__provider',
        queryset=Provider.objects.all(),
        label=_('Provider (ID)'),
    )
    provider = django_filters.ModelMultipleChoiceFilter(
        field_name='virtual_circuit__provider_network__provider__slug',
        queryset=Provider.objects.all(),
        to_field_name='slug',
        label=_('Provider (slug)'),
    )
    provider_account_id = django_filters.ModelMultipleChoiceFilter(
        field_name='virtual_circuit__provider_account',
        queryset=ProviderAccount.objects.all(),
        label=_('Provider account (ID)'),
    )
    provider_account = django_filters.ModelMultipleChoiceFilter(
        field_name='virtual_circuit__provider_account__account',
        queryset=ProviderAccount.objects.all(),
        to_field_name='account',
        label=_('Provider account (account)'),
    )
    provider_network_id = django_filters.ModelMultipleChoiceFilter(
        queryset=ProviderNetwork.objects.all(),
        field_name='virtual_circuit__provider_network',
        label=_('Provider network (ID)'),
    )
    interface_id = django_filters.ModelMultipleChoiceFilter(
        queryset=Interface.objects.all(),
        field_name='interface',
        label=_('Interface (ID)'),
    )

    class Meta:
        model = VirtualCircuitTermination
        fields = ('id', 'interface_id', 'description')

    def search(self, queryset, name, value):
        if not value.strip():
            return queryset
        return queryset.filter(
            Q(virtual_circuit__cid__icontains=value) |
            Q(description__icontains=value)
        ).distinct()
