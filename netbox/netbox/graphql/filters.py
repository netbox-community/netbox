from dataclasses import dataclass
from datetime import datetime
from typing import Annotated, TYPE_CHECKING

import strawberry
import strawberry_django
from strawberry import ID
from strawberry_django import FilterLookup, DatetimeFilterLookup

from extras.graphql.filter_mixins import CustomFieldsFilterMixin, JournalEntriesFilterMixin, TagsFilterMixin

if TYPE_CHECKING:
    from .filters import *

__all__ = (
    'BaseModelFilter',
    'ChangeLoggedModelFilter',
    'NestedGroupModelFilter',
    'NetBoxModelFilter',
    'OrganizationalModelFilter',
    'PrimaryModelFilter',
)


class BaseModelFilter:
    id: FilterLookup[ID] | None = strawberry_django.filter_field()


@dataclass
class ChangeLoggedModelFilter(BaseModelFilter):
    # TODO: "changelog" is not a valid field name; needs to be updated for ObjectChange
    changelog: Annotated['ObjectChangeFilter', strawberry.lazy('core.graphql.filters')] | None = (
        strawberry_django.filter_field()
    )
    created: DatetimeFilterLookup[datetime] | None = strawberry_django.filter_field()
    last_updated: DatetimeFilterLookup[datetime] | None = strawberry_django.filter_field()


class NetBoxModelFilter(
    CustomFieldsFilterMixin,
    JournalEntriesFilterMixin,
    TagsFilterMixin,
    ChangeLoggedModelFilter,
):
    pass


@dataclass
class NestedGroupModelFilter(NetBoxModelFilter):
    name: FilterLookup[str] | None = strawberry_django.filter_field()
    slug: FilterLookup[str] | None = strawberry_django.filter_field()
    description: FilterLookup[str] | None = strawberry_django.filter_field()
    parent_id: ID | None = strawberry_django.filter_field()


@dataclass
class OrganizationalModelFilter(NetBoxModelFilter):
    name: FilterLookup[str] | None = strawberry_django.filter_field()
    slug: FilterLookup[str] | None = strawberry_django.filter_field()
    description: FilterLookup[str] | None = strawberry_django.filter_field()


@dataclass
class PrimaryModelFilter(NetBoxModelFilter):
    description: FilterLookup[str] | None = strawberry_django.filter_field()
    comments: FilterLookup[str] | None = strawberry_django.filter_field()
