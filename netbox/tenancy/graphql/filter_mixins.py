from dataclasses import dataclass
from typing import Annotated, TYPE_CHECKING

import strawberry
import strawberry_django
from strawberry import ID

from core.graphql.filter_mixins import BaseFilterMixin

if TYPE_CHECKING:
    from netbox.graphql.filter_lookups import TreeNodeFilter
    from .filters import ContactAssignmentFilter, TenantFilter, TenantGroupFilter

__all__ = (
    'ContactFilterMixin',
    'TenancyFilterMixin',
)


@dataclass
class ContactFilterMixin(BaseFilterMixin):
    contacts: Annotated['ContactAssignmentFilter', strawberry.lazy('tenancy.graphql.filters')] | None = (
        strawberry_django.filter_field()
    )


@dataclass
class TenancyFilterMixin(BaseFilterMixin):
    tenant: Annotated['TenantFilter', strawberry.lazy('tenancy.graphql.filters')] | None = (
        strawberry_django.filter_field()
    )
    tenant_id: ID | None = strawberry_django.filter_field()
    tenant_group: Annotated['TenantGroupFilter', strawberry.lazy('tenancy.graphql.filters')] | None = (
        strawberry_django.filter_field()
    )
    tenant_group_id: Annotated['TreeNodeFilter', strawberry.lazy('netbox.graphql.filter_lookups')] | None = (
        strawberry_django.filter_field()
    )
