from dataclasses import dataclass
from typing import Annotated, TYPE_CHECKING

from django.db.models import Q
import strawberry
import strawberry_django
from strawberry import ID

from core.graphql.filter_mixins import BaseFilterMixin

if TYPE_CHECKING:
    from netbox.graphql.filter_lookups import TreeNodeFilter
    from .filters import ContactFilter, TenantFilter, TenantGroupFilter

__all__ = (
    'ContactFilterMixin',
    'TenancyFilterMixin',
)


@strawberry.type
class ContactFilterMixin(BaseFilterMixin):
    @strawberry_django.filter_field
    def contacts(
        self,
        queryset,
        value: Annotated['ContactFilter', strawberry.lazy('tenancy.graphql.filters')],
        prefix: str,
    ):
        return strawberry_django.process_filters(
            filters=value,
            queryset=queryset,
            info=None,
            prefix=f"{prefix}contacts__contact__"
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
