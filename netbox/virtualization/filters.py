from __future__ import unicode_literals

import django_filters
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from netaddr import EUI
from netaddr.core import AddrFormatError

from dcim.models import DeviceRole, Interface, Platform, Region, Site
from extras.filters import CustomFieldFilterSet
from tenancy.models import Tenant
from utilities.filters import NumericInFilter, TagFilter
from .constants import VM_STATUS_CHOICES
from .models import Cluster, ClusterGroup, ClusterType, VirtualMachine


class ClusterTypeFilter(django_filters.FilterSet):

    class Meta:
        model = ClusterType
        fields = ['name', 'slug']


class ClusterGroupFilter(django_filters.FilterSet):

    class Meta:
        model = ClusterGroup
        fields = ['name', 'slug']


class ClusterFilter(CustomFieldFilterSet):
    id__in = NumericInFilter(name='id', lookup_expr='in')
    q = django_filters.CharFilter(
        method='search',
        label='Search',
    )
    group_id = django_filters.ModelMultipleChoiceFilter(
        queryset=ClusterGroup.objects.all(),
        label='Parent group (ID)',
    )
    group = django_filters.ModelMultipleChoiceFilter(
        name='group__slug',
        queryset=ClusterGroup.objects.all(),
        to_field_name='slug',
        label='Parent group (slug)',
    )
    type_id = django_filters.ModelMultipleChoiceFilter(
        queryset=ClusterType.objects.all(),
        label='Cluster type (ID)',
    )
    type = django_filters.ModelMultipleChoiceFilter(
        name='type__slug',
        queryset=ClusterType.objects.all(),
        to_field_name='slug',
        label='Cluster type (slug)',
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
    tag = TagFilter()

    class Meta:
        model = Cluster
        fields = ['name']

    def search(self, queryset, name, value):
        if not value.strip():
            return queryset
        return queryset.filter(
            Q(name__icontains=value) |
            Q(comments__icontains=value)
        )


class VirtualMachineFilter(CustomFieldFilterSet):
    id__in = NumericInFilter(name='id', lookup_expr='in')
    q = django_filters.CharFilter(
        method='search',
        label='Search',
    )
    status = django_filters.MultipleChoiceFilter(
        choices=VM_STATUS_CHOICES,
        null_value=None
    )
    cluster_group_id = django_filters.ModelMultipleChoiceFilter(
        name='cluster__group',
        queryset=ClusterGroup.objects.all(),
        label='Cluster group (ID)',
    )
    cluster_group = django_filters.ModelMultipleChoiceFilter(
        name='cluster__group__slug',
        queryset=ClusterGroup.objects.all(),
        to_field_name='slug',
        label='Cluster group (slug)',
    )
    cluster_type_id = django_filters.ModelMultipleChoiceFilter(
        name='cluster__type',
        queryset=ClusterType.objects.all(),
        label='Cluster type (ID)',
    )
    cluster_type = django_filters.ModelMultipleChoiceFilter(
        name='cluster__type__slug',
        queryset=ClusterType.objects.all(),
        to_field_name='slug',
        label='Cluster type (slug)',
    )
    cluster_id = django_filters.ModelMultipleChoiceFilter(
        queryset=Cluster.objects.all(),
        label='Cluster (ID)',
    )
    region_id = django_filters.NumberFilter(
        method='filter_region',
        name='pk',
        label='Region (ID)',
    )
    region = django_filters.CharFilter(
        method='filter_region',
        name='slug',
        label='Region (slug)',
    )
    site_id = django_filters.ModelMultipleChoiceFilter(
        name='cluster__site',
        queryset=Site.objects.all(),
        label='Site (ID)',
    )
    site = django_filters.ModelMultipleChoiceFilter(
        name='cluster__site__slug',
        queryset=Site.objects.all(),
        to_field_name='slug',
        label='Site (slug)',
    )
    role_id = django_filters.ModelMultipleChoiceFilter(
        queryset=DeviceRole.objects.all(),
        label='Role (ID)',
    )
    role = django_filters.ModelMultipleChoiceFilter(
        name='role__slug',
        queryset=DeviceRole.objects.all(),
        to_field_name='slug',
        label='Role (slug)',
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
    platform_id = django_filters.ModelMultipleChoiceFilter(
        queryset=Platform.objects.all(),
        label='Platform (ID)',
    )
    platform = django_filters.ModelMultipleChoiceFilter(
        name='platform__slug',
        queryset=Platform.objects.all(),
        to_field_name='slug',
        label='Platform (slug)',
    )
    tag = TagFilter()

    class Meta:
        model = VirtualMachine
        fields = ['name', 'cluster']

    def search(self, queryset, name, value):
        if not value.strip():
            return queryset
        return queryset.filter(
            Q(name__icontains=value) |
            Q(comments__icontains=value)
        )

    def filter_region(self, queryset, name, value):
        try:
            region = Region.objects.get(**{name: value})
        except ObjectDoesNotExist:
            return queryset.none()
        return queryset.filter(
            Q(cluster__site__region=region) |
            Q(cluster__site__region__in=region.get_descendants())
        )


class InterfaceFilter(django_filters.FilterSet):
    virtual_machine_id = django_filters.ModelMultipleChoiceFilter(
        name='virtual_machine',
        queryset=VirtualMachine.objects.all(),
        label='Virtual machine (ID)',
    )
    virtual_machine = django_filters.ModelMultipleChoiceFilter(
        name='virtual_machine__name',
        queryset=VirtualMachine.objects.all(),
        to_field_name='name',
        label='Virtual machine',
    )
    mac_address = django_filters.CharFilter(
        method='_mac_address',
        label='MAC address',
    )

    class Meta:
        model = Interface
        fields = ['name', 'enabled', 'mtu']

    def _mac_address(self, queryset, name, value):
        value = value.strip()
        if not value:
            return queryset
        try:
            mac = EUI(value.strip())
            return queryset.filter(mac_address=mac)
        except AddrFormatError:
            return queryset.none()
