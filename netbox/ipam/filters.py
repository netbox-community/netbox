from __future__ import unicode_literals

import django_filters
from django.core.exceptions import ValidationError
from django.db.models import Q
import netaddr
from netaddr.core import AddrFormatError

from dcim.models import Site, Device, Interface
from extras.filters import CustomFieldFilterSet
from tenancy.models import Tenant
from utilities.filters import NumericInFilter
from virtualization.models import VirtualMachine
from .constants import IPADDRESS_ROLE_CHOICES, IPADDRESS_STATUS_CHOICES, PREFIX_STATUS_CHOICES, VLAN_STATUS_CHOICES
from .models import Aggregate, IPAddress, Prefix, RIR, Role, Service, VLAN, VLANGroup, VRF


class VRFFilter(CustomFieldFilterSet, django_filters.FilterSet):
    id__in = NumericInFilter(name='id', lookup_expr='in')
    q = django_filters.CharFilter(
        method='search',
        label='Search',
    )
    tenant_id = django_filters.ModelMultipleChoiceFilter(
        queryset=Tenant.objects.all(),
        label='Tenant (ID)',
    )
    tenant = django_filters.ModelMultipleChoiceFilter(
        name='tenant__slug',
        queryset=Tenant.objects.all(),
        to_field_name='slug',
        label='Tenant (slug)',
    )
    tag = django_filters.CharFilter(
        name='tags__slug',
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
        fields = ['name', 'rd', 'enforce_unique']


class RIRFilter(django_filters.FilterSet):
    id__in = NumericInFilter(name='id', lookup_expr='in')

    class Meta:
        model = RIR
        fields = ['name', 'slug', 'is_private']


class AggregateFilter(CustomFieldFilterSet, django_filters.FilterSet):
    id__in = NumericInFilter(name='id', lookup_expr='in')
    q = django_filters.CharFilter(
        method='search',
        label='Search',
    )
    rir_id = django_filters.ModelMultipleChoiceFilter(
        queryset=RIR.objects.all(),
        label='RIR (ID)',
    )
    rir = django_filters.ModelMultipleChoiceFilter(
        name='rir__slug',
        queryset=RIR.objects.all(),
        to_field_name='slug',
        label='RIR (slug)',
    )
    tag = django_filters.CharFilter(
        name='tags__slug',
    )

    class Meta:
        model = Aggregate
        fields = ['family', 'date_added']

    def search(self, queryset, name, value):
        if not value.strip():
            return queryset
        qs_filter = Q(description__icontains=value)
        try:
            prefix = str(netaddr.IPNetwork(value.strip()).cidr)
            qs_filter |= Q(prefix__net_contains_or_equals=prefix)
        except (AddrFormatError, ValueError):
            pass
        return queryset.filter(qs_filter)


class RoleFilter(django_filters.FilterSet):

    class Meta:
        model = Role
        fields = ['name', 'slug']


class PrefixFilter(CustomFieldFilterSet, django_filters.FilterSet):
    id__in = NumericInFilter(name='id', lookup_expr='in')
    q = django_filters.CharFilter(
        method='search',
        label='Search',
    )
    within = django_filters.CharFilter(
        method='search_within',
        label='Within prefix',
    )
    within_include = django_filters.CharFilter(
        method='search_within_include',
        label='Within and including prefix',
    )
    contains = django_filters.CharFilter(
        method='search_contains',
        label='Prefixes which contain this prefix or IP',
    )
    mask_length = django_filters.NumberFilter(
        method='filter_mask_length',
        label='Mask length',
    )
    vrf_id = django_filters.ModelMultipleChoiceFilter(
        queryset=VRF.objects.all(),
        label='VRF',
    )
    vrf = django_filters.ModelMultipleChoiceFilter(
        name='vrf__rd',
        queryset=VRF.objects.all(),
        to_field_name='rd',
        label='VRF (RD)',
    )
    tenant_id = django_filters.ModelMultipleChoiceFilter(
        queryset=Tenant.objects.all(),
        label='Tenant (ID)',
    )
    tenant = django_filters.ModelMultipleChoiceFilter(
        name='tenant__slug',
        queryset=Tenant.objects.all(),
        to_field_name='slug',
        label='Tenant (slug)',
    )
    site_id = django_filters.ModelMultipleChoiceFilter(
        queryset=Site.objects.all(),
        label='Site (ID)',
    )
    site = django_filters.ModelMultipleChoiceFilter(
        name='site__slug',
        queryset=Site.objects.all(),
        to_field_name='slug',
        label='Site (slug)',
    )
    vlan_id = django_filters.ModelMultipleChoiceFilter(
        queryset=VLAN.objects.all(),
        label='VLAN (ID)',
    )
    vlan_vid = django_filters.NumberFilter(
        name='vlan__vid',
        label='VLAN number (1-4095)',
    )
    role_id = django_filters.ModelMultipleChoiceFilter(
        queryset=Role.objects.all(),
        label='Role (ID)',
    )
    role = django_filters.ModelMultipleChoiceFilter(
        name='role__slug',
        queryset=Role.objects.all(),
        to_field_name='slug',
        label='Role (slug)',
    )
    status = django_filters.MultipleChoiceFilter(
        choices=PREFIX_STATUS_CHOICES,
        null_value=None
    )
    tag = django_filters.CharFilter(
        name='tags__slug',
    )

    class Meta:
        model = Prefix
        fields = ['family', 'is_pool']

    def search(self, queryset, name, value):
        if not value.strip():
            return queryset
        qs_filter = Q(description__icontains=value)
        try:
            prefix = str(netaddr.IPNetwork(value.strip()).cidr)
            qs_filter |= Q(prefix__net_contains_or_equals=prefix)
        except (AddrFormatError, ValueError):
            pass
        return queryset.filter(qs_filter)

    def search_within(self, queryset, name, value):
        value = value.strip()
        if not value:
            return queryset
        try:
            query = str(netaddr.IPNetwork(value).cidr)
            return queryset.filter(prefix__net_contained=query)
        except (AddrFormatError, ValueError):
            return queryset.none()

    def search_within_include(self, queryset, name, value):
        value = value.strip()
        if not value:
            return queryset
        try:
            query = str(netaddr.IPNetwork(value).cidr)
            return queryset.filter(prefix__net_contained_or_equal=query)
        except (AddrFormatError, ValueError):
            return queryset.none()

    def search_contains(self, queryset, name, value):
        value = value.strip()
        if not value:
            return queryset
        try:
            # Searching by prefix
            if '/' in value:
                return queryset.filter(prefix__net_contains_or_equals=str(netaddr.IPNetwork(value).cidr))
            # Searching by IP address
            else:
                return queryset.filter(prefix__net_contains=str(netaddr.IPAddress(value)))
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
    address = django_filters.CharFilter(
        method='filter_address',
        label='Address',
    )
    mask_length = django_filters.NumberFilter(
        method='filter_mask_length',
        label='Mask length',
    )
    vrf_id = django_filters.ModelMultipleChoiceFilter(
        queryset=VRF.objects.all(),
        label='VRF',
    )
    vrf = django_filters.ModelMultipleChoiceFilter(
        name='vrf__rd',
        queryset=VRF.objects.all(),
        to_field_name='rd',
        label='VRF (RD)',
    )
    tenant_id = django_filters.ModelMultipleChoiceFilter(
        queryset=Tenant.objects.all(),
        label='Tenant (ID)',
    )
    tenant = django_filters.ModelMultipleChoiceFilter(
        name='tenant__slug',
        queryset=Tenant.objects.all(),
        to_field_name='slug',
        label='Tenant (slug)',
    )
    device = django_filters.CharFilter(
        method='filter_device',
        name='name',
        label='Device',
    )
    device_id = django_filters.NumberFilter(
        method='filter_device',
        name='pk',
        label='Device (ID)',
    )
    virtual_machine_id = django_filters.ModelMultipleChoiceFilter(
        name='interface__virtual_machine',
        queryset=VirtualMachine.objects.all(),
        label='Virtual machine (ID)',
    )
    virtual_machine = django_filters.ModelMultipleChoiceFilter(
        name='interface__virtual_machine__name',
        queryset=VirtualMachine.objects.all(),
        to_field_name='name',
        label='Virtual machine (name)',
    )
    interface_id = django_filters.ModelMultipleChoiceFilter(
        queryset=Interface.objects.all(),
        label='Interface (ID)',
    )
    status = django_filters.MultipleChoiceFilter(
        choices=IPADDRESS_STATUS_CHOICES,
        null_value=None
    )
    role = django_filters.MultipleChoiceFilter(
        choices=IPADDRESS_ROLE_CHOICES
    )
    tag = django_filters.CharFilter(
        name='tags__slug',
    )

    class Meta:
        model = IPAddress
        fields = ['family']

    def search(self, queryset, name, value):
        if not value.strip():
            return queryset
        qs_filter = (
            Q(description__icontains=value) |
            Q(address__istartswith=value)
        )
        return queryset.filter(qs_filter)

    def search_by_parent(self, queryset, name, value):
        value = value.strip()
        if not value:
            return queryset
        try:
            query = str(netaddr.IPNetwork(value.strip()).cidr)
            return queryset.filter(address__net_host_contained=query)
        except (AddrFormatError, ValueError):
            return queryset.none()

    def filter_address(self, queryset, name, value):
        if not value.strip():
            return queryset
        try:
            # Match address and subnet mask
            if '/' in value:
                return queryset.filter(address=value)
            return queryset.filter(address__net_host=value)
        except ValidationError:
            return queryset.none()

    def filter_mask_length(self, queryset, name, value):
        if not value:
            return queryset
        return queryset.filter(address__net_mask_length=value)

    def filter_device(self, queryset, name, value):
        try:
            device = Device.objects.select_related('device_type').get(**{name: value})
            vc_interface_ids = [i['id'] for i in device.vc_interfaces.values('id')]
            return queryset.filter(interface_id__in=vc_interface_ids)
        except Device.DoesNotExist:
            return queryset.none()


class VLANGroupFilter(django_filters.FilterSet):
    site_id = django_filters.ModelMultipleChoiceFilter(
        queryset=Site.objects.all(),
        label='Site (ID)',
    )
    site = django_filters.ModelMultipleChoiceFilter(
        name='site__slug',
        queryset=Site.objects.all(),
        to_field_name='slug',
        label='Site (slug)',
    )

    class Meta:
        model = VLANGroup
        fields = ['name', 'slug']


class VLANFilter(CustomFieldFilterSet, django_filters.FilterSet):
    id__in = NumericInFilter(name='id', lookup_expr='in')
    q = django_filters.CharFilter(
        method='search',
        label='Search',
    )
    site_id = django_filters.ModelMultipleChoiceFilter(
        queryset=Site.objects.all(),
        label='Site (ID)',
    )
    site = django_filters.ModelMultipleChoiceFilter(
        name='site__slug',
        queryset=Site.objects.all(),
        to_field_name='slug',
        label='Site (slug)',
    )
    group_id = django_filters.ModelMultipleChoiceFilter(
        queryset=VLANGroup.objects.all(),
        label='Group (ID)',
    )
    group = django_filters.ModelMultipleChoiceFilter(
        name='group__slug',
        queryset=VLANGroup.objects.all(),
        to_field_name='slug',
        label='Group',
    )
    tenant_id = django_filters.ModelMultipleChoiceFilter(
        queryset=Tenant.objects.all(),
        label='Tenant (ID)',
    )
    tenant = django_filters.ModelMultipleChoiceFilter(
        name='tenant__slug',
        queryset=Tenant.objects.all(),
        to_field_name='slug',
        label='Tenant (slug)',
    )
    role_id = django_filters.ModelMultipleChoiceFilter(
        queryset=Role.objects.all(),
        label='Role (ID)',
    )
    role = django_filters.ModelMultipleChoiceFilter(
        name='role__slug',
        queryset=Role.objects.all(),
        to_field_name='slug',
        label='Role (slug)',
    )
    status = django_filters.MultipleChoiceFilter(
        choices=VLAN_STATUS_CHOICES,
        null_value=None
    )
    tag = django_filters.CharFilter(
        name='tags__slug',
    )

    class Meta:
        model = VLAN
        fields = ['vid', 'name']

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
    q = django_filters.CharFilter(
        method='search',
        label='Search',
    )
    device_id = django_filters.ModelMultipleChoiceFilter(
        queryset=Device.objects.all(),
        label='Device (ID)',
    )
    device = django_filters.ModelMultipleChoiceFilter(
        name='device__name',
        queryset=Device.objects.all(),
        to_field_name='name',
        label='Device (name)',
    )
    virtual_machine_id = django_filters.ModelMultipleChoiceFilter(
        queryset=VirtualMachine.objects.all(),
        label='Virtual machine (ID)',
    )
    virtual_machine = django_filters.ModelMultipleChoiceFilter(
        name='virtual_machine__name',
        queryset=VirtualMachine.objects.all(),
        to_field_name='name',
        label='Virtual machine (name)',
    )
    tag = django_filters.CharFilter(
        name='tags__slug',
    )

    class Meta:
        model = Service
        fields = ['name', 'protocol', 'port']

    def search(self, queryset, name, value):
        if not value.strip():
            return queryset
        qs_filter = Q(name__icontains=value) | Q(description__icontains=value)
        return queryset.filter(qs_filter)
