from typing import Annotated, List, Union

import strawberry
import strawberry_django

from wireless import models
from netbox.graphql.types import OrganizationalObjectType, NetBoxObjectType
from .filters import *

__all__ = (
    'WirelessLANType',
    'WirelessLANGroupType',
    'WirelessLinkType',
)


@strawberry_django.type(
    models.WirelessLANGroup,
    # fields='__all__',
    exclude=('parent',),  # bug - temp
    filters=WirelessLANGroupFilter
)
class WirelessLANGroupType(OrganizationalObjectType):

    @strawberry_django.field
    def parent(self) -> Annotated["WirelessLANGroupType", strawberry.lazy('wireless.graphql.types')]:
        return self.parent

    @strawberry_django.field
    def wireless_lans(self) -> List[Annotated["WirelessLANType", strawberry.lazy('wireless.graphql.types')]]:
        return self.wireless_lans.all()

    @strawberry_django.field
    def children(self) -> List[Annotated["WirelessLANGroupType", strawberry.lazy('wireless.graphql.types')]]:
        return self.children.all()


@strawberry_django.type(
    models.WirelessLAN,
    fields='__all__',
    filters=WirelessLANFilter
)
class WirelessLANType(NetBoxObjectType):

    @strawberry_django.field
    def interfaces(self) -> List[Annotated["InterfaceType", strawberry.lazy('dcim.graphql.types')]]:
        return self.interfaces.all()


@strawberry_django.type(
    models.WirelessLink,
    fields='__all__',
    filters=WirelessLinkFilter
)
class WirelessLinkType(NetBoxObjectType):
    pass
