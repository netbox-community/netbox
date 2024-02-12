import strawberry
import strawberry_django

from ipam import models
from netbox.graphql.types import BaseObjectType, OrganizationalObjectType, NetBoxObjectType
from .filters import *

__all__ = (
    'ASNType',
    'ASNRangeType',
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
    'ServiceTemplateType',
    'VLANType',
    'VLANGroupType',
    'VRFType',
)


class IPAddressFamilyType:

    # value = graphene.Int()
    # label = graphene.String()

    def __init__(self, value):
        self.value = value
        self.label = f'IPv{value}'


class BaseIPAddressFamilyType:
    """
    Base type for models that need to expose their IPAddress family type.
    """
    # family = graphene.Field(IPAddressFamilyType)

    def resolve_family(self, _):
        # Note that self, is an instance of models.IPAddress
        # thus resolves to the address family value.
        return IPAddressFamilyType(self.family)


@strawberry_django.type(
    models.ASN,
    # fields='__all__',
    exclude=('asn',),  # bug - temp
    filters=ASNFilter
)
class ASNType(NetBoxObjectType):
    # asn = graphene.Field(BigInt)
    pass


@strawberry_django.type(
    models.ASNRange,
    # fields='__all__',
    exclude=('start', 'end',),  # bug - temp
    filters=ASNRangeFilter
)
class ASNRangeType(NetBoxObjectType):
    pass


@strawberry_django.type(
    models.Aggregate,
    # fields='__all__',
    exclude=('prefix',),  # bug - temp
    filters=AggregateFilter
)
class AggregateType(NetBoxObjectType, BaseIPAddressFamilyType):
    pass


@strawberry_django.type(
    models.FHRPGroup,
    fields='__all__',
    filters=FHRPGroupFilter
)
class FHRPGroupType(NetBoxObjectType):

    def resolve_auth_type(self, info):
        return self.auth_type or None


@strawberry_django.type(
    models.FHRPGroupAssignment,
    exclude=('interface_type', 'interface_id'),
    filters=FHRPGroupAssignmentFilter
)
class FHRPGroupAssignmentType(BaseObjectType):
    # interface = graphene.Field('ipam.graphql.gfk_mixins.FHRPGroupInterfaceType')
    pass


@strawberry_django.type(
    models.IPAddress,
    exclude=('assigned_object_type', 'assigned_object_id', 'address'),
    filters=IPAddressFilter
)
class IPAddressType(NetBoxObjectType, BaseIPAddressFamilyType):
    # assigned_object = graphene.Field('ipam.graphql.gfk_mixins.IPAddressAssignmentType')

    def resolve_role(self, info):
        return self.role or None


@strawberry_django.type(
    models.IPRange,
    # fields='__all__',
    exclude=('start_address', 'end_address',),  # bug - temp
    filters=IPRangeFilter
)
class IPRangeType(NetBoxObjectType):

    def resolve_role(self, info):
        return self.role or None


@strawberry_django.type(
    models.Prefix,
    # fields='__all__',
    exclude=('prefix',),  # bug - temp
    filters=PrefixFilter
)
class PrefixType(NetBoxObjectType, BaseIPAddressFamilyType):
    pass


@strawberry_django.type(
    models.RIR,
    fields='__all__',
    filters=RIRFilter
)
class RIRType(OrganizationalObjectType):
    pass


@strawberry_django.type(
    models.Role,
    fields='__all__',
    filters=RoleFilter
)
class RoleType(OrganizationalObjectType):
    pass


@strawberry_django.type(
    models.RouteTarget,
    fields='__all__',
    filters=RouteTargetFilter
)
class RouteTargetType(NetBoxObjectType):
    pass


@strawberry_django.type(
    models.Service,
    # fields='__all__',
    exclude=('ports',),  # bug - temp
    filters=ServiceFilter
)
class ServiceType(NetBoxObjectType):
    pass


@strawberry_django.type(
    models.ServiceTemplate,
    # fields='__all__',
    exclude=('ports',),  # bug - temp
    filters=ServiceTemplateFilter
)
class ServiceTemplateType(NetBoxObjectType):
    pass


@strawberry_django.type(
    models.VLAN,
    fields='__all__',
    filters=VLANFilter
)
class VLANType(NetBoxObjectType):
    pass


@strawberry_django.type(
    models.VLANGroup,
    exclude=('scope_type', 'scope_id'),
    filters=VLANGroupFilter
)
class VLANGroupType(OrganizationalObjectType):
    # scope = graphene.Field('ipam.graphql.gfk_mixins.VLANGroupScopeType')
    pass


@strawberry_django.type(
    models.VRF,
    fields='__all__',
    filters=VRFFilter
)
class VRFType(NetBoxObjectType):
    pass
