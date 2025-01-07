from dataclasses import dataclass
from typing import Annotated, TYPE_CHECKING
import strawberry
from strawberry import ID
import strawberry_django
from core.graphql.filter_mixins import BaseFilterMixin

if TYPE_CHECKING:
    from .filters import *
    from core.graphql.filter_lookups import *

__all__ = ['TenancyFilterMixin', 'ContactFilterMixin']


@dataclass
class ContactFilterMixin(BaseFilterMixin):
    contacts: Annotated['ContactFilter', strawberry.lazy('tenancy.graphql.filters')] | None = (
        strawberry_django.filter_field()
    )


@dataclass
class TenancyFilterMixin(BaseFilterMixin):
    tenant: Annotated['TenantFilter', strawberry.lazy('tenancy.graphql.filters')] | None = (
        strawberry_django.filter_field()
    )
    tenant_id: ID | None = strawberry_django.filter_field()
    group: Annotated['TenantGroupFilter', strawberry.lazy('tenancy.graphql.filters')] | None = (
        strawberry_django.filter_field()
    )
    group_id: Annotated['TreeNodeFilter', strawberry.lazy('core.graphql.filter_lookups')] | None = (
        strawberry_django.filter_field()
    )
