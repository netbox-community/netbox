import graphene
from dcim.graphql.types import (
    InterfaceType,
    LocationType,
    RackType,
    RegionType,
    SiteGroupType,
    SiteType,
)
from dcim.models import Interface, Location, Rack, Region, Site, SiteGroup
from ipam.graphql.types import FHRPGroupType, VLANType
from ipam.models import VLAN, FHRPGroup
from virtualization.graphql.types import ClusterGroupType, ClusterType, VMInterfaceType
from virtualization.models import Cluster, ClusterGroup, VMInterface


class IPAddressAssignmentType(graphene.Union):
    class Meta:
        types = (
            InterfaceType,
            FHRPGroupType,
            VMInterfaceType,
        )

    @classmethod
    def resolve_type(cls, instance, info):
        if type(instance) == Interface:
            return InterfaceType
        if type(instance) == FHRPGroup:
            return FHRPGroupType
        if type(instance) == VMInterface:
            return VMInterfaceType


class L2VPNAssignmentType(graphene.Union):
    class Meta:
        types = (
            InterfaceType,
            VLANType,
            VMInterfaceType,
        )

    @classmethod
    def resolve_type(cls, instance, info):
        if type(instance) == Interface:
            return InterfaceType
        if type(instance) == VLAN:
            return VLANType
        if type(instance) == VMInterface:
            return VMInterfaceType


class FHRPGroupInterfaceType(graphene.Union):
    class Meta:
        types = (
            InterfaceType,
            VMInterfaceType,
        )

    @classmethod
    def resolve_type(cls, instance, info):
        if type(instance) == Interface:
            return InterfaceType
        if type(instance) == VMInterface:
            return VMInterfaceType


class VLANGroupScopeType(graphene.Union):
    class Meta:
        types = (
            ClusterType,
            ClusterGroupType,
            LocationType,
            RackType,
            RegionType,
            SiteType,
            SiteGroupType,
        )

    @classmethod
    def resolve_type(cls, instance, info):
        if type(instance) == Cluster:
            return ClusterType
        if type(instance) == ClusterGroup:
            return ClusterGroupType
        if type(instance) == Location:
            return LocationType
        if type(instance) == Rack:
            return RackType
        if type(instance) == Region:
            return RegionType
        if type(instance) == Site:
            return SiteType
        if type(instance) == SiteGroup:
            return SiteGroupType
