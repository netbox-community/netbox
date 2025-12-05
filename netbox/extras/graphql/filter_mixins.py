from dataclasses import dataclass
from typing import Annotated, TYPE_CHECKING

import strawberry
import strawberry_django
from strawberry_django import FilterLookup

from core.graphql.filter_mixins import BaseFilter

if TYPE_CHECKING:
    from netbox.graphql.filter_lookups import JSONFilter
    from .filters import *

__all__ = (
    'CustomFieldsFilterMixin',
    'JournalEntriesFilterMixin',
    'TagsFilterMixin',
    'ConfigContextFilterMixin',
    'TagBaseFilter',
)


@dataclass
class CustomFieldsFilterMixin(BaseFilter):
    custom_field_data: Annotated['JSONFilter', strawberry.lazy('netbox.graphql.filter_lookups')] | None = (
        strawberry_django.filter_field()
    )


@dataclass
class JournalEntriesFilterMixin(BaseFilter):
    journal_entries: Annotated['JournalEntryFilter', strawberry.lazy('extras.graphql.filters')] | None = (
        strawberry_django.filter_field()
    )


@dataclass
class TagsFilterMixin(BaseFilter):
    tags: Annotated['TagFilter', strawberry.lazy('extras.graphql.filters')] | None = strawberry_django.filter_field()


@dataclass
class ConfigContextFilterMixin(BaseFilter):
    local_context_data: Annotated['JSONFilter', strawberry.lazy('netbox.graphql.filter_lookups')] | None = (
        strawberry_django.filter_field()
    )


@dataclass
class TagBaseFilter(BaseFilter):
    name: FilterLookup[str] | None = strawberry_django.filter_field()
    slug: FilterLookup[str] | None = strawberry_django.filter_field()
