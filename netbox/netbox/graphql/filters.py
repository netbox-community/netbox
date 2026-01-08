from dataclasses import dataclass
from typing import TYPE_CHECKING

import strawberry_django
from strawberry import ID
from strawberry_django import ComparisonFilterLookup, FilterLookup

from core.graphql.filter_mixins import ChangeLoggingMixin
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


@dataclass
class BaseModelFilter:
    id: ComparisonFilterLookup[ID] | None = strawberry_django.filter_field()


class ChangeLoggedModelFilter(ChangeLoggingMixin, BaseModelFilter):
    pass


class NetBoxModelFilter(
    CustomFieldsFilterMixin,
    JournalEntriesFilterMixin,
    TagsFilterMixin,
    ChangeLoggingMixin,
    BaseModelFilter
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
    comments: FilterLookup[str] | None = strawberry_django.filter_field()


@dataclass
class PrimaryModelFilter(NetBoxModelFilter):
    description: FilterLookup[str] | None = strawberry_django.filter_field()
    comments: FilterLookup[str] | None = strawberry_django.filter_field()
