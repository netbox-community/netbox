import graphene

from extras.graphql.mixins import ContactsMixin
from ipam import filtersets, models
from netbox.graphql.scalars import BigInt
from netbox.graphql.types import BaseObjectType, OrganizationalObjectType, NetBoxObjectType

__all__ = (
    'ASNType',
    'ASNRangeType',
    'AggregateType',
    'FHRPGroupType',
    'FHRPGroupAssignmentType',
    'IPAddressType',
    'IPRangeType',
    'L2VPNType',
    'L2VPNTerminationType',
    'PrefixType',
    'RIRType',
    'RoleType',
    'RouteTargetType',
    'ServiceType',
    'ServiceTemplateType',
    'VLANType',
    'VLANGroupType',
    'VRFType',
)


class IPAddressFamilyType(graphene.ObjectType):

    value = graphene.Int()
    label = graphene.String()

    def __init__(self, value):
        self.value = value
        self.label = f'IPv{value}'


class BaseIPAddressFamilyType:
    """
    Base type for models that need to expose their IPAddress family type.
    """
    family = graphene.Field(IPAddressFamilyType)

    def resolve_family(self, _):
        # Note that self, is an instance of models.IPAddress
        # thus resolves to the address family value.
        return IPAddressFamilyType(self.family)


class ASNType(NetBoxObjectType):
    asn = graphene.Field(BigInt)

    class Meta:
        model = models.ASN
        fields = '__all__'
        filterset_class = filtersets.ASNFilterSet


class ASNRangeType(NetBoxObjectType):

    class Meta:
        model = models.ASNRange
        fields = '__all__'
        filterset_class = filtersets.ASNRangeFilterSet


class AggregateType(NetBoxObjectType, BaseIPAddressFamilyType):

    class Meta:
        model = models.Aggregate
        fields = '__all__'
        filterset_class = filtersets.AggregateFilterSet


class FHRPGroupType(NetBoxObjectType):

    class Meta:
        model = models.FHRPGroup
        fields = '__all__'
        filterset_class = filtersets.FHRPGroupFilterSet

    def resolve_auth_type(self, info):
        return self.auth_type or None


class FHRPGroupAssignmentType(BaseObjectType):
    interface = graphene.Field('ipam.graphql.gfk_mixins.FHRPGroupInterfaceType')

    class Meta:
        model = models.FHRPGroupAssignment
        exclude = ('interface_type', 'interface_id')
        filterset_class = filtersets.FHRPGroupAssignmentFilterSet


class IPAddressType(NetBoxObjectType, BaseIPAddressFamilyType):
    assigned_object = graphene.Field('ipam.graphql.gfk_mixins.IPAddressAssignmentType')

    class Meta:
        model = models.IPAddress
        exclude = ('assigned_object_type', 'assigned_object_id')
        filterset_class = filtersets.IPAddressFilterSet

    def resolve_role(self, info):
        return self.role or None


class IPRangeType(NetBoxObjectType):

    class Meta:
        model = models.IPRange
        fields = '__all__'
        filterset_class = filtersets.IPRangeFilterSet

    def resolve_role(self, info):
        return self.role or None


class PrefixType(NetBoxObjectType, BaseIPAddressFamilyType):

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


class RouteTargetType(NetBoxObjectType):

    class Meta:
        model = models.RouteTarget
        fields = '__all__'
        filterset_class = filtersets.RouteTargetFilterSet


class ServiceType(NetBoxObjectType):

    class Meta:
        model = models.Service
        fields = '__all__'
        filterset_class = filtersets.ServiceFilterSet


class ServiceTemplateType(NetBoxObjectType):

    class Meta:
        model = models.ServiceTemplate
        fields = '__all__'
        filterset_class = filtersets.ServiceTemplateFilterSet


class VLANType(NetBoxObjectType):

    class Meta:
        model = models.VLAN
        fields = '__all__'
        filterset_class = filtersets.VLANFilterSet


class VLANGroupType(OrganizationalObjectType):
    scope = graphene.Field('ipam.graphql.gfk_mixins.VLANGroupScopeType')

    class Meta:
        model = models.VLANGroup
        exclude = ('scope_type', 'scope_id')
        filterset_class = filtersets.VLANGroupFilterSet


class VRFType(NetBoxObjectType):

    class Meta:
        model = models.VRF
        fields = '__all__'
        filterset_class = filtersets.VRFFilterSet


class L2VPNType(ContactsMixin, NetBoxObjectType):
    class Meta:
        model = models.L2VPN
        fields = '__all__'
        filtersets_class = filtersets.L2VPNFilterSet


class L2VPNTerminationType(NetBoxObjectType):
    assigned_object = graphene.Field('ipam.graphql.gfk_mixins.L2VPNAssignmentType')

    class Meta:
        model = models.L2VPNTermination
        exclude = ('assigned_object_type', 'assigned_object_id')
        filtersets_class = filtersets.L2VPNTerminationFilterSet
