from datetime import date
from typing import Annotated, TYPE_CHECKING

import strawberry
import strawberry_django
from strawberry.scalars import ID
from strawberry_django import FilterLookup, DateFilterLookup

from circuits import models
from core.graphql.filter_mixins_v1 import BaseObjectTypeFilterMixinV1, ChangeLogFilterMixinV1
from dcim.graphql.filter_mixins_v1 import CabledObjectModelFilterMixinV1
from extras.graphql.filter_mixins_v1 import CustomFieldsFilterMixinV1, TagsFilterMixinV1
from netbox.graphql.filter_mixins_v1 import (
    DistanceFilterMixinV1,
    ImageAttachmentFilterMixinV1,
    OrganizationalModelFilterMixinV1,
    PrimaryModelFilterMixinV1,
)
from tenancy.graphql.filter_mixins_v1 import ContactFilterMixinV1, TenancyFilterMixinV1
from .filter_mixins_v1 import BaseCircuitTypeFilterMixinV1

if TYPE_CHECKING:
    from core.graphql.filters_v1 import ContentTypeFilterV1
    from dcim.graphql.filters_v1 import (
        InterfaceFilterV1, LocationFilterV1, RegionFilterV1, SiteFilterV1, SiteGroupFilterV1
    )
    from ipam.graphql.filters_v1 import ASNFilterV1
    from netbox.graphql.filter_lookups import IntegerLookup
    from .enums import *

__all__ = (
    'CircuitFilterV1',
    'CircuitGroupAssignmentFilterV1',
    'CircuitGroupFilterV1',
    'CircuitTerminationFilterV1',
    'CircuitTypeFilterV1',
    'ProviderFilterV1',
    'ProviderAccountFilterV1',
    'ProviderNetworkFilterV1',
    'VirtualCircuitFilterV1',
    'VirtualCircuitTerminationFilterV1',
    'VirtualCircuitTypeFilterV1',
)


@strawberry_django.filter_type(models.CircuitTermination, lookups=True)
class CircuitTerminationFilterV1(
    BaseObjectTypeFilterMixinV1,
    CustomFieldsFilterMixinV1,
    TagsFilterMixinV1,
    ChangeLogFilterMixinV1,
    CabledObjectModelFilterMixinV1,
):
    circuit: Annotated['CircuitFilterV1', strawberry.lazy('circuits.graphql.filters_v1')] | None = (
        strawberry_django.filter_field()
    )
    term_side: Annotated['CircuitTerminationSideEnum', strawberry.lazy('circuits.graphql.enums')] | None = (
        strawberry_django.filter_field()
    )
    termination_type: Annotated['ContentTypeFilterV1', strawberry.lazy('core.graphql.filters_v1')] | None = (
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
    _provider_network: Annotated['ProviderNetworkFilterV1', strawberry.lazy('circuits.graphql.filters_v1')] | None = (
        strawberry_django.filter_field(name='provider_network')
    )
    _location: Annotated['LocationFilterV1', strawberry.lazy('dcim.graphql.filters_v1')] | None = (
        strawberry_django.filter_field(name='location')
    )
    _region: Annotated['RegionFilterV1', strawberry.lazy('dcim.graphql.filters_v1')] | None = (
        strawberry_django.filter_field(name='region')
    )
    _site_group: Annotated['SiteGroupFilterV1', strawberry.lazy('dcim.graphql.filters_v1')] | None = (
        strawberry_django.filter_field(name='site_group')
    )
    _site: Annotated['SiteFilterV1', strawberry.lazy('dcim.graphql.filters_v1')] | None = (
        strawberry_django.filter_field(name='site')
    )


@strawberry_django.filter_type(models.Circuit, lookups=True)
class CircuitFilterV1(
    ContactFilterMixinV1,
    ImageAttachmentFilterMixinV1,
    DistanceFilterMixinV1,
    TenancyFilterMixinV1,
    PrimaryModelFilterMixinV1
):
    cid: FilterLookup[str] | None = strawberry_django.filter_field()
    provider: Annotated['ProviderFilterV1', strawberry.lazy('circuits.graphql.filters_v1')] | None = (
        strawberry_django.filter_field()
    )
    provider_id: ID | None = strawberry_django.filter_field()
    provider_account: Annotated['ProviderAccountFilterV1', strawberry.lazy('circuits.graphql.filters_v1')] | None = (
        strawberry_django.filter_field()
    )
    provider_account_id: ID | None = strawberry_django.filter_field()
    type: Annotated['CircuitTypeFilterV1', strawberry.lazy('circuits.graphql.filters_v1')] | None = (
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
    terminations: Annotated['CircuitTerminationFilterV1', strawberry.lazy('circuits.graphql.filters_v1')] | None = (
        strawberry_django.filter_field()
    )


@strawberry_django.filter_type(models.CircuitType, lookups=True)
class CircuitTypeFilterV1(BaseCircuitTypeFilterMixinV1):
    pass


@strawberry_django.filter_type(models.CircuitGroup, lookups=True)
class CircuitGroupFilterV1(TenancyFilterMixinV1, OrganizationalModelFilterMixinV1):
    pass


@strawberry_django.filter_type(models.CircuitGroupAssignment, lookups=True)
class CircuitGroupAssignmentFilterV1(
    BaseObjectTypeFilterMixinV1, CustomFieldsFilterMixinV1, TagsFilterMixinV1, ChangeLogFilterMixinV1
):
    member_type: Annotated['ContentTypeFilterV1', strawberry.lazy('core.graphql.filters_v1')] | None = (
        strawberry_django.filter_field()
    )
    member_id: ID | None = strawberry_django.filter_field()
    group: Annotated['CircuitGroupFilterV1', strawberry.lazy('circuits.graphql.filters_v1')] | None = (
        strawberry_django.filter_field()
    )
    group_id: ID | None = strawberry_django.filter_field()
    priority: Annotated['CircuitPriorityEnum', strawberry.lazy('circuits.graphql.enums')] | None = (
        strawberry_django.filter_field()
    )


@strawberry_django.filter_type(models.Provider, lookups=True)
class ProviderFilterV1(ContactFilterMixinV1, PrimaryModelFilterMixinV1):
    name: FilterLookup[str] | None = strawberry_django.filter_field()
    slug: FilterLookup[str] | None = strawberry_django.filter_field()
    asns: Annotated['ASNFilterV1', strawberry.lazy('ipam.graphql.filters_v1')] | None = strawberry_django.filter_field()
    circuits: Annotated['CircuitFilterV1', strawberry.lazy('circuits.graphql.filters_v1')] | None = (
        strawberry_django.filter_field()
    )


@strawberry_django.filter_type(models.ProviderAccount, lookups=True)
class ProviderAccountFilterV1(ContactFilterMixinV1, PrimaryModelFilterMixinV1):
    provider: Annotated['ProviderFilterV1', strawberry.lazy('circuits.graphql.filters_v1')] | None = (
        strawberry_django.filter_field()
    )
    provider_id: ID | None = strawberry_django.filter_field()
    account: FilterLookup[str] | None = strawberry_django.filter_field()
    name: FilterLookup[str] | None = strawberry_django.filter_field()


@strawberry_django.filter_type(models.ProviderNetwork, lookups=True)
class ProviderNetworkFilterV1(PrimaryModelFilterMixinV1):
    name: FilterLookup[str] | None = strawberry_django.filter_field()
    provider: Annotated['ProviderFilterV1', strawberry.lazy('circuits.graphql.filters_v1')] | None = (
        strawberry_django.filter_field()
    )
    provider_id: ID | None = strawberry_django.filter_field()
    service_id: FilterLookup[str] | None = strawberry_django.filter_field()


@strawberry_django.filter_type(models.VirtualCircuitType, lookups=True)
class VirtualCircuitTypeFilterV1(BaseCircuitTypeFilterMixinV1):
    pass


@strawberry_django.filter_type(models.VirtualCircuit, lookups=True)
class VirtualCircuitFilterV1(TenancyFilterMixinV1, PrimaryModelFilterMixinV1):
    cid: FilterLookup[str] | None = strawberry_django.filter_field()
    provider_network: Annotated['ProviderNetworkFilterV1', strawberry.lazy('circuits.graphql.filters_v1')] | None = (
        strawberry_django.filter_field()
    )
    provider_network_id: ID | None = strawberry_django.filter_field()
    provider_account: Annotated['ProviderAccountFilterV1', strawberry.lazy('circuits.graphql.filters_v1')] | None = (
        strawberry_django.filter_field()
    )
    provider_account_id: ID | None = strawberry_django.filter_field()
    type: Annotated['VirtualCircuitTypeFilterV1', strawberry.lazy('circuits.graphql.filters_v1')] | None = (
        strawberry_django.filter_field()
    )
    type_id: ID | None = strawberry_django.filter_field()
    status: Annotated['CircuitStatusEnum', strawberry.lazy('circuits.graphql.enums')] | None = (
        strawberry_django.filter_field()
    )
    group_assignments: Annotated[
        'CircuitGroupAssignmentFilterV1', strawberry.lazy('circuits.graphql.filters_v1')
    ] | None = (
        strawberry_django.filter_field()
    )


@strawberry_django.filter_type(models.VirtualCircuitTermination, lookups=True)
class VirtualCircuitTerminationFilterV1(
    BaseObjectTypeFilterMixinV1, CustomFieldsFilterMixinV1, TagsFilterMixinV1, ChangeLogFilterMixinV1
):
    virtual_circuit: Annotated['VirtualCircuitFilterV1', strawberry.lazy('circuits.graphql.filters_v1')] | None = (
        strawberry_django.filter_field()
    )
    virtual_circuit_id: ID | None = strawberry_django.filter_field()
    role: Annotated['VirtualCircuitTerminationRoleEnum', strawberry.lazy('circuits.graphql.enums')] | None = (
        strawberry_django.filter_field()
    )
    interface: Annotated['InterfaceFilterV1', strawberry.lazy('dcim.graphql.filters_v1')] | None = (
        strawberry_django.filter_field()
    )
    interface_id: ID | None = strawberry_django.filter_field()
    description: FilterLookup[str] | None = strawberry_django.filter_field()
