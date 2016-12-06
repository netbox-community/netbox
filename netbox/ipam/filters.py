import django_filters
from netaddr import IPNetwork
from netaddr.core import AddrFormatError

from django.db.models import Q

from dcim.models import Site, Device, Interface
from extras.filters import CustomFieldFilterSet
from tenancy.models import Tenant
from utilities.filters import NullableModelMultipleChoiceFilter

from .models import RIR, Aggregate, VRF, Prefix, IPAddress, VLAN, VLANGroup, Role


class VRFFilter(CustomFieldFilterSet, django_filters.FilterSet):
    q = django_filters.MethodFilter(
        action='search',
        label='Search',
    )
    name = django_filters.CharFilter(
        name='name',
        lookup_type='icontains',
        label='Name',
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

    def search(self, queryset, value):
        return queryset.filter(
            Q(name__icontains=value) |
            Q(rd__icontains=value) |
            Q(description__icontains=value)
        )

    class Meta:
        model = VRF
        fields = ['name', 'rd']


class RIRFilter(django_filters.FilterSet):

    class Meta:
        model = RIR
        fields = ['is_private']


class AggregateFilter(CustomFieldFilterSet, django_filters.FilterSet):
    q = django_filters.MethodFilter(
        action='search',
        label='Search',
    )
    rir_id = django_filters.ModelMultipleChoiceFilter(
        name='rir',
        queryset=RIR.objects.all(),
        label='RIR (ID)',
    )
    rir = django_filters.ModelMultipleChoiceFilter(
        name='rir',
        queryset=RIR.objects.all(),
        to_field_name='slug',
        label='RIR (slug)',
    )

    class Meta:
        model = Aggregate
        fields = ['family', 'rir_id', 'rir', 'date_added']

    def search(self, queryset, value):
        qs_filter = Q(description__icontains=value)
        try:
            prefix = str(IPNetwork(value.strip()).cidr)
            qs_filter |= Q(prefix__net_contains_or_equals=prefix)
        except AddrFormatError:
            pass
        return queryset.filter(qs_filter)


class PrefixFilter(CustomFieldFilterSet, django_filters.FilterSet):
    q = django_filters.MethodFilter(
        action='search',
        label='Search',
    )
    parent = django_filters.MethodFilter(
        action='search_by_parent',
        label='Parent prefix',
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
    vlan_id = django_filters.ModelMultipleChoiceFilter(
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

    class Meta:
        model = Prefix
        fields = ['family', 'site_id', 'site', 'vlan_id', 'vlan_vid', 'status', 'role_id', 'role']

    def search(self, queryset, value):
        qs_filter = Q(description__icontains=value)
        try:
            prefix = str(IPNetwork(value.strip()).cidr)
            qs_filter |= Q(prefix__net_contains_or_equals=prefix)
        except AddrFormatError:
            pass
        return queryset.filter(qs_filter)

    def search_by_parent(self, queryset, value):
        value = value.strip()
        if not value:
            return queryset
        try:
            query = str(IPNetwork(value).cidr)
            return queryset.filter(prefix__net_contained_or_equal=query)
        except AddrFormatError:
            return queryset.none()

    def _tenant(self, queryset, value):
        if str(value) == '':
            return queryset
        return queryset.filter(
            Q(tenant__slug=value) |
            Q(tenant__isnull=True, vrf__tenant__slug=value)
        )

    def _tenant_id(self, queryset, value):
        try:
            value = int(value)
        except ValueError:
            return queryset.none()
        return queryset.filter(
            Q(tenant__pk=value) |
            Q(tenant__isnull=True, vrf__tenant__pk=value)
        )


class IPAddressFilter(CustomFieldFilterSet, django_filters.FilterSet):
    q = django_filters.MethodFilter(
        action='search',
        label='Search',
    )
    parent = django_filters.MethodFilter(
        action='search_by_parent',
        label='Parent prefix',
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
        name='interface__device',
        queryset=Device.objects.all(),
        to_field_name='name',
        label='Device (name)',
    )
    interface_id = django_filters.ModelMultipleChoiceFilter(
        name='interface',
        queryset=Interface.objects.all(),
        label='Interface (ID)',
    )

    class Meta:
        model = IPAddress
        fields = ['q', 'family', 'status', 'device_id', 'device', 'interface_id']

    def search(self, queryset, value):
        qs_filter = Q(description__icontains=value)
        try:
            ipaddress = str(IPNetwork(value.strip()))
            qs_filter |= Q(address__net_host=ipaddress)
        except AddrFormatError:
            pass
        return queryset.filter(qs_filter)

    def search_by_parent(self, queryset, value):
        value = value.strip()
        if not value:
            return queryset
        try:
            query = str(IPNetwork(value).cidr)
            return queryset.filter(address__net_contained_or_equal=query)
        except AddrFormatError:
            return queryset.none()


class VLANGroupFilter(django_filters.FilterSet):
    site_id = django_filters.ModelMultipleChoiceFilter(
        name='site',
        queryset=Site.objects.all(),
        label='Site (ID)',
    )
    site = django_filters.ModelMultipleChoiceFilter(
        name='site',
        queryset=Site.objects.all(),
        to_field_name='slug',
        label='Site (slug)',
    )

    class Meta:
        model = VLANGroup
        fields = ['site_id', 'site']


class VLANFilter(CustomFieldFilterSet, django_filters.FilterSet):
    q = django_filters.MethodFilter(
        action='search',
        label='Search',
    )
    site_id = django_filters.ModelMultipleChoiceFilter(
        name='site',
        queryset=Site.objects.all(),
        label='Site (ID)',
    )
    site = django_filters.ModelMultipleChoiceFilter(
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
    name = django_filters.CharFilter(
        name='name',
        lookup_type='icontains',
        label='Name',
    )
    vid = django_filters.NumberFilter(
        name='vid',
        label='VLAN number (1-4095)',
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

    class Meta:
        model = VLAN
        fields = ['site_id', 'site', 'vid', 'name', 'status', 'role_id', 'role']

    def search(self, queryset, value):
        qs_filter = Q(name__icontains=value) | Q(description__icontains=value)
        try:
            qs_filter |= Q(vid=int(value))
        except ValueError:
            pass
        return queryset.filter(qs_filter)
