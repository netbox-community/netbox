from typing import Annotated, TYPE_CHECKING

import strawberry
import strawberry_django
from strawberry.scalars import ID
from strawberry_django import FilterLookup

from dcim.graphql.filter_mixins import ScopedFilterMixin
from netbox.graphql.filter_mixins import DistanceFilterMixin, PrimaryModelFilterMixin, NestedGroupModelFilterMixin
from tenancy.graphql.filter_mixins import TenancyFilterMixin
from wireless import models
from .filter_mixins import WirelessAuthenticationBaseFilterMixin

if TYPE_CHECKING:
    from dcim.graphql.filters import InterfaceFilter
    from ipam.graphql.filters import VLANFilter
    from .enums import *

__all__ = (
    'WirelessLANGroupFilter',
    'WirelessLANFilter',
    'WirelessLinkFilter',
)


@strawberry_django.filter_type(models.WirelessLANGroup, lookups=True)
class WirelessLANGroupFilter(NestedGroupModelFilterMixin):
    pass


@strawberry_django.filter_type(models.WirelessLAN, lookups=True)
class WirelessLANFilter(
    WirelessAuthenticationBaseFilterMixin,
    ScopedFilterMixin,
    TenancyFilterMixin,
    PrimaryModelFilterMixin
):
    ssid: FilterLookup[str] | None = strawberry_django.filter_field()
    status: Annotated['WirelessLANStatusEnum', strawberry.lazy('wireless.graphql.enums')] | None = (
        strawberry_django.filter_field()
    )
    group: Annotated['WirelessLANGroupFilter', strawberry.lazy('wireless.graphql.filters')] | None = (
        strawberry_django.filter_field()
    )
    group_id: ID | None = strawberry_django.filter_field()
    vlan: Annotated['VLANFilter', strawberry.lazy('ipam.graphql.filters')] | None = strawberry_django.filter_field()
    vlan_id: ID | None = strawberry_django.filter_field()


@strawberry_django.filter_type(models.WirelessLink, lookups=True)
class WirelessLinkFilter(
    WirelessAuthenticationBaseFilterMixin,
    DistanceFilterMixin,
    TenancyFilterMixin,
    PrimaryModelFilterMixin
):
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
