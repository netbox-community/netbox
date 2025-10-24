from dataclasses import dataclass
from typing import Annotated, TYPE_CHECKING

import strawberry
import strawberry_django
from strawberry import ID

from core.graphql.filter_mixins_v1 import BaseFilterMixinV1

if TYPE_CHECKING:
    from netbox.graphql.filter_lookups import TreeNodeFilter
    from .filters_v1 import ContactAssignmentFilterV1, TenantFilterV1, TenantGroupFilterV1

__all__ = (
    'ContactFilterMixinV1',
    'TenancyFilterMixinV1',
)


@dataclass
class ContactFilterMixinV1(BaseFilterMixinV1):
    contacts: Annotated['ContactAssignmentFilterV1', strawberry.lazy('tenancy.graphql.filters_v1')] | None = (
        strawberry_django.filter_field()
    )


@dataclass
class TenancyFilterMixinV1(BaseFilterMixinV1):
    tenant: Annotated['TenantFilterV1', strawberry.lazy('tenancy.graphql.filters_v1')] | None = (
        strawberry_django.filter_field()
    )
    tenant_id: ID | None = strawberry_django.filter_field()
    tenant_group: Annotated['TenantGroupFilterV1', strawberry.lazy('tenancy.graphql.filters_v1')] | None = (
        strawberry_django.filter_field()
    )
    tenant_group_id: Annotated['TreeNodeFilter', strawberry.lazy('netbox.graphql.filter_lookups')] | None = (
        strawberry_django.filter_field()
    )
