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
    pass


@strawberry_django.type(
    models.WirelessLAN,
    fields='__all__',
    filters=WirelessLANFilter
)
class WirelessLANType(NetBoxObjectType):

    def resolve_auth_type(self, info):
        return self.auth_type or None

    def resolve_auth_cipher(self, info):
        return self.auth_cipher or None


@strawberry_django.type(
    models.WirelessLink,
    fields='__all__',
    filters=WirelessLinkFilter
)
class WirelessLinkType(NetBoxObjectType):

    def resolve_auth_type(self, info):
        return self.auth_type or None

    def resolve_auth_cipher(self, info):
        return self.auth_cipher or None
