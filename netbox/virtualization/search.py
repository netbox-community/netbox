from netbox.search import SearchIndex, register_search
from . import models


@register_search
class ClusterIndex(SearchIndex):
    model = models.Cluster
    fields = (
        ('name', 100),
        ('description', 500),
        ('comments', 5000),
    )
    display_attrs = ('type', 'group', 'status', 'tenant', 'scope', 'description')


@register_search
class ClusterGroupIndex(SearchIndex):
    model = models.ClusterGroup
    fields = (
        ('name', 100),
        ('slug', 110),
        ('description', 500),
    )
    display_attrs = ('description',)


@register_search
class ClusterTypeIndex(SearchIndex):
    model = models.ClusterType
    fields = (
        ('name', 100),
        ('slug', 110),
        ('description', 500),
    )
    display_attrs = ('description',)


@register_search
class VirtualMachineIndex(SearchIndex):
    model = models.VirtualMachine
    fields = (
        ('serial', 60),
        ('name', 100),
        ('description', 500),
        ('comments', 5000),
    )
    display_attrs = ('site', 'cluster', 'device', 'tenant', 'platform', 'status', 'serial', 'role', 'description')


@register_search
class VMInterfaceIndex(SearchIndex):
    model = models.VMInterface
    fields = (
        ('name', 100),
        ('description', 500),
        ('mtu', 2000),
    )
    display_attrs = ('virtual_machine', 'description')


@register_search
class VirtualDiskIndex(SearchIndex):
    model = models.VirtualDisk
    fields = (
        ('name', 100),
        ('description', 500),
    )
    display_attrs = ('virtual_machine', 'size', 'description')
