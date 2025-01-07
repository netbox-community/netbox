from datetime import date
from typing import Annotated, TYPE_CHECKING
import strawberry
from strawberry.scalars import ID
import strawberry_django
from strawberry_django import FilterLookup, DateFilterLookup
from extras.graphql.filter_mixins import *
from netbox.graphql.filter_mixins import *
from core.graphql.filter_mixins import *
from tenancy.graphql.filter_mixins import *
from dcim.graphql.filter_mixins import *
from .filter_mixins import *

from circuits import models

if TYPE_CHECKING:
    from .enums import *
    from netbox.graphql.enums import *
    from wireless.graphql.enums import *
    from core.graphql.filter_lookups import *
    from core.graphql.filters import *
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


@strawberry_django.filter(models.CircuitTermination, lookups=True)
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
    port_speed: Annotated['IntegerLookup', strawberry.lazy('core.graphql.filter_lookups')] | None = (
        strawberry_django.filter_field()
    )
    upstream_speed: Annotated['IntegerLookup', strawberry.lazy('core.graphql.filter_lookups')] | None = (
        strawberry_django.filter_field()
    )
    xconnect_id: FilterLookup[str] | None = strawberry_django.filter_field()
    pp_info: FilterLookup[str] | None = strawberry_django.filter_field()
    description: FilterLookup[str] | None = strawberry_django.filter_field()


@strawberry_django.filter(models.Circuit, lookups=True)
class CircuitFilter(ContactFilterMixin, ImageAttachmentFilterMixin, DistanceFilterMixin, PrimaryModelFilterMixin):
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
    tenant: Annotated['TenantFilter', strawberry.lazy('tenancy.graphql.filters')] | None = (
        strawberry_django.filter_field()
    )
    tenant_id: ID | None = strawberry_django.filter_field()
    install_date: DateFilterLookup[date] | None = strawberry_django.filter_field()
    termination_date: DateFilterLookup[date] | None = strawberry_django.filter_field()
    commit_rate: Annotated['IntegerLookup', strawberry.lazy('core.graphql.filter_lookups')] | None = (
        strawberry_django.filter_field()
    )


@strawberry_django.filter(models.CircuitType, lookups=True)
class CircuitTypeFilter(BaseCircuitTypeFilterMixin):
    pass


@strawberry_django.filter(models.CircuitGroup, lookups=True)
class CircuitGroupFilter(OrganizationalModelFilterMixin):
    tenant: Annotated['TenantFilter', strawberry.lazy('tenancy.graphql.filters')] | None = (
        strawberry_django.filter_field()
    )
    tenant_id: ID | None = strawberry_django.filter_field()


@strawberry_django.filter(models.CircuitGroupAssignment, lookups=True)
class CircuitGroupAssignmentFilter(
    BaseObjectTypeFilterMixin, CustomFieldsFilterMixin, TagsFilterMixin, ChangeLogFilterMixin
):
    member_type: Annotated['ContentTypeFilter', strawberry.lazy('core.graphql.filters')] | None = (
        strawberry_django.filter_field()
    )
    member_type_id: ID | None = strawberry_django.filter_field()
    group: Annotated['CircuitGroupFilter', strawberry.lazy('circuits.graphql.filters')] | None = (
        strawberry_django.filter_field()
    )
    group_id: ID | None = strawberry_django.filter_field()
    priority: Annotated['CircuitPriorityEnum', strawberry.lazy('circuits.graphql.enums')] | None = (
        strawberry_django.filter_field()
    )


@strawberry_django.filter(models.Provider, lookups=True)
class ProviderFilter(ContactFilterMixin, PrimaryModelFilterMixin):
    name: FilterLookup[str] | None = strawberry_django.filter_field()
    slug: FilterLookup[str] | None = strawberry_django.filter_field()
    asns: Annotated['ASNFilter', strawberry.lazy('ipam.graphql.filters')] | None = strawberry_django.filter_field()


@strawberry_django.filter(models.ProviderAccount, lookups=True)
class ProviderAccountFilter(ContactFilterMixin, PrimaryModelFilterMixin):
    provider: Annotated['ProviderFilter', strawberry.lazy('circuits.graphql.filters')] | None = (
        strawberry_django.filter_field()
    )
    provider_id: ID | None = strawberry_django.filter_field()
    account: FilterLookup[str] | None = strawberry_django.filter_field()
    name: FilterLookup[str] | None = strawberry_django.filter_field()


@strawberry_django.filter(models.ProviderNetwork, lookups=True)
class ProviderNetworkFilter(PrimaryModelFilterMixin):
    name: FilterLookup[str] | None = strawberry_django.filter_field()
    provider: Annotated['ProviderFilter', strawberry.lazy('circuits.graphql.filters')] | None = (
        strawberry_django.filter_field()
    )
    provider_id: ID | None = strawberry_django.filter_field()
    service_id: FilterLookup[str] | None = strawberry_django.filter_field()


@strawberry_django.filter(models.VirtualCircuitType, lookups=True)
class VirtualCircuitTypeFilter(BaseCircuitTypeFilterMixin):
    pass


@strawberry_django.filter(models.VirtualCircuit, lookups=True)
class VirtualCircuitFilter(PrimaryModelFilterMixin):
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
    tenant: Annotated['TenantFilter', strawberry.lazy('tenancy.graphql.filters')] | None = (
        strawberry_django.filter_field()
    )
    tenant_id: ID | None = strawberry_django.filter_field()
    group_assignments: Annotated['CircuitGroupAssignmentFilter', strawberry.lazy('circuits.graphql.filters')] | None = (
        strawberry_django.filter_field()
    )


@strawberry_django.filter(models.VirtualCircuitTermination, lookups=True)
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
