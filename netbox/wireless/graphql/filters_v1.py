from typing import Annotated, TYPE_CHECKING

import strawberry
import strawberry_django
from strawberry.scalars import ID
from strawberry_django import FilterLookup

from dcim.graphql.filter_mixins_v1 import ScopedFilterMixinV1
from netbox.graphql.filter_mixins_v1 import (
    DistanceFilterMixinV1, PrimaryModelFilterMixinV1, NestedGroupModelFilterMixinV1
)
from tenancy.graphql.filter_mixins_v1 import TenancyFilterMixinV1
from wireless import models
from .filter_mixins_v1 import WirelessAuthenticationBaseFilterMixinV1

if TYPE_CHECKING:
    from dcim.graphql.filters_v1 import InterfaceFilterV1
    from ipam.graphql.filters_v1 import VLANFilterV1
    from .enums import *

__all__ = (
    'WirelessLANGroupFilterV1',
    'WirelessLANFilterV1',
    'WirelessLinkFilterV1',
)


@strawberry_django.filter_type(models.WirelessLANGroup, lookups=True)
class WirelessLANGroupFilterV1(NestedGroupModelFilterMixinV1):
    pass


@strawberry_django.filter_type(models.WirelessLAN, lookups=True)
class WirelessLANFilterV1(
    WirelessAuthenticationBaseFilterMixinV1,
    ScopedFilterMixinV1,
    TenancyFilterMixinV1,
    PrimaryModelFilterMixinV1
):
    ssid: FilterLookup[str] | None = strawberry_django.filter_field()
    status: Annotated['WirelessLANStatusEnum', strawberry.lazy('wireless.graphql.enums')] | None = (
        strawberry_django.filter_field()
    )
    group: Annotated['WirelessLANGroupFilterV1', strawberry.lazy('wireless.graphql.filters_v1')] | None = (
        strawberry_django.filter_field()
    )
    group_id: ID | None = strawberry_django.filter_field()
    vlan: Annotated['VLANFilterV1', strawberry.lazy('ipam.graphql.filters_v1')] | None = (
        strawberry_django.filter_field()
    )
    vlan_id: ID | None = strawberry_django.filter_field()


@strawberry_django.filter_type(models.WirelessLink, lookups=True)
class WirelessLinkFilterV1(
    WirelessAuthenticationBaseFilterMixinV1,
    DistanceFilterMixinV1,
    TenancyFilterMixinV1,
    PrimaryModelFilterMixinV1
):
    interface_a: Annotated['InterfaceFilterV1', strawberry.lazy('dcim.graphql.filters_v1')] | None = (
        strawberry_django.filter_field()
    )
    interface_a_id: ID | None = strawberry_django.filter_field()
    interface_b: Annotated['InterfaceFilterV1', strawberry.lazy('dcim.graphql.filters_v1')] | None = (
        strawberry_django.filter_field()
    )
    interface_b_id: ID | None = strawberry_django.filter_field()
    ssid: FilterLookup[str] | None = strawberry_django.filter_field()
    status: Annotated['WirelessLANStatusEnum', strawberry.lazy('wireless.graphql.enums')] | None = (
        strawberry_django.filter_field()
    )
