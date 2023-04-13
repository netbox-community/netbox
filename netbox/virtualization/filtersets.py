import django_filters
from django.db.models import Q
from django.utils.translation import gettext as _

from dcim.filtersets import CommonInterfaceFilterSet
from dcim.models import Device, DeviceRole, Platform, Region, Site, SiteGroup
from extras.filtersets import LocalConfigContextFilterSet
from netbox.filtersets import OrganizationalModelFilterSet, NetBoxModelFilterSet
from tenancy.filtersets import TenancyFilterSet, ContactModelFilterSet
from utilities.filters import MultiValueCharFilter, MultiValueMACAddressFilter, TreeNodeMultipleChoiceFilter
from .choices import *
from .models import Cluster, ClusterGroup, ClusterType, VirtualMachine, VMInterface

__all__ = (
    'ClusterFilterSet',
    'ClusterGroupFilterSet',
    'ClusterTypeFilterSet',
    'VirtualMachineFilterSet',
    'VMInterfaceFilterSet',
)


class ClusterTypeFilterSet(OrganizationalModelFilterSet):

    class Meta:
        model = ClusterType
        fields = ['id', 'name', 'slug', 'description']


class ClusterGroupFilterSet(OrganizationalModelFilterSet, ContactModelFilterSet):

    class Meta:
        model = ClusterGroup
        fields = ['id', 'name', 'slug', 'description']


class ClusterFilterSet(NetBoxModelFilterSet, TenancyFilterSet, ContactModelFilterSet):
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
    site_group_id = TreeNodeMultipleChoiceFilter(
        queryset=SiteGroup.objects.all(),
        field_name='site__group',
        lookup_expr='in',
        label=_('Site group (ID)'),
    )
    site_group = TreeNodeMultipleChoiceFilter(
        queryset=SiteGroup.objects.all(),
        field_name='site__group',
        lookup_expr='in',
        to_field_name='slug',
        label=_('Site group (slug)'),
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
        queryset=ClusterGroup.objects.all(),
        label=_('Parent group (ID)'),
    )
    group = django_filters.ModelMultipleChoiceFilter(
        field_name='group__slug',
        queryset=ClusterGroup.objects.all(),
        to_field_name='slug',
        label=_('Parent group (slug)'),
    )
    type_id = django_filters.ModelMultipleChoiceFilter(
        queryset=ClusterType.objects.all(),
        label=_('Cluster type (ID)'),
    )
    type = django_filters.ModelMultipleChoiceFilter(
        field_name='type__slug',
        queryset=ClusterType.objects.all(),
        to_field_name='slug',
        label=_('Cluster type (slug)'),
    )
    status = django_filters.MultipleChoiceFilter(
        choices=ClusterStatusChoices,
        null_value=None
    )

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
    NetBoxModelFilterSet,
    TenancyFilterSet,
    ContactModelFilterSet,
    LocalConfigContextFilterSet
):
    status = django_filters.MultipleChoiceFilter(
        choices=VirtualMachineStatusChoices,
        null_value=None
    )
    cluster_group_id = django_filters.ModelMultipleChoiceFilter(
        field_name='cluster__group',
        queryset=ClusterGroup.objects.all(),
        label=_('Cluster group (ID)'),
    )
    cluster_group = django_filters.ModelMultipleChoiceFilter(
        field_name='cluster__group__slug',
        queryset=ClusterGroup.objects.all(),
        to_field_name='slug',
        label=_('Cluster group (slug)'),
    )
    cluster_type_id = django_filters.ModelMultipleChoiceFilter(
        field_name='cluster__type',
        queryset=ClusterType.objects.all(),
        label=_('Cluster type (ID)'),
    )
    cluster_type = django_filters.ModelMultipleChoiceFilter(
        field_name='cluster__type__slug',
        queryset=ClusterType.objects.all(),
        to_field_name='slug',
        label=_('Cluster type (slug)'),
    )
    cluster_id = django_filters.ModelMultipleChoiceFilter(
        queryset=Cluster.objects.all(),
        label=_('Cluster (ID)'),
    )
    cluster = django_filters.ModelMultipleChoiceFilter(
        field_name='cluster__name',
        queryset=Cluster.objects.all(),
        to_field_name='name',
        label=_('Cluster'),
    )
    device_id = django_filters.ModelMultipleChoiceFilter(
        queryset=Device.objects.all(),
        label=_('Device (ID)'),
    )
    device = django_filters.ModelMultipleChoiceFilter(
        field_name='device__name',
        queryset=Device.objects.all(),
        to_field_name='name',
        label=_('Device'),
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
    site_group_id = TreeNodeMultipleChoiceFilter(
        queryset=SiteGroup.objects.all(),
        field_name='site__group',
        lookup_expr='in',
        label=_('Site group (ID)'),
    )
    site_group = TreeNodeMultipleChoiceFilter(
        queryset=SiteGroup.objects.all(),
        field_name='site__group',
        lookup_expr='in',
        to_field_name='slug',
        label=_('Site group (slug)'),
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
    name = MultiValueCharFilter(
        lookup_expr='iexact'
    )
    role_id = django_filters.ModelMultipleChoiceFilter(
        queryset=DeviceRole.objects.all(),
        label=_('Role (ID)'),
    )
    role = django_filters.ModelMultipleChoiceFilter(
        field_name='role__slug',
        queryset=DeviceRole.objects.all(),
        to_field_name='slug',
        label=_('Role (slug)'),
    )
    platform_id = django_filters.ModelMultipleChoiceFilter(
        queryset=Platform.objects.all(),
        label=_('Platform (ID)'),
    )
    platform = django_filters.ModelMultipleChoiceFilter(
        field_name='platform__slug',
        queryset=Platform.objects.all(),
        to_field_name='slug',
        label=_('Platform (slug)'),
    )
    mac_address = MultiValueMACAddressFilter(
        field_name='interfaces__mac_address',
        label=_('MAC address'),
    )
    has_primary_ip = django_filters.BooleanFilter(
        method='_has_primary_ip',
        label=_('Has a primary IP'),
    )

    class Meta:
        model = VirtualMachine
        fields = ['id', 'cluster', 'vcpus', 'memory', 'disk']

    def search(self, queryset, name, value):
        if not value.strip():
            return queryset
        return queryset.filter(
            Q(name__icontains=value) |
            Q(comments__icontains=value) |
            Q(primary_ip4__address__startswith=value) |
            Q(primary_ip6__address__startswith=value)
        )

    def _has_primary_ip(self, queryset, name, value):
        params = Q(primary_ip4__isnull=False) | Q(primary_ip6__isnull=False)
        if value:
            return queryset.filter(params)
        return queryset.exclude(params)


class VMInterfaceFilterSet(NetBoxModelFilterSet, CommonInterfaceFilterSet):
    cluster_id = django_filters.ModelMultipleChoiceFilter(
        field_name='virtual_machine__cluster',
        queryset=Cluster.objects.all(),
        label=_('Cluster (ID)'),
    )
    cluster = django_filters.ModelMultipleChoiceFilter(
        field_name='virtual_machine__cluster__name',
        queryset=Cluster.objects.all(),
        to_field_name='name',
        label=_('Cluster'),
    )
    virtual_machine_id = django_filters.ModelMultipleChoiceFilter(
        field_name='virtual_machine',
        queryset=VirtualMachine.objects.all(),
        label=_('Virtual machine (ID)'),
    )
    virtual_machine = django_filters.ModelMultipleChoiceFilter(
        field_name='virtual_machine__name',
        queryset=VirtualMachine.objects.all(),
        to_field_name='name',
        label=_('Virtual machine'),
    )
    parent_id = django_filters.ModelMultipleChoiceFilter(
        field_name='parent',
        queryset=VMInterface.objects.all(),
        label=_('Parent interface (ID)'),
    )
    bridge_id = django_filters.ModelMultipleChoiceFilter(
        field_name='bridge',
        queryset=VMInterface.objects.all(),
        label=_('Bridged interface (ID)'),
    )
    mac_address = MultiValueMACAddressFilter(
        label=_('MAC address'),
    )

    class Meta:
        model = VMInterface
        fields = ['id', 'name', 'enabled', 'mtu', 'description']

    def search(self, queryset, name, value):
        if not value.strip():
            return queryset
        return queryset.filter(
            Q(name__icontains=value) |
            Q(description__icontains=value)
        )
