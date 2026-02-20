from dataclasses import dataclass
from typing import TYPE_CHECKING, Annotated

import strawberry
import strawberry_django

if TYPE_CHECKING:
    from netbox.graphql.filter_lookups import JSONFilter

    from .filters import *

__all__ = (
    'ConfigContextFilterMixin',
    'CustomFieldsFilterMixin',
    'JournalEntriesFilterMixin',
    'TagsFilterMixin',
)


@dataclass
class CustomFieldsFilterMixin:
    custom_field_data: Annotated['JSONFilter', strawberry.lazy('netbox.graphql.filter_lookups')] | None = (
        strawberry_django.filter_field()
    )


@dataclass
class JournalEntriesFilterMixin:
    journal_entries: Annotated['JournalEntryFilter', strawberry.lazy('extras.graphql.filters')] | None = (
        strawberry_django.filter_field()
    )


@dataclass
class TagsFilterMixin:
    tags: Annotated['TagFilter', strawberry.lazy('extras.graphql.filters')] | None = strawberry_django.filter_field()


@dataclass
class ConfigContextFilterMixin:
    local_context_data: Annotated['JSONFilter', strawberry.lazy('netbox.graphql.filter_lookups')] | None = (
        strawberry_django.filter_field()
    )
