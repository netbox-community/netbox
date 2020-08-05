import django_filters
import netaddr
from django.core.exceptions import ValidationError
from django.db.models import Q
from django.utils.translation import gettext as _
from netaddr.core import AddrFormatError

from dcim.models import Device, Interface, Region, Site
from extras.filters import CustomFieldFilterSet, CreatedUpdatedFilterSet
from tenancy.filters import TenancyFilterSet
from utilities.filters import (
    BaseFilterSet, MultiValueCharFilter, MultiValueNumberFilter, NameSlugSearchFilterSet, TagFilter,
    TreeNodeMultipleChoiceFilter,
)
from virtualization.models import VirtualMachine
from .choices import *
from .models import Aggregate, IPAddress, Prefix, RIR, Role, Service, VLAN, VLANGroup, VRF


__all__ = (
    'AggregateFilterSet',
    'IPAddressFilterSet',
    'PrefixFilterSet',
    'RIRFilterSet',
    'RoleFilterSet',
    'ServiceFilterSet',
    'VLANFilterSet',
    'VLANGroupFilterSet',
    'VRFFilterSet',
)


class VRFFilterSet(BaseFilterSet, TenancyFilterSet, CustomFieldFilterSet, CreatedUpdatedFilterSet):
    q = django_filters.CharFilter(
        method='search',
        label=_('Search'),
    )
    tag = TagFilter()

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
        fields = ['id', 'name', 'rd', 'enforce_unique']


class RIRFilterSet(BaseFilterSet, NameSlugSearchFilterSet):

    class Meta:
        model = RIR
        fields = ['id', 'name', 'slug', 'is_private', 'description']


class AggregateFilterSet(BaseFilterSet, CustomFieldFilterSet, CreatedUpdatedFilterSet):
    q = django_filters.CharFilter(
        method='search',
        label=_('Search'),
    )
    family = django_filters.NumberFilter(
        field_name='prefix',
        lookup_expr='family'
    )
    prefix = django_filters.CharFilter(
        method='filter_prefix',
        label=_('Prefix'),
    )
    rir_id = django_filters.ModelMultipleChoiceFilter(
        queryset=RIR.objects.all(),
        label=_('RIR (ID)'),
    )
    rir = django_filters.ModelMultipleChoiceFilter(
        field_name='rir__slug',
        queryset=RIR.objects.all(),
        to_field_name='slug',
        label=_('RIR (slug)'),
    )
    tag = TagFilter()

    class Meta:
        model = Aggregate
        fields = ['id', 'date_added']

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

    def filter_prefix(self, queryset, name, value):
        if not value.strip():
            return queryset
        try:
            query = str(netaddr.IPNetwork(value).cidr)
            return queryset.filter(prefix=query)
        except (AddrFormatError, ValueError):
            return queryset.none()


class RoleFilterSet(BaseFilterSet, NameSlugSearchFilterSet):
    q = django_filters.CharFilter(
        method='search',
        label=_('Search'),
    )

    class Meta:
        model = Role
        fields = ['id', 'name', 'slug']


class PrefixFilterSet(BaseFilterSet, TenancyFilterSet, CustomFieldFilterSet, CreatedUpdatedFilterSet):
    q = django_filters.CharFilter(
        method='search',
        label=_('Search'),
    )
    family = django_filters.NumberFilter(
        field_name='prefix',
        lookup_expr='family'
    )
    prefix = django_filters.CharFilter(
        method='filter_prefix',
        label=_('Prefix'),
    )
    within = django_filters.CharFilter(
        method='search_within',
        label=_('Within prefix'),
    )
    within_include = django_filters.CharFilter(
        method='search_within_include',
        label=_('Within and including prefix'),
    )
    contains = django_filters.CharFilter(
        method='search_contains',
        label=_('Prefixes which contain this prefix or IP'),
    )
    mask_length = django_filters.NumberFilter(
        method='filter_mask_length',
        label=_('Mask length'),
    )
    vrf_id = django_filters.ModelMultipleChoiceFilter(
        queryset=VRF.objects.all(),
        label=_('VRF'),
    )
    vrf = django_filters.ModelMultipleChoiceFilter(
        field_name='vrf__rd',
        queryset=VRF.objects.all(),
        to_field_name='rd',
        label=_('VRF (RD)'),
    )
    region_id = TreeNodeMultipleChoiceFilter(
        queryset=Region.objects.all(),
        field_name='site__region',
        lookup_expr='in',
        label=_('Region (ID)'),
    )
    region = TreeNodeMultipleChoiceFilter(
        queryset=Region.objects.all(),
        field_name='site__region',
        lookup_expr='in',
        to_field_name='slug',
        label=_('Region (slug)'),
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
    vlan_id = django_filters.ModelMultipleChoiceFilter(
        queryset=VLAN.objects.all(),
        label=_('VLAN (ID)'),
    )
    vlan_vid = django_filters.NumberFilter(
        field_name='vlan__vid',
        label=_('VLAN number (1-4095)'),
    )
    role_id = django_filters.ModelMultipleChoiceFilter(
        queryset=Role.objects.all(),
        label=_('Role (ID)'),
    )
    role = django_filters.ModelMultipleChoiceFilter(
        field_name='role__slug',
        queryset=Role.objects.all(),
        to_field_name='slug',
        label=_('Role (slug)'),
    )
    status = django_filters.MultipleChoiceFilter(
        choices=PrefixStatusChoices,
        null_value=None
    )
    tag = TagFilter()

    class Meta:
        model = Prefix
        fields = ['id', 'is_pool']

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

    def filter_prefix(self, queryset, name, value):
        if not value.strip():
            return queryset
        try:
            query = str(netaddr.IPNetwork(value).cidr)
            return queryset.filter(prefix=query)
        except (AddrFormatError, ValueError):
            return queryset.none()

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


class IPAddressFilterSet(BaseFilterSet, TenancyFilterSet, CustomFieldFilterSet, CreatedUpdatedFilterSet):
    q = django_filters.CharFilter(
        method='search',
        label=_('Search'),
    )
    family = django_filters.NumberFilter(
        field_name='address',
        lookup_expr='family'
    )
    parent = django_filters.CharFilter(
        method='search_by_parent',
        label=_('Parent prefix'),
    )
    address = MultiValueCharFilter(
        method='filter_address',
        label=_('Address'),
    )
    mask_length = django_filters.NumberFilter(
        method='filter_mask_length',
        label=_('Mask length'),
    )
    vrf_id = django_filters.ModelMultipleChoiceFilter(
        queryset=VRF.objects.all(),
        label=_('VRF'),
    )
    vrf = django_filters.ModelMultipleChoiceFilter(
        field_name='vrf__rd',
        queryset=VRF.objects.all(),
        to_field_name='rd',
        label=_('VRF (RD)'),
    )
    device = MultiValueCharFilter(
        method='filter_device',
        field_name='name',
        label=_('Device (name)'),
    )
    device_id = MultiValueNumberFilter(
        method='filter_device',
        field_name='pk',
        label=_('Device (ID)'),
    )
    virtual_machine_id = django_filters.ModelMultipleChoiceFilter(
        field_name='interface__virtual_machine',
        queryset=VirtualMachine.objects.all(),
        label=_('Virtual machine (ID)'),
    )
    virtual_machine = django_filters.ModelMultipleChoiceFilter(
        field_name='interface__virtual_machine__name',
        queryset=VirtualMachine.objects.all(),
        to_field_name='name',
        label=_('Virtual machine (name)'),
    )
    interface = django_filters.ModelMultipleChoiceFilter(
        field_name='interface__name',
        queryset=Interface.objects.all(),
        to_field_name='name',
        label=_('Interface (ID)'),
    )
    interface_id = django_filters.ModelMultipleChoiceFilter(
        queryset=Interface.objects.all(),
        label=_('Interface (ID)'),
    )
    assigned_to_interface = django_filters.BooleanFilter(
        method='_assigned_to_interface',
        label=_('Is assigned to an interface'),
    )
    status = django_filters.MultipleChoiceFilter(
        choices=IPAddressStatusChoices,
        null_value=None
    )
    role = django_filters.MultipleChoiceFilter(
        choices=IPAddressRoleChoices
    )
    tag = TagFilter()

    class Meta:
        model = IPAddress
        fields = ['id', 'dns_name']

    def search(self, queryset, name, value):
        if not value.strip():
            return queryset
        qs_filter = (
            Q(dns_name__icontains=value) |
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
        try:
            return queryset.filter(address__net_in=value)
        except ValidationError:
            return queryset.none()

    def filter_mask_length(self, queryset, name, value):
        if not value:
            return queryset
        return queryset.filter(address__net_mask_length=value)

    def filter_device(self, queryset, name, value):
        try:
            devices = Device.objects.prefetch_related('device_type').filter(**{'{}__in'.format(name): value})
            vc_interface_ids = []
            for device in devices:
                vc_interface_ids.extend([i['id'] for i in device.vc_interfaces.values('id')])
            return queryset.filter(interface_id__in=vc_interface_ids)
        except Device.DoesNotExist:
            return queryset.none()

    def _assigned_to_interface(self, queryset, name, value):
        return queryset.exclude(interface__isnull=value)


class VLANGroupFilterSet(BaseFilterSet, NameSlugSearchFilterSet):
    region_id = TreeNodeMultipleChoiceFilter(
        queryset=Region.objects.all(),
        field_name='site__region',
        lookup_expr='in',
        label=_('Region (ID)'),
    )
    region = TreeNodeMultipleChoiceFilter(
        queryset=Region.objects.all(),
        field_name='site__region',
        lookup_expr='in',
        to_field_name='slug',
        label=_('Region (slug)'),
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

    class Meta:
        model = VLANGroup
        fields = ['id', 'name', 'slug', 'description']


class VLANFilterSet(BaseFilterSet, TenancyFilterSet, CustomFieldFilterSet, CreatedUpdatedFilterSet):
    q = django_filters.CharFilter(
        method='search',
        label=_('Search'),
    )
    region_id = TreeNodeMultipleChoiceFilter(
        queryset=Region.objects.all(),
        field_name='site__region',
        lookup_expr='in',
        label=_('Region (ID)'),
    )
    region = TreeNodeMultipleChoiceFilter(
        queryset=Region.objects.all(),
        field_name='site__region',
        lookup_expr='in',
        to_field_name='slug',
        label=_('Region (slug)'),
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
    group_id = django_filters.ModelMultipleChoiceFilter(
        queryset=VLANGroup.objects.all(),
        label=_('Group (ID)'),
    )
    group = django_filters.ModelMultipleChoiceFilter(
        field_name='group__slug',
        queryset=VLANGroup.objects.all(),
        to_field_name='slug',
        label=_('Group'),
    )
    role_id = django_filters.ModelMultipleChoiceFilter(
        queryset=Role.objects.all(),
        label=_('Role (ID)'),
    )
    role = django_filters.ModelMultipleChoiceFilter(
        field_name='role__slug',
        queryset=Role.objects.all(),
        to_field_name='slug',
        label=_('Role (slug)'),
    )
    status = django_filters.MultipleChoiceFilter(
        choices=VLANStatusChoices,
        null_value=None
    )
    tag = TagFilter()

    class Meta:
        model = VLAN
        fields = ['id', 'vid', 'name']

    def search(self, queryset, name, value):
        if not value.strip():
            return queryset
        qs_filter = Q(name__icontains=value) | Q(description__icontains=value)
        try:
            qs_filter |= Q(vid=int(value.strip()))
        except ValueError:
            pass
        return queryset.filter(qs_filter)


class ServiceFilterSet(BaseFilterSet, CreatedUpdatedFilterSet):
    q = django_filters.CharFilter(
        method='search',
        label=_('Search'),
    )
    device_id = django_filters.ModelMultipleChoiceFilter(
        queryset=Device.objects.all(),
        label=_('Device (ID)'),
    )
    device = django_filters.ModelMultipleChoiceFilter(
        field_name='device__name',
        queryset=Device.objects.all(),
        to_field_name='name',
        label=_('Device (name)'),
    )
    virtual_machine_id = django_filters.ModelMultipleChoiceFilter(
        queryset=VirtualMachine.objects.all(),
        label=_('Virtual machine (ID)'),
    )
    virtual_machine = django_filters.ModelMultipleChoiceFilter(
        field_name='virtual_machine__name',
        queryset=VirtualMachine.objects.all(),
        to_field_name='name',
        label=_('Virtual machine (name)'),
    )
    tag = TagFilter()

    class Meta:
        model = Service
        fields = ['id', 'name', 'protocol', 'port']

    def search(self, queryset, name, value):
        if not value.strip():
            return queryset
        qs_filter = Q(name__icontains=value) | Q(description__icontains=value)
        return queryset.filter(qs_filter)
