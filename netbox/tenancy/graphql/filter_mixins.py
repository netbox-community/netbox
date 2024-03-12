from typing import List
import strawberry
import strawberry_django
from strawberry import auto
from netbox.graphql.filter_mixins import BaseFilterMixin

__all__ = (
    'ContactModelFilterMixin',
    'TenancyFilterMixin',
)


@strawberry.input
class TenancyFilterMixin(BaseFilterMixin):
    created: auto
    last_updated: auto
    created_by_request: str | None
    updated_by_request: str | None
    modified_by_request: str | None

    def filter_created_by_request(self, queryset):
        return self.filter_by_filterset(queryset, 'created_by_request')

    def filter_updated_by_request(self, queryset):
        return self.filter_by_filterset(queryset, 'updated_by_request')

    def filter_modified_by_request(self, queryset):
        return self.filter_by_filterset(queryset, 'modified_by_request')


@strawberry.input
class ContactModelFilterMixin(BaseFilterMixin):
    tenant_group_id: List[str] | None
    tenant_group: List[str] | None
    tenant_id: List[str] | None
    tenant: List[str] | None

    def filter_tenant_group_id(self, queryset):
        return self.filter_by_filterset(queryset, 'tenant_group_id')

    def filter_tenant_group(self, queryset):
        return self.filter_by_filterset(queryset, 'tenant_group')

    def filter_tenant_id(self, queryset):
        return self.filter_by_filterset(queryset, 'tenant_id')

    def filter_tenant(self, queryset):
        return self.filter_by_filterset(queryset, 'tenant')
