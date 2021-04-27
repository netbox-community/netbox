import django_filters
from django.db.models import Q

from dcim.models import DeviceRole, Platform, Region, Site, SiteGroup
from extras.filters import CustomFieldModelFilterSet, CreatedUpdatedFilterSet, LocalConfigContextFilterSet
from tenancy.filters import TenancyFilterSet
from utilities.filters import (
    BaseFilterSet, MultiValueMACAddressFilter, NameSlugSearchFilterSet, TagFilter,
    TreeNodeMultipleChoiceFilter,
)
from .choices import *
from .models import Cluster, ClusterGroup, ClusterType, VirtualMachine, VMInterface

__all__ = (
    'ClusterFilterSet',
    'ClusterGroupFilterSet',
    'ClusterTypeFilterSet',
    'VirtualMachineFilterSet',
    'VMInterfaceFilterSet',
)


class ClusterTypeFilterSet(BaseFilterSet, NameSlugSearchFilterSet, CreatedUpdatedFilterSet):

    class Meta:
        model = ClusterType
        fields = ['id', 'name', 'slug', 'description']


class ClusterGroupFilterSet(BaseFilterSet, NameSlugSearchFilterSet, CreatedUpdatedFilterSet):

    class Meta:
        model = ClusterGroup
        fields = ['id', 'name', 'slug', 'description']


class ClusterFilterSet(BaseFilterSet, TenancyFilterSet, CustomFieldModelFilterSet, CreatedUpdatedFilterSet):
    q = django_filters.CharFilter(
        method='search',
        label='Search',
    )
    region_id = TreeNodeMultipleChoiceFilter(
        queryset=Region.objects.all(),
        field_name='site__region',
        lookup_expr='in',
        label='Region (ID)',
    )
    region = TreeNodeMultipleChoiceFilter(
        queryset=Region.objects.all(),
        field_name='site__region',
        lookup_expr='in',
        to_field_name='slug',
        label='Region (slug)',
    )
    site_group_id = TreeNodeMultipleChoiceFilter(
        queryset=SiteGroup.objects.all(),
        field_name='site__group',
        lookup_expr='in',
        label='Site group (ID)',
    )
    site_group = TreeNodeMultipleChoiceFilter(
        queryset=SiteGroup.objects.all(),
        field_name='site__group',
        lookup_expr='in',
        to_field_name='slug',
        label='Site group (slug)',
    )
    site_id = django_filters.ModelMultipleChoiceFilter(
        queryset=Site.objects.all(),
        label='Site (ID)',
    )
    site = django_filters.ModelMultipleChoiceFilter(
        field_name='site__slug',
        queryset=Site.objects.all(),
        to_field_name='slug',
        label='Site (slug)',
    )
    group_id = django_filters.ModelMultipleChoiceFilter(
        queryset=ClusterGroup.objects.all(),
        label='Parent group (ID)',
    )
    group = django_filters.ModelMultipleChoiceFilter(
        field_name='group__slug',
        queryset=ClusterGroup.objects.all(),
        to_field_name='slug',
        label='Parent group (slug)',
    )
    type_id = django_filters.ModelMultipleChoiceFilter(
        queryset=ClusterType.objects.all(),
        label='Cluster type (ID)',
    )
    type = django_filters.ModelMultipleChoiceFilter(
        field_name='type__slug',
        queryset=ClusterType.objects.all(),
        to_field_name='slug',
        label='Cluster type (slug)',
    )
    tag = TagFilter()

    class Meta:
        model = Cluster
        fields = ['id', 'name']

    def search(self, queryset, name, value):
        if not value.strip():
            return queryset
        return queryset.filter(
            Q(name__icontains=value) |
            Q(comments__icontains=value)
        )


class VirtualMachineFilterSet(
    BaseFilterSet,
    LocalConfigContextFilterSet,
    TenancyFilterSet,
    CustomFieldModelFilterSet,
    CreatedUpdatedFilterSet
):
    q = django_filters.CharFilter(
        method='search',
        label='Search',
    )
    status = django_filters.MultipleChoiceFilter(
        choices=VirtualMachineStatusChoices,
        null_value=None
    )
    cluster_group_id = django_filters.ModelMultipleChoiceFilter(
        field_name='cluster__group',
        queryset=ClusterGroup.objects.all(),
        label='Cluster group (ID)',
    )
    cluster_group = django_filters.ModelMultipleChoiceFilter(
        field_name='cluster__group__slug',
        queryset=ClusterGroup.objects.all(),
        to_field_name='slug',
        label='Cluster group (slug)',
    )
    cluster_type_id = django_filters.ModelMultipleChoiceFilter(
        field_name='cluster__type',
        queryset=ClusterType.objects.all(),
        label='Cluster type (ID)',
    )
    cluster_type = django_filters.ModelMultipleChoiceFilter(
        field_name='cluster__type__slug',
        queryset=ClusterType.objects.all(),
        to_field_name='slug',
        label='Cluster type (slug)',
    )
    cluster_id = django_filters.ModelMultipleChoiceFilter(
        queryset=Cluster.objects.all(),
        label='Cluster (ID)',
    )
    region_id = TreeNodeMultipleChoiceFilter(
        queryset=Region.objects.all(),
        field_name='cluster__site__region',
        lookup_expr='in',
        label='Region (ID)',
    )
    region = TreeNodeMultipleChoiceFilter(
        queryset=Region.objects.all(),
        field_name='cluster__site__region',
        lookup_expr='in',
        to_field_name='slug',
        label='Region (slug)',
    )
    site_group_id = TreeNodeMultipleChoiceFilter(
        queryset=SiteGroup.objects.all(),
        field_name='cluster__site__group',
        lookup_expr='in',
        label='Site group (ID)',
    )
    site_group = TreeNodeMultipleChoiceFilter(
        queryset=SiteGroup.objects.all(),
        field_name='cluster__site__group',
        lookup_expr='in',
        to_field_name='slug',
        label='Site group (slug)',
    )
    site_id = django_filters.ModelMultipleChoiceFilter(
        field_name='cluster__site',
        queryset=Site.objects.all(),
        label='Site (ID)',
    )
    site = django_filters.ModelMultipleChoiceFilter(
        field_name='cluster__site__slug',
        queryset=Site.objects.all(),
        to_field_name='slug',
        label='Site (slug)',
    )
    role_id = django_filters.ModelMultipleChoiceFilter(
        queryset=DeviceRole.objects.all(),
        label='Role (ID)',
    )
    role = django_filters.ModelMultipleChoiceFilter(
        field_name='role__slug',
        queryset=DeviceRole.objects.all(),
        to_field_name='slug',
        label='Role (slug)',
    )
    platform_id = django_filters.ModelMultipleChoiceFilter(
        queryset=Platform.objects.all(),
        label='Platform (ID)',
    )
    platform = django_filters.ModelMultipleChoiceFilter(
        field_name='platform__slug',
        queryset=Platform.objects.all(),
        to_field_name='slug',
        label='Platform (slug)',
    )
    mac_address = MultiValueMACAddressFilter(
        field_name='interfaces__mac_address',
        label='MAC address',
    )
    has_primary_ip = django_filters.BooleanFilter(
        method='_has_primary_ip',
        label='Has a primary IP',
    )
    tag = TagFilter()

    class Meta:
        model = VirtualMachine
        fields = ['id', 'name', 'cluster', 'vcpus', 'memory', 'disk']

    def search(self, queryset, name, value):
        if not value.strip():
            return queryset
        return queryset.filter(
            Q(name__icontains=value) |
            Q(comments__icontains=value)
        )

    def _has_primary_ip(self, queryset, name, value):
        params = Q(primary_ip4__isnull=False) | Q(primary_ip6__isnull=False)
        if value:
            return queryset.filter(params)
        return queryset.exclude(params)


class VMInterfaceFilterSet(BaseFilterSet, CustomFieldModelFilterSet, CreatedUpdatedFilterSet):
    q = django_filters.CharFilter(
        method='search',
        label='Search',
    )
    cluster_id = django_filters.ModelMultipleChoiceFilter(
        field_name='virtual_machine__cluster',
        queryset=Cluster.objects.all(),
        label='Cluster (ID)',
    )
    cluster = django_filters.ModelMultipleChoiceFilter(
        field_name='virtual_machine__cluster__name',
        queryset=Cluster.objects.all(),
        to_field_name='name',
        label='Cluster',
    )
    virtual_machine_id = django_filters.ModelMultipleChoiceFilter(
        field_name='virtual_machine',
        queryset=VirtualMachine.objects.all(),
        label='Virtual machine (ID)',
    )
    virtual_machine = django_filters.ModelMultipleChoiceFilter(
        field_name='virtual_machine__name',
        queryset=VirtualMachine.objects.all(),
        to_field_name='name',
        label='Virtual machine',
    )
    parent_id = django_filters.ModelMultipleChoiceFilter(
        field_name='parent',
        queryset=VMInterface.objects.all(),
        label='Parent interface (ID)',
    )
    mac_address = MultiValueMACAddressFilter(
        label='MAC address',
    )
    tag = TagFilter()

    class Meta:
        model = VMInterface
        fields = ['id', 'name', 'enabled', 'mtu']

    def search(self, queryset, name, value):
        if not value.strip():
            return queryset
        return queryset.filter(
            Q(name__icontains=value)
        )
