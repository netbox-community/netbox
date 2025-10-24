from dataclasses import dataclass
from datetime import datetime
from typing import TypeVar, TYPE_CHECKING, Annotated

import strawberry
import strawberry_django
from strawberry import ID
from strawberry_django import FilterLookup, DatetimeFilterLookup

from core.graphql.filter_mixins_v1 import BaseFilterMixinV1, BaseObjectTypeFilterMixinV1, ChangeLogFilterMixinV1
from extras.graphql.filter_mixins_v1 import CustomFieldsFilterMixinV1, JournalEntriesFilterMixinV1, TagsFilterMixinV1

__all__ = (
    'DistanceFilterMixinV1',
    'ImageAttachmentFilterMixinV1',
    'NestedGroupModelFilterMixinV1',
    'NetBoxModelFilterMixinV1',
    'OrganizationalModelFilterMixinV1',
    'PrimaryModelFilterMixinV1',
    'SyncedDataFilterMixinV1',
    'WeightFilterMixinV1',
)

T = TypeVar('T')


if TYPE_CHECKING:
    from .enums import *
    from core.graphql.filters_v1 import *
    from extras.graphql.filters_v1 import *


class NetBoxModelFilterMixinV1(
    ChangeLogFilterMixinV1,
    CustomFieldsFilterMixinV1,
    JournalEntriesFilterMixinV1,
    TagsFilterMixinV1,
    BaseObjectTypeFilterMixinV1,
):
    pass


@dataclass
class NestedGroupModelFilterMixinV1(NetBoxModelFilterMixinV1):
    name: FilterLookup[str] | None = strawberry_django.filter_field()
    slug: FilterLookup[str] | None = strawberry_django.filter_field()
    description: FilterLookup[str] | None = strawberry_django.filter_field()
    parent_id: ID | None = strawberry_django.filter_field()


@dataclass
class OrganizationalModelFilterMixinV1(
    ChangeLogFilterMixinV1,
    CustomFieldsFilterMixinV1,
    TagsFilterMixinV1,
    BaseObjectTypeFilterMixinV1,
):
    name: FilterLookup[str] | None = strawberry_django.filter_field()
    slug: FilterLookup[str] | None = strawberry_django.filter_field()
    description: FilterLookup[str] | None = strawberry_django.filter_field()


@dataclass
class PrimaryModelFilterMixinV1(NetBoxModelFilterMixinV1):
    description: FilterLookup[str] | None = strawberry_django.filter_field()
    comments: FilterLookup[str] | None = strawberry_django.filter_field()


@dataclass
class ImageAttachmentFilterMixinV1(BaseFilterMixinV1):
    images: Annotated['ImageAttachmentFilterV1', strawberry.lazy('extras.graphql.filters_v1')] | None = (
        strawberry_django.filter_field()
    )


@dataclass
class WeightFilterMixinV1(BaseFilterMixinV1):
    weight: FilterLookup[float] | None = strawberry_django.filter_field()
    weight_unit: Annotated['WeightUnitEnum', strawberry.lazy('netbox.graphql.enums')] | None = (
        strawberry_django.filter_field()
    )


@dataclass
class SyncedDataFilterMixinV1(BaseFilterMixinV1):
    data_source: Annotated['DataSourceFilterV1', strawberry.lazy('core.graphql.filters_v1')] | None = (
        strawberry_django.filter_field()
    )
    data_source_id: FilterLookup[int] | None = strawberry_django.filter_field()
    data_file: Annotated['DataFileFilterV1', strawberry.lazy('core.graphql.filters_v1')] | None = (
        strawberry_django.filter_field()
    )
    data_file_id: FilterLookup[int] | None = strawberry_django.filter_field()
    data_path: FilterLookup[str] | None = strawberry_django.filter_field()
    auto_sync_enabled: FilterLookup[bool] | None = strawberry_django.filter_field()
    data_synced: DatetimeFilterLookup[datetime] | None = strawberry_django.filter_field()


@dataclass
class DistanceFilterMixinV1(BaseFilterMixinV1):
    distance: FilterLookup[float] | None = strawberry_django.filter_field()
    distance_unit: Annotated['DistanceUnitEnum', strawberry.lazy('netbox.graphql.enums')] | None = (
        strawberry_django.filter_field()
    )
