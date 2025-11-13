from dataclasses import dataclass
from typing import Annotated, TYPE_CHECKING

import strawberry
import strawberry_django
from strawberry_django import FilterLookup

from core.graphql.filter_mixins_v1 import BaseFilterMixinV1

if TYPE_CHECKING:
    from netbox.graphql.filter_lookups import JSONFilter
    from .filters_v1 import *

__all__ = (
    'CustomFieldsFilterMixinV1',
    'JournalEntriesFilterMixinV1',
    'TagsFilterMixinV1',
    'ConfigContextFilterMixinV1',
    'TagBaseFilterMixinV1',
)


@dataclass
class CustomFieldsFilterMixinV1(BaseFilterMixinV1):
    custom_field_data: Annotated['JSONFilter', strawberry.lazy('netbox.graphql.filter_lookups')] | None = (
        strawberry_django.filter_field()
    )


@dataclass
class JournalEntriesFilterMixinV1(BaseFilterMixinV1):
    journal_entries: Annotated['JournalEntryFilterV1', strawberry.lazy('extras.graphql.filters_v1')] | None = (
        strawberry_django.filter_field()
    )


@dataclass
class TagsFilterMixinV1(BaseFilterMixinV1):
    tags: Annotated['TagFilter', strawberry.lazy('extras.graphql.filters')] | None = strawberry_django.filter_field()


@dataclass
class ConfigContextFilterMixinV1(BaseFilterMixinV1):
    local_context_data: Annotated['JSONFilter', strawberry.lazy('netbox.graphql.filter_lookups')] | None = (
        strawberry_django.filter_field()
    )


@dataclass
class TagBaseFilterMixinV1(BaseFilterMixinV1):
    name: FilterLookup[str] | None = strawberry_django.filter_field()
    slug: FilterLookup[str] | None = strawberry_django.filter_field()
