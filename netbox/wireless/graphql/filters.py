from typing import Annotated, TYPE_CHECKING
import strawberry
from strawberry.scalars import ID
import strawberry_django
from strawberry_django import (
    FilterLookup,
)
from extras.graphql.filter_mixins import *
from netbox.graphql.filter_mixins import *
from core.graphql.filter_mixins import *
from tenancy.graphql.filter_mixins import *
from .filter_mixins import *

from wireless import models

if TYPE_CHECKING:
    from .enums import *
    from netbox.graphql.enums import *
    from wireless.graphql.enums import *
    from core.graphql.filter_lookups import *
    from extras.graphql.filters import *
    from circuits.graphql.filters import *
    from dcim.graphql.filters import *
    from ipam.graphql.filters import *
    from tenancy.graphql.filters import *
    from wireless.graphql.filters import *
    from users.graphql.filters import *
    from virtualization.graphql.filters import *
    from vpn.graphql.filters import *

__all__ = (
    'WirelessLANGroupFilter',
    'WirelessLANFilter',
    'WirelessLinkFilter',
)


@strawberry_django.filter(models.WirelessLANGroup, lookups=True)
class WirelessLANGroupFilter(NestedGroupModelFilterMixin):
    pass


@strawberry_django.filter(models.WirelessLAN, lookups=True)
class WirelessLANFilter(WirelessAuthenticationBaseFilterMixin, PrimaryModelFilterMixin):
    ssid: FilterLookup[str] | None = strawberry_django.filter_field()
    group: Annotated['WirelessLANGroupFilter', strawberry.lazy('wireless.graphql.filters')] | None = (
        strawberry_django.filter_field()
    )
    group_id: ID | None = strawberry_django.filter_field()
    vlan: Annotated['VLANFilter', strawberry.lazy('ipam.graphql.filters')] | None = strawberry_django.filter_field()
    vlan_id: ID | None = strawberry_django.filter_field()
    tenant: Annotated['TenantFilter', strawberry.lazy('tenancy.graphql.filters')] | None = (
        strawberry_django.filter_field()
    )
    tenant_id: ID | None = strawberry_django.filter_field()


@strawberry_django.filter(models.WirelessLink, lookups=True)
class WirelessLinkFilter(WirelessAuthenticationBaseFilterMixin, DistanceFilterMixin, PrimaryModelFilterMixin):
    interface_a: Annotated['InterfaceFilter', strawberry.lazy('dcim.graphql.filters')] | None = (
        strawberry_django.filter_field()
    )
    interface_a_id: ID | None = strawberry_django.filter_field()
    interface_b: Annotated['InterfaceFilter', strawberry.lazy('dcim.graphql.filters')] | None = (
        strawberry_django.filter_field()
    )
    interface_b_id: ID | None = strawberry_django.filter_field()
    ssid: FilterLookup[str] | None = strawberry_django.filter_field()
    status: Annotated['WirelessLANStatusEnum', strawberry.lazy('wireless.graphql.enums')] | None = (
        strawberry_django.filter_field()
    )
    tenant: Annotated['TenantFilter', strawberry.lazy('tenancy.graphql.filters')] | None = (
        strawberry_django.filter_field()
    )
    tenant_id: ID | None = strawberry_django.filter_field()
