import django_filters
from django.db.models import Q
from django.utils.translation import gettext as _

from dcim.filtersets import CabledObjectFilterSet
from dcim.models import Region, Site, SiteGroup
from ipam.models import ASN
from netbox.filtersets import NetBoxModelFilterSet, OrganizationalModelFilterSet
from tenancy.filtersets import ContactModelFilterSet, TenancyFilterSet
from utilities.filters import TreeNodeMultipleChoiceFilter
from .choices import *
from .models import *

__all__ = (
    'CircuitFilterSet',
    'CircuitTerminationFilterSet',
    'CircuitTypeFilterSet',
    'ProviderNetworkFilterSet',
    'ProviderAccountFilterSet',
    'ProviderFilterSet',
)


class ProviderFilterSet(NetBoxModelFilterSet, ContactModelFilterSet):
    region_id = TreeNodeMultipleChoiceFilter(
        queryset=Region.objects.all(),
        field_name='circuits__terminations__site__region',
        lookup_expr='in',
        label=_('Region (ID)'),
    )
    region = TreeNodeMultipleChoiceFilter(
        queryset=Region.objects.all(),
        field_name='circuits__terminations__site__region',
        lookup_expr='in',
        to_field_name='slug',
        label=_('Region (slug)'),
    )
    site_group_id = TreeNodeMultipleChoiceFilter(
        queryset=SiteGroup.objects.all(),
        field_name='circuits__terminations__site__group',
        lookup_expr='in',
        label=_('Site group (ID)'),
    )
    site_group = TreeNodeMultipleChoiceFilter(
        queryset=SiteGroup.objects.all(),
        field_name='circuits__terminations__site__group',
        lookup_expr='in',
        to_field_name='slug',
        label=_('Site group (slug)'),
    )
    site_id = django_filters.ModelMultipleChoiceFilter(
        field_name='circuits__terminations__site',
        queryset=Site.objects.all(),
        label=_('Site'),
    )
    site = django_filters.ModelMultipleChoiceFilter(
        field_name='circuits__terminations__site__slug',
        queryset=Site.objects.all(),
        to_field_name='slug',
        label=_('Site (slug)'),
    )
    asn_id = django_filters.ModelMultipleChoiceFilter(
        field_name='asns',
        queryset=ASN.objects.all(),
        label=_('ASN (ID)'),
    )

    class Meta:
        model = Provider
        fields = ['id', 'name', 'slug']

    def search(self, queryset, name, value):
        if not value.strip():
            return queryset
        return queryset.filter(
            Q(name__icontains=value) |
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
        fields = ['id', 'name', 'account', 'description']

    def search(self, queryset, name, value):
        if not value.strip():
            return queryset
        return queryset.filter(
            Q(name__icontains=value) |
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
        fields = ['id', 'name', 'service_id', 'description']

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
        fields = ['id', 'name', 'slug', 'description']


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
        label=_('ProviderAccount (ID)'),
    )
    provider_network_id = django_filters.ModelMultipleChoiceFilter(
        field_name='terminations__provider_network',
        queryset=ProviderNetwork.objects.all(),
        label=_('ProviderNetwork (ID)'),
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
        field_name='terminations__site__region',
        lookup_expr='in',
        label=_('Region (ID)'),
    )
    region = TreeNodeMultipleChoiceFilter(
        queryset=Region.objects.all(),
        field_name='terminations__site__region',
        lookup_expr='in',
        to_field_name='slug',
        label=_('Region (slug)'),
    )
    site_group_id = TreeNodeMultipleChoiceFilter(
        queryset=SiteGroup.objects.all(),
        field_name='terminations__site__group',
        lookup_expr='in',
        label=_('Site group (ID)'),
    )
    site_group = TreeNodeMultipleChoiceFilter(
        queryset=SiteGroup.objects.all(),
        field_name='terminations__site__group',
        lookup_expr='in',
        to_field_name='slug',
        label=_('Site group (slug)'),
    )
    site_id = django_filters.ModelMultipleChoiceFilter(
        field_name='terminations__site',
        queryset=Site.objects.all(),
        label=_('Site (ID)'),
    )
    site = django_filters.ModelMultipleChoiceFilter(
        field_name='terminations__site__slug',
        queryset=Site.objects.all(),
        to_field_name='slug',
        label=_('Site (slug)'),
    )

    class Meta:
        model = Circuit
        fields = ['id', 'cid', 'description', 'install_date', 'termination_date', 'commit_rate']

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
    site_id = django_filters.ModelMultipleChoiceFilter(
        queryset=Site.objects.all(),
        label=_('Site (ID)'),
    )
    site = django_filters.ModelMultipleChoiceFilter(
        field_name='site__slug',
        queryset=Site.objects.all(),
        to_field_name='slug',
        label=_('Site (slug)'),
    )
    provider_network_id = django_filters.ModelMultipleChoiceFilter(
        queryset=ProviderNetwork.objects.all(),
        label=_('ProviderNetwork (ID)'),
    )

    class Meta:
        model = CircuitTermination
        fields = ['id', 'term_side', 'port_speed', 'upstream_speed', 'xconnect_id', 'description', 'cable_end']

    def search(self, queryset, name, value):
        if not value.strip():
            return queryset
        return queryset.filter(
            Q(circuit__cid__icontains=value) |
            Q(xconnect_id__icontains=value) |
            Q(pp_info__icontains=value) |
            Q(description__icontains=value)
        ).distinct()
