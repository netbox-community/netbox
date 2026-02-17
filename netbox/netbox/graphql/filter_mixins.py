from dataclasses import dataclass
from datetime import datetime
from typing import TYPE_CHECKING, Annotated, TypeVar

import strawberry
import strawberry_django
from strawberry_django import BaseFilterLookup, DatetimeFilterLookup, FilterLookup

__all__ = (
    'DistanceFilterMixin',
    'ImageAttachmentFilterMixin',
    'SyncedDataFilterMixin',
    'WeightFilterMixin',
)

T = TypeVar('T')


if TYPE_CHECKING:
    from core.graphql.filters import *
    from extras.graphql.filters import *

    from .enums import *


@dataclass
class ImageAttachmentFilterMixin:
    images: Annotated['ImageAttachmentFilter', strawberry.lazy('extras.graphql.filters')] | None = (
        strawberry_django.filter_field()
    )


@dataclass
class WeightFilterMixin:
    weight: FilterLookup[float] | None = strawberry_django.filter_field()
    weight_unit: BaseFilterLookup[Annotated['WeightUnitEnum', strawberry.lazy('netbox.graphql.enums')]] | None = (
        strawberry_django.filter_field()
    )


@dataclass
class SyncedDataFilterMixin:
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
class DistanceFilterMixin:
    distance: FilterLookup[float] | None = strawberry_django.filter_field()
    distance_unit: BaseFilterLookup[Annotated['DistanceUnitEnum', strawberry.lazy('netbox.graphql.enums')]] | None = (
        strawberry_django.filter_field()
    )
