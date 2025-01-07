from dataclasses import dataclass
from typing import Annotated, TYPE_CHECKING
import strawberry
import strawberry_django
from strawberry_django import FilterLookup
from core.graphql.filter_mixins import BaseFilterMixin

if TYPE_CHECKING:
    from core.graphql.filter_lookups import *
    from .filters import *

__all__ = [
    'CustomFieldsFilterMixin',
    'JournalEntriesFilterMixin',
    'TagsFilterMixin',
    'ConfigContextFilterMixin',
    'TagBaseFilterMixin',
]


@dataclass
class CustomFieldsFilterMixin(BaseFilterMixin):
    custom_field_data: Annotated['JSONFilter', strawberry.lazy('core.graphql.filter_lookups')] | None = (
        strawberry_django.filter_field()
    )


@dataclass
class JournalEntriesFilterMixin(BaseFilterMixin):
    journal_entries: Annotated['JournalEntryFilter', strawberry.lazy('extras.graphql.filters')] | None = (
        strawberry_django.filter_field()
    )


@dataclass
class TagsFilterMixin(BaseFilterMixin):
    tags: Annotated['TagFilter', strawberry.lazy('extras.graphql.filters')] | None = strawberry_django.filter_field()


@dataclass
class ConfigContextFilterMixin(BaseFilterMixin):
    local_config_context: Annotated['ConfigContextFilter', strawberry.lazy('extras.graphql.filters')] | None = (
        strawberry_django.filter_field()
    )
    config_context: Annotated['ConfigContextFilter', strawberry.lazy('extras.graphql.filters')] | None = (
        strawberry_django.filter_field()
    )


@dataclass
class TagBaseFilterMixin(BaseFilterMixin):
    name: FilterLookup[str] | None = strawberry_django.filter_field()
    slug: FilterLookup[str] | None = strawberry_django.filter_field()
