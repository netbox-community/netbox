from dataclasses import dataclass
from typing import TypeVar, TYPE_CHECKING, Annotated


from datetime import datetime
import strawberry
from strawberry import ID
import strawberry_django
from strawberry_django import FilterLookup, DatetimeFilterLookup

from extras.models import *
from utilities.filters import *
from core.graphql.filter_lookups import *
from core.graphql.filter_mixins import *
from extras.graphql.filter_mixins import *

__all__ = [
    'NetBoxModelFilterMixin',
    'OrganizationalModelFilterMixin',
    'PrimaryModelFilterMixin',
    # 'autotype_decorator',
    'NestedGroupModelFilterMixin',
    'ImageAttachmentFilterMixin',
    'WeightFilterMixin',
    'SyncedDataFilterMixin',
    'DistanceFilterMixin',
]

T = TypeVar('T')


if TYPE_CHECKING:
    from .enums import *
    from core.graphql.filters import *
    from tenancy.graphql.filters import *
    from extras.graphql.filters import *


class NetBoxModelFilterMixin(
    ChangeLogFilterMixin,
    CustomFieldsFilterMixin,
    JournalEntriesFilterMixin,
    TagsFilterMixin,
    BaseObjectTypeFilterMixin,
):
    pass


@dataclass
class NestedGroupModelFilterMixin(NetBoxModelFilterMixin):
    name: FilterLookup[str] | None = strawberry_django.filter_field()
    slug: FilterLookup[str] | None = strawberry_django.filter_field()
    description: FilterLookup[str] | None = strawberry_django.filter_field()
    lft: IntegerLookup | None = strawberry_django.filter_field()
    rght: IntegerLookup | None = strawberry_django.filter_field()
    tree_id: IntegerLookup | None = strawberry_django.filter_field()
    level: IntegerLookup | None = strawberry_django.filter_field()
    parent_id: ID | None = strawberry_django.filter_field()


@dataclass
class OrganizationalModelFilterMixin(
    ChangeLogFilterMixin,
    CustomFieldsFilterMixin,
    TagsFilterMixin,
    BaseObjectTypeFilterMixin,
):
    name: FilterLookup[str] | None = strawberry_django.filter_field()
    slug: FilterLookup[str] | None = strawberry_django.filter_field()
    description: FilterLookup[str] | None = strawberry_django.filter_field()


@dataclass
class PrimaryModelFilterMixin(NetBoxModelFilterMixin):
    description: FilterLookup[str] | None = strawberry_django.filter_field()
    comments: FilterLookup[str] | None = strawberry_django.filter_field()


@dataclass
class ImageAttachmentFilterMixin(BaseFilterMixin):
    images: Annotated['ImageAttachmentFilter', strawberry.lazy('extras.graphql.filters')] | None = (
        strawberry_django.filter_field()
    )


@dataclass
class WeightFilterMixin(BaseFilterMixin):
    weight: FilterLookup[float] | None = strawberry_django.filter_field()
    weight_unit: Annotated['WeightUnitEnum', strawberry.lazy('netbox.graphql.enums')] | None = (
        strawberry_django.filter_field()
    )


@dataclass
class SyncedDataFilterMixin(BaseFilterMixin):
    data_source: Annotated['DataSourceFilter', strawberry.lazy('core.graphql.filters')] | None = (
        strawberry_django.filter_field()
    )
    data_source_id: FilterLookup[int] | None = strawberry_django.filter_field()
    data_file: Annotated['DataFileFilter', strawberry.lazy('core.graphql.filters')] | None = (
        strawberry_django.filter_field()
    )
    data_file_id: FilterLookup[int] | None = strawberry_django.filter_field()
    data_path: FilterLookup[str] | None = strawberry_django.filter_field()
    auto_sync_enabled: FilterLookup[bool] | None = strawberry_django.filter_field()
    data_synced: DatetimeFilterLookup[datetime] | None = strawberry_django.filter_field()


@dataclass
class DistanceFilterMixin(BaseFilterMixin):
    distance: FilterLookup[float] | None = strawberry_django.filter_field()
    distance_unit: Annotated['DistanceUnitEnum', strawberry.lazy('netbox.graphql.enums')] | None = (
        strawberry_django.filter_field()
    )
