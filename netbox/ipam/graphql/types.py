from ipam import filtersets, models
from netbox.graphql.types import ObjectType, TaggedObjectType

__all__ = (
    'AggregateType',
    'IPAddressType',
    'IPRangeType',
    'PrefixType',
    'RIRType',
    'RoleType',
    'RouteTargetType',
    'ServiceType',
    'VLANType',
    'VLANGroupType',
    'VRFType',
)


class AggregateType(TaggedObjectType):

    class Meta:
        model = models.Aggregate
        fields = '__all__'
        filterset_class = filtersets.AggregateFilterSet


class IPAddressType(TaggedObjectType):

    class Meta:
        model = models.IPAddress
        fields = '__all__'
        filterset_class = filtersets.IPAddressFilterSet

    def resolve_role(self, info):
        return self.role or None


class IPRangeType(TaggedObjectType):

    class Meta:
        model = models.IPRange
        fields = '__all__'
        filterset_class = filtersets.IPRangeFilterSet

    def resolve_role(self, info):
        return self.role or None


class PrefixType(TaggedObjectType):

    class Meta:
        model = models.Prefix
        fields = '__all__'
        filterset_class = filtersets.PrefixFilterSet


class RIRType(ObjectType):

    class Meta:
        model = models.RIR
        fields = '__all__'
        filterset_class = filtersets.RIRFilterSet


class RoleType(ObjectType):

    class Meta:
        model = models.Role
        fields = '__all__'
        filterset_class = filtersets.RoleFilterSet


class RouteTargetType(TaggedObjectType):

    class Meta:
        model = models.RouteTarget
        fields = '__all__'
        filterset_class = filtersets.RouteTargetFilterSet


class ServiceType(TaggedObjectType):

    class Meta:
        model = models.Service
        fields = '__all__'
        filterset_class = filtersets.ServiceFilterSet


class VLANType(TaggedObjectType):

    class Meta:
        model = models.VLAN
        fields = '__all__'
        filterset_class = filtersets.VLANFilterSet


class VLANGroupType(ObjectType):

    class Meta:
        model = models.VLANGroup
        fields = '__all__'
        filterset_class = filtersets.VLANGroupFilterSet


class VRFType(TaggedObjectType):

    class Meta:
        model = models.VRF
        fields = '__all__'
        filterset_class = filtersets.VRFFilterSet
