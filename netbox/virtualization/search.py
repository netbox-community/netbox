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


@register_search
class ClusterGroupIndex(SearchIndex):
    model = models.ClusterGroup
    fields = (
        ('name', 100),
        ('slug', 110),
        ('description', 500),
    )


@register_search
class ClusterTypeIndex(SearchIndex):
    model = models.ClusterType
    fields = (
        ('name', 100),
        ('slug', 110),
        ('description', 500),
    )


@register_search
class VirtualMachineIndex(SearchIndex):
    model = models.VirtualMachine
    fields = (
        ('name', 100),
        ('description', 500),
        ('comments', 5000),
    )


@register_search
class VMInterfaceIndex(SearchIndex):
    model = models.VMInterface
    fields = (
        ('name', 100),
        ('mac_address', 300),
        ('description', 500),
        ('mtu', 2000),
    )
