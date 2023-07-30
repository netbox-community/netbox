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
        if type(instance) is Interface:
            return InterfaceType
        if type(instance) is FHRPGroup:
            return FHRPGroupType
        if type(instance) is VMInterface:
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
        if type(instance) is Interface:
            return InterfaceType
        if type(instance) is VLAN:
            return VLANType
        if type(instance) is VMInterface:
            return VMInterfaceType


class FHRPGroupInterfaceType(graphene.Union):
    class Meta:
        types = (
            InterfaceType,
            VMInterfaceType,
        )

    @classmethod
    def resolve_type(cls, instance, info):
        if type(instance) is Interface:
            return InterfaceType
        if type(instance) is VMInterface:
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
        if type(instance) is Cluster:
            return ClusterType
        if type(instance) is ClusterGroup:
            return ClusterGroupType
        if type(instance) is Location:
            return LocationType
        if type(instance) is Rack:
            return RackType
        if type(instance) is Region:
            return RegionType
        if type(instance) is Site:
            return SiteType
        if type(instance) is SiteGroup:
            return SiteGroupType
