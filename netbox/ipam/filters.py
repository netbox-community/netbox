from __future__ import unicode_literals

import django_filters
from netaddr import IPNetwork
from netaddr.core import AddrFormatError

from django.db.models import Q

from dcim.models import Site, Device, Interface
from extras.filters import CustomFieldFilterSet
from tenancy.models import Tenant
from utilities.filters import NullableModelMultipleChoiceFilter, NumericInFilter
from .models import (
    Aggregate, IPAddress, IPADDRESS_STATUS_CHOICES, Prefix, PREFIX_STATUS_CHOICES, RIR, Role, Service, VLAN,
    VLAN_STATUS_CHOICES, VLANGroup, VRF,
)


class VRFFilter(CustomFieldFilterSet, django_filters.FilterSet):
    id__in = NumericInFilter(name='id', lookup_expr='in')
    q = django_filters.CharFilter(
        method='search',
        label='Search',
    )
    tenant_id = NullableModelMultipleChoiceFilter(
        name='tenant',
        queryset=Tenant.objects.all(),
        label='Tenant (ID)',
    )
    tenant = NullableModelMultipleChoiceFilter(
        name='tenant',
        queryset=Tenant.objects.all(),
        to_field_name='slug',
        label='Tenant (slug)',
    )

    def search(self, queryset, name, value):
        if not value.strip():
            return queryset
        return queryset.filter(
            Q(name__icontains=value) |
            Q(rd__icontains=value) |
            Q(description__icontains=value)
        )

    class Meta:
        model = VRF
        fields = ['name', 'rd']


class RIRFilter(django_filters.FilterSet):
    id__in = NumericInFilter(name='id', lookup_expr='in')

    class Meta:
        model = RIR
        fields = ['is_private']


class AggregateFilter(CustomFieldFilterSet, django_filters.FilterSet):
    id__in = NumericInFilter(name='id', lookup_expr='in')
    q = django_filters.CharFilter(
        method='search',
        label='Search',
    )
    rir_id = django_filters.ModelMultipleChoiceFilter(
        name='rir',
        queryset=RIR.objects.all(),
        label='RIR (ID)',
    )
    rir = django_filters.ModelMultipleChoiceFilter(
        name='rir__slug',
        queryset=RIR.objects.all(),
        to_field_name='slug',
        label='RIR (slug)',
    )

    class Meta:
        model = Aggregate
        fields = ['family', 'date_added']

    def search(self, queryset, name, value):
        if not value.strip():
            return queryset
        qs_filter = Q(description__icontains=value)
        try:
            prefix = str(IPNetwork(value.strip()).cidr)
            qs_filter |= Q(prefix__net_contains_or_equals=prefix)
        except (AddrFormatError, ValueError):
            pass
        return queryset.filter(qs_filter)


class PrefixFilter(CustomFieldFilterSet, django_filters.FilterSet):
    id__in = NumericInFilter(name='id', lookup_expr='in')
    q = django_filters.CharFilter(
        method='search',
        label='Search',
    )
    parent = django_filters.CharFilter(
        method='search_by_parent',
        label='Parent prefix',
    )
    mask_length = django_filters.NumberFilter(
        method='filter_mask_length',
        label='Mask length',
    )
    vrf_id = NullableModelMultipleChoiceFilter(
        name='vrf_id',
        queryset=VRF.objects.all(),
        label='VRF',
    )
    vrf = NullableModelMultipleChoiceFilter(
        name='vrf',
        queryset=VRF.objects.all(),
        to_field_name='rd',
        label='VRF (RD)',
    )
    tenant_id = NullableModelMultipleChoiceFilter(
        name='tenant',
        queryset=Tenant.objects.all(),
        label='Tenant (ID)',
    )
    tenant = NullableModelMultipleChoiceFilter(
        name='tenant',
        queryset=Tenant.objects.all(),
        to_field_name='slug',
        label='Tenant (slug)',
    )
    site_id = NullableModelMultipleChoiceFilter(
        name='site',
        queryset=Site.objects.all(),
        label='Site (ID)',
    )
    site = NullableModelMultipleChoiceFilter(
        name='site',
        queryset=Site.objects.all(),
        to_field_name='slug',
        label='Site (slug)',
    )
    vlan_id = NullableModelMultipleChoiceFilter(
        name='vlan',
        queryset=VLAN.objects.all(),
        label='VLAN (ID)',
    )
    vlan_vid = django_filters.NumberFilter(
        name='vlan__vid',
        label='VLAN number (1-4095)',
    )
    role_id = NullableModelMultipleChoiceFilter(
        name='role',
        queryset=Role.objects.all(),
        label='Role (ID)',
    )
    role = NullableModelMultipleChoiceFilter(
        name='role',
        queryset=Role.objects.all(),
        to_field_name='slug',
        label='Role (slug)',
    )
    status = django_filters.MultipleChoiceFilter(
        choices=PREFIX_STATUS_CHOICES
    )

    class Meta:
        model = Prefix
        fields = ['family']

    def search(self, queryset, name, value):
        if not value.strip():
            return queryset
        qs_filter = Q(description__icontains=value)
        try:
            prefix = str(IPNetwork(value.strip()).cidr)
            qs_filter |= Q(prefix__net_contains_or_equals=prefix)
        except (AddrFormatError, ValueError):
            pass
        return queryset.filter(qs_filter)

    def search_by_parent(self, queryset, name, value):
        value = value.strip()
        if not value:
            return queryset
        try:
            query = str(IPNetwork(value).cidr)
            return queryset.filter(prefix__net_contained_or_equal=query)
        except (AddrFormatError, ValueError):
            return queryset.none()

    def filter_mask_length(self, queryset, name, value):
        if not value:
            return queryset
        return queryset.filter(prefix__net_mask_length=value)


class IPAddressFilter(CustomFieldFilterSet, django_filters.FilterSet):
    id__in = NumericInFilter(name='id', lookup_expr='in')
    q = django_filters.CharFilter(
        method='search',
        label='Search',
    )
    parent = django_filters.CharFilter(
        method='search_by_parent',
        label='Parent prefix',
    )
    mask_length = django_filters.NumberFilter(
        method='filter_mask_length',
        label='Mask length',
    )
    vrf_id = NullableModelMultipleChoiceFilter(
        name='vrf_id',
        queryset=VRF.objects.all(),
        label='VRF',
    )
    vrf = NullableModelMultipleChoiceFilter(
        name='vrf',
        queryset=VRF.objects.all(),
        to_field_name='rd',
        label='VRF (RD)',
    )
    tenant_id = NullableModelMultipleChoiceFilter(
        name='tenant',
        queryset=Tenant.objects.all(),
        label='Tenant (ID)',
    )
    tenant = NullableModelMultipleChoiceFilter(
        name='tenant',
        queryset=Tenant.objects.all(),
        to_field_name='slug',
        label='Tenant (slug)',
    )
    device_id = django_filters.ModelMultipleChoiceFilter(
        name='interface__device',
        queryset=Device.objects.all(),
        label='Device (ID)',
    )
    device = django_filters.ModelMultipleChoiceFilter(
        name='interface__device__name',
        queryset=Device.objects.all(),
        to_field_name='name',
        label='Device (name)',
    )
    interface_id = django_filters.ModelMultipleChoiceFilter(
        name='interface',
        queryset=Interface.objects.all(),
        label='Interface (ID)',
    )
    status = django_filters.MultipleChoiceFilter(
        choices=IPADDRESS_STATUS_CHOICES
    )

    class Meta:
        model = IPAddress
        fields = ['family']

    def search(self, queryset, name, value):
        if not value.strip():
            return queryset
        qs_filter = Q(description__icontains=value)
        try:
            ipaddress = str(IPNetwork(value.strip()))
            qs_filter |= Q(address__net_host=ipaddress)
        except (AddrFormatError, ValueError):
            pass
        return queryset.filter(qs_filter)

    def search_by_parent(self, queryset, name, value):
        value = value.strip()
        if not value:
            return queryset
        try:
            query = str(IPNetwork(value.strip()).cidr)
            return queryset.filter(address__net_host_contained=query)
        except (AddrFormatError, ValueError):
            return queryset.none()

    def filter_mask_length(self, queryset, name, value):
        if not value:
            return queryset
        return queryset.filter(address__net_mask_length=value)


class VLANGroupFilter(django_filters.FilterSet):
    site_id = NullableModelMultipleChoiceFilter(
        name='site',
        queryset=Site.objects.all(),
        label='Site (ID)',
    )
    site = NullableModelMultipleChoiceFilter(
        name='site',
        queryset=Site.objects.all(),
        to_field_name='slug',
        label='Site (slug)',
    )

    class Meta:
        model = VLANGroup
        fields = ['name']


class VLANFilter(CustomFieldFilterSet, django_filters.FilterSet):
    id__in = NumericInFilter(name='id', lookup_expr='in')
    q = django_filters.CharFilter(
        method='search',
        label='Search',
    )
    site_id = NullableModelMultipleChoiceFilter(
        name='site',
        queryset=Site.objects.all(),
        label='Site (ID)',
    )
    site = NullableModelMultipleChoiceFilter(
        name='site',
        queryset=Site.objects.all(),
        to_field_name='slug',
        label='Site (slug)',
    )
    group_id = NullableModelMultipleChoiceFilter(
        name='group',
        queryset=VLANGroup.objects.all(),
        label='Group (ID)',
    )
    group = NullableModelMultipleChoiceFilter(
        name='group',
        queryset=VLANGroup.objects.all(),
        to_field_name='slug',
        label='Group',
    )
    tenant_id = NullableModelMultipleChoiceFilter(
        name='tenant',
        queryset=Tenant.objects.all(),
        label='Tenant (ID)',
    )
    tenant = NullableModelMultipleChoiceFilter(
        name='tenant',
        queryset=Tenant.objects.all(),
        to_field_name='slug',
        label='Tenant (slug)',
    )
    role_id = NullableModelMultipleChoiceFilter(
        name='role',
        queryset=Role.objects.all(),
        label='Role (ID)',
    )
    role = NullableModelMultipleChoiceFilter(
        name='role',
        queryset=Role.objects.all(),
        to_field_name='slug',
        label='Role (slug)',
    )
    status = django_filters.MultipleChoiceFilter(
        choices=VLAN_STATUS_CHOICES
    )

    class Meta:
        model = VLAN
        fields = ['name', 'vid']

    def search(self, queryset, name, value):
        if not value.strip():
            return queryset
        qs_filter = Q(name__icontains=value) | Q(description__icontains=value)
        try:
            qs_filter |= Q(vid=int(value.strip()))
        except ValueError:
            pass
        return queryset.filter(qs_filter)


class ServiceFilter(django_filters.FilterSet):
    device_id = django_filters.ModelMultipleChoiceFilter(
        name='device',
        queryset=Device.objects.all(),
        label='Device (ID)',
    )
    device = django_filters.ModelMultipleChoiceFilter(
        name='device__name',
        queryset=Device.objects.all(),
        to_field_name='name',
        label='Device (name)',
    )

    class Meta:
        model = Service
        fields = ['name', 'protocol', 'port']
