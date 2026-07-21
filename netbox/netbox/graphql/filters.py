from dataclasses import dataclass
from typing import TYPE_CHECKING

import strawberry_django
from strawberry import ID
from strawberry_django import ComparisonFilterLookup, StrFilterLookup

from core.graphql.filter_mixins import ChangeLoggingMixin
from extras.graphql.filter_mixins import CustomFieldsFilterMixin, JournalEntriesFilterMixin, TagsFilterMixin
from netbox.graphql.utils import splice_extension_bases
from netbox.registry import registry

if TYPE_CHECKING:
    from .filters import *

__all__ = (
    'BaseModelFilter',
    'ChangeLoggedModelFilter',
    'NestedGroupModelFilter',
    'NetBoxModelFilter',
    'OrganizationalModelFilter',
    'PrimaryModelFilter',
    'register_filter',
)


def register_filter(model, **kwargs):
    """
    Drop-in replacement for `strawberry_django.filter_type()` for model-bound NetBox GraphQL filters. Before
    delegating to `strawberry_django.filter_type()`, any plugin-registered filter mixins for the given model are
    spliced into the decorated class's bases. With no extensions registered this is an exact pass-through, leaving
    schema output unchanged.

    Note: the extension registry is read here at decoration (import) time, so all plugins must have registered their
    extensions (via `PluginConfig.ready()`) before this module is imported. This holds because the GraphQL schema is
    assembled lazily from the URLconf, after every app's `ready()` has run. Importing a core `graphql/filters.py`
    during app initialization would read the registry too early and silently drop later-registered extensions.
    """
    label = f'{model._meta.app_label}.{model._meta.model_name}'

    def wrapper(cls):
        extensions = registry['plugins']['graphql_filter_extensions'].get(label)
        cls = splice_extension_bases(cls, extensions)
        return strawberry_django.filter_type(model, **kwargs)(cls)

    return wrapper


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
    name: StrFilterLookup | None = strawberry_django.filter_field()
    slug: StrFilterLookup | None = strawberry_django.filter_field()
    description: StrFilterLookup | None = strawberry_django.filter_field()
    parent_id: ID | None = strawberry_django.filter_field()


@dataclass
class OrganizationalModelFilter(NetBoxModelFilter):
    name: StrFilterLookup | None = strawberry_django.filter_field()
    slug: StrFilterLookup | None = strawberry_django.filter_field()
    description: StrFilterLookup | None = strawberry_django.filter_field()
    comments: StrFilterLookup | None = strawberry_django.filter_field()


@dataclass
class PrimaryModelFilter(NetBoxModelFilter):
    description: StrFilterLookup | None = strawberry_django.filter_field()
    comments: StrFilterLookup | None = strawberry_django.filter_field()
