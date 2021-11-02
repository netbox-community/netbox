from ipam import filtersets, models
from netbox.graphql.types import OrganizationalObjectType, PrimaryObjectType

__all__ = (
    'AggregateType',
    'FHRPGroupType',
    'FHRPGroupAssignmentType',
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


class AggregateType(PrimaryObjectType):

    class Meta:
        model = models.Aggregate
        fields = '__all__'
        filterset_class = filtersets.AggregateFilterSet


class FHRPGroupType(PrimaryObjectType):

    class Meta:
        model = models.FHRPGroup
        fields = '__all__'
        filterset_class = filtersets.FHRPGroupFilterSet

    def resolve_auth_type(self, info):
        return self.auth_type or None


class FHRPGroupAssignmentType(PrimaryObjectType):

    class Meta:
        model = models.FHRPGroupAssignment
        fields = '__all__'
        filterset_class = filtersets.FHRPGroupAssignmentFilterSet


class IPAddressType(PrimaryObjectType):

    class Meta:
        model = models.IPAddress
        fields = '__all__'
        filterset_class = filtersets.IPAddressFilterSet

    def resolve_role(self, info):
        return self.role or None


class IPRangeType(PrimaryObjectType):

    class Meta:
        model = models.IPRange
        fields = '__all__'
        filterset_class = filtersets.IPRangeFilterSet

    def resolve_role(self, info):
        return self.role or None


class PrefixType(PrimaryObjectType):

    class Meta:
        model = models.Prefix
        fields = '__all__'
        filterset_class = filtersets.PrefixFilterSet


class RIRType(OrganizationalObjectType):

    class Meta:
        model = models.RIR
        fields = '__all__'
        filterset_class = filtersets.RIRFilterSet


class RoleType(OrganizationalObjectType):

    class Meta:
        model = models.Role
        fields = '__all__'
        filterset_class = filtersets.RoleFilterSet


class RouteTargetType(PrimaryObjectType):

    class Meta:
        model = models.RouteTarget
        fields = '__all__'
        filterset_class = filtersets.RouteTargetFilterSet


class ServiceType(PrimaryObjectType):

    class Meta:
        model = models.Service
        fields = '__all__'
        filterset_class = filtersets.ServiceFilterSet


class VLANType(PrimaryObjectType):

    class Meta:
        model = models.VLAN
        fields = '__all__'
        filterset_class = filtersets.VLANFilterSet


class VLANGroupType(OrganizationalObjectType):

    class Meta:
        model = models.VLANGroup
        fields = '__all__'
        filterset_class = filtersets.VLANGroupFilterSet


class VRFType(PrimaryObjectType):

    class Meta:
        model = models.VRF
        fields = '__all__'
        filterset_class = filtersets.VRFFilterSet
