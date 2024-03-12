from typing import List
import strawberry
import strawberry_django
from strawberry import auto


@strawberry.input
class BaseFilterMixin:
    id: auto

    def filter_by_filterset(self, queryset, key):
        return self.filterset(data={key: getattr(self, key)}, queryset=queryset).qs


@strawberry.input
class ChangeLoggedModelFilterMixin(BaseFilterMixin):
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
class NetBoxModelFilterMixin(ChangeLoggedModelFilterMixin):
    q: str | None
    tag: List[str] | None

    def filter_q(self, queryset):
        # return self.search(queryset, None, self.q)
        return self.filter_by_filterset(queryset, 'q')

    def filter_tag(self, queryset, info):
        # return self.filterset(data={'tag': self.tag}, queryset=queryset).qs
        # return self.filterset(data={'tag': getattr(self, 'tag')}, queryset=queryset).qs
        return self.filter_by_filterset(queryset, 'tag')
