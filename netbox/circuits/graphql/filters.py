from datetime import date
from typing import Annotated, TYPE_CHECKING

import strawberry
import strawberry_django
from strawberry.scalars import ID
from strawberry_django import FilterLookup, DateFilterLookup

from circuits import models
from core.graphql.filter_mixins import BaseObjectTypeFilterMixin, ChangeLogFilterMixin
from dcim.graphql.filter_mixins import CabledObjectModelFilterMixin
from extras.graphql.filter_mixins import CustomFieldsFilterMixin, TagsFilterMixin
from netbox.graphql.filter_mixins import (
    DistanceFilterMixin,
    ImageAttachmentFilterMixin,
    OrganizationalModelFilterMixin,
    PrimaryModelFilterMixin,
)
from tenancy.graphql.filter_mixins import ContactFilterMixin, TenancyFilterMixin
from .filter_mixins import BaseCircuitTypeFilterMixin

if TYPE_CHECKING:
    from core.graphql.filters import ContentTypeFilter
    from dcim.graphql.filters import InterfaceFilter, LocationFilter, RegionFilter, SiteFilter, SiteGroupFilter
    from ipam.graphql.filters import ASNFilter
    from netbox.graphql.filter_lookups import IntegerLookup
    from .enums import *

__all__ = (
    'CircuitFilter',
    'CircuitGroupAssignmentFilter',
    'CircuitGroupFilter',
    'CircuitTerminationFilter',
    'CircuitTypeFilter',
    'ProviderFilter',
    'ProviderAccountFilter',
    'ProviderNetworkFilter',
    'VirtualCircuitFilter',
    'VirtualCircuitTerminationFilter',
    'VirtualCircuitTypeFilter',
)


@strawberry_django.filter_type(models.CircuitTermination, lookups=True)
class CircuitTerminationFilter(
    BaseObjectTypeFilterMixin,
    CustomFieldsFilterMixin,
    TagsFilterMixin,
    ChangeLogFilterMixin,
    CabledObjectModelFilterMixin,
):
    circuit: Annotated['CircuitFilter', strawberry.lazy('circuits.graphql.filters')] | None = (
        strawberry_django.filter_field()
    )
    term_side: Annotated['CircuitTerminationSideEnum', strawberry.lazy('circuits.graphql.enums')] | None = (
        strawberry_django.filter_field()
    )
    termination_type: Annotated['ContentTypeFilter', strawberry.lazy('core.graphql.filters')] | None = (
        strawberry_django.filter_field()
    )
    termination_id: ID | None = strawberry_django.filter_field()
    port_speed: Annotated['IntegerLookup', strawberry.lazy('netbox.graphql.filter_lookups')] | None = (
        strawberry_django.filter_field()
    )
    upstream_speed: Annotated['IntegerLookup', strawberry.lazy('netbox.graphql.filter_lookups')] | None = (
        strawberry_django.filter_field()
    )
    xconnect_id: FilterLookup[str] | None = strawberry_django.filter_field()
    pp_info: FilterLookup[str] | None = strawberry_django.filter_field()
    description: FilterLookup[str] | None = strawberry_django.filter_field()

    # Cached relations
    _provider_network: Annotated['ProviderNetworkFilter', strawberry.lazy('circuits.graphql.filters')] | None = (
        strawberry_django.filter_field(name='provider_network')
    )
    _location: Annotated['LocationFilter', strawberry.lazy('dcim.graphql.filters')] | None = (
        strawberry_django.filter_field(name='location')
    )
    _region: Annotated['RegionFilter', strawberry.lazy('dcim.graphql.filters')] | None = (
        strawberry_django.filter_field(name='region')
    )
    _site_group: Annotated['SiteGroupFilter', strawberry.lazy('dcim.graphql.filters')] | None = (
        strawberry_django.filter_field(name='site_group')
    )
    _site: Annotated['SiteFilter', strawberry.lazy('dcim.graphql.filters')] | None = (
        strawberry_django.filter_field(name='site')
    )


@strawberry_django.filter_type(models.Circuit, lookups=True)
class CircuitFilter(
    ContactFilterMixin,
    ImageAttachmentFilterMixin,
    DistanceFilterMixin,
    TenancyFilterMixin,
    PrimaryModelFilterMixin
):
    cid: FilterLookup[str] | None = strawberry_django.filter_field()
    provider: Annotated['ProviderFilter', strawberry.lazy('circuits.graphql.filters')] | None = (
        strawberry_django.filter_field()
    )
    provider_id: ID | None = strawberry_django.filter_field()
    provider_account: Annotated['ProviderAccountFilter', strawberry.lazy('circuits.graphql.filters')] | None = (
        strawberry_django.filter_field()
    )
    provider_account_id: ID | None = strawberry_django.filter_field()
    type: Annotated['CircuitTypeFilter', strawberry.lazy('circuits.graphql.filters')] | None = (
        strawberry_django.filter_field()
    )
    type_id: ID | None = strawberry_django.filter_field()
    status: Annotated['CircuitStatusEnum', strawberry.lazy('circuits.graphql.enums')] | None = (
        strawberry_django.filter_field()
    )
    install_date: DateFilterLookup[date] | None = strawberry_django.filter_field()
    termination_date: DateFilterLookup[date] | None = strawberry_django.filter_field()
    commit_rate: Annotated['IntegerLookup', strawberry.lazy('netbox.graphql.filter_lookups')] | None = (
        strawberry_django.filter_field()
    )
    terminations: Annotated['CircuitTerminationFilter', strawberry.lazy('circuits.graphql.filters')] | None = (
        strawberry_django.filter_field()
    )


@strawberry_django.filter_type(models.CircuitType, lookups=True)
class CircuitTypeFilter(BaseCircuitTypeFilterMixin):
    pass


@strawberry_django.filter_type(models.CircuitGroup, lookups=True)
class CircuitGroupFilter(TenancyFilterMixin, OrganizationalModelFilterMixin):
    pass


@strawberry_django.filter_type(models.CircuitGroupAssignment, lookups=True)
class CircuitGroupAssignmentFilter(
    BaseObjectTypeFilterMixin, CustomFieldsFilterMixin, TagsFilterMixin, ChangeLogFilterMixin
):
    member_type: Annotated['ContentTypeFilter', strawberry.lazy('core.graphql.filters')] | None = (
        strawberry_django.filter_field()
    )
    member_id: ID | None = strawberry_django.filter_field()
    group: Annotated['CircuitGroupFilter', strawberry.lazy('circuits.graphql.filters')] | None = (
        strawberry_django.filter_field()
    )
    group_id: ID | None = strawberry_django.filter_field()
    priority: Annotated['CircuitPriorityEnum', strawberry.lazy('circuits.graphql.enums')] | None = (
        strawberry_django.filter_field()
    )


@strawberry_django.filter_type(models.Provider, lookups=True)
class ProviderFilter(ContactFilterMixin, PrimaryModelFilterMixin):
    name: FilterLookup[str] | None = strawberry_django.filter_field()
    slug: FilterLookup[str] | None = strawberry_django.filter_field()
    asns: Annotated['ASNFilter', strawberry.lazy('ipam.graphql.filters')] | None = strawberry_django.filter_field()
    circuits: Annotated['CircuitFilter', strawberry.lazy('circuits.graphql.filters')] | None = (
        strawberry_django.filter_field()
    )


@strawberry_django.filter_type(models.ProviderAccount, lookups=True)
class ProviderAccountFilter(ContactFilterMixin, PrimaryModelFilterMixin):
    provider: Annotated['ProviderFilter', strawberry.lazy('circuits.graphql.filters')] | None = (
        strawberry_django.filter_field()
    )
    provider_id: ID | None = strawberry_django.filter_field()
    account: FilterLookup[str] | None = strawberry_django.filter_field()
    name: FilterLookup[str] | None = strawberry_django.filter_field()


@strawberry_django.filter_type(models.ProviderNetwork, lookups=True)
class ProviderNetworkFilter(PrimaryModelFilterMixin):
    name: FilterLookup[str] | None = strawberry_django.filter_field()
    provider: Annotated['ProviderFilter', strawberry.lazy('circuits.graphql.filters')] | None = (
        strawberry_django.filter_field()
    )
    provider_id: ID | None = strawberry_django.filter_field()
    service_id: FilterLookup[str] | None = strawberry_django.filter_field()


@strawberry_django.filter_type(models.VirtualCircuitType, lookups=True)
class VirtualCircuitTypeFilter(BaseCircuitTypeFilterMixin):
    pass


@strawberry_django.filter_type(models.VirtualCircuit, lookups=True)
class VirtualCircuitFilter(TenancyFilterMixin, PrimaryModelFilterMixin):
    cid: FilterLookup[str] | None = strawberry_django.filter_field()
    provider_network: Annotated['ProviderNetworkFilter', strawberry.lazy('circuits.graphql.filters')] | None = (
        strawberry_django.filter_field()
    )
    provider_network_id: ID | None = strawberry_django.filter_field()
    provider_account: Annotated['ProviderAccountFilter', strawberry.lazy('circuits.graphql.filters')] | None = (
        strawberry_django.filter_field()
    )
    provider_account_id: ID | None = strawberry_django.filter_field()
    type: Annotated['VirtualCircuitTypeFilter', strawberry.lazy('circuits.graphql.filters')] | None = (
        strawberry_django.filter_field()
    )
    type_id: ID | None = strawberry_django.filter_field()
    status: Annotated['CircuitStatusEnum', strawberry.lazy('circuits.graphql.enums')] | None = (
        strawberry_django.filter_field()
    )
    group_assignments: Annotated['CircuitGroupAssignmentFilter', strawberry.lazy('circuits.graphql.filters')] | None = (
        strawberry_django.filter_field()
    )


@strawberry_django.filter_type(models.VirtualCircuitTermination, lookups=True)
class VirtualCircuitTerminationFilter(
    BaseObjectTypeFilterMixin, CustomFieldsFilterMixin, TagsFilterMixin, ChangeLogFilterMixin
):
    virtual_circuit: Annotated['VirtualCircuitFilter', strawberry.lazy('circuits.graphql.filters')] | None = (
        strawberry_django.filter_field()
    )
    virtual_circuit_id: ID | None = strawberry_django.filter_field()
    role: Annotated['VirtualCircuitTerminationRoleEnum', strawberry.lazy('circuits.graphql.enums')] | None = (
        strawberry_django.filter_field()
    )
    interface: Annotated['InterfaceFilter', strawberry.lazy('dcim.graphql.filters')] | None = (
        strawberry_django.filter_field()
    )
    interface_id: ID | None = strawberry_django.filter_field()
    description: FilterLookup[str] | None = strawberry_django.filter_field()
