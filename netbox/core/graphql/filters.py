from datetime import datetime
from typing import Annotated, TYPE_CHECKING
import strawberry
from strawberry.scalars import ID
import strawberry_django
from strawberry_django import (
    DatetimeFilterLookup,
    FilterLookup,
)
from django.contrib.contenttypes.models import ContentType as DjangoContentType
from core.graphql.filter_mixins import BaseFilterMixin
from core.graphql.filter_lookups import JSONFilter
from netbox.graphql.filter_mixins import (
    PrimaryModelFilterMixin,
)

from core import models

if TYPE_CHECKING:
    from core.graphql.filter_lookups import *
    from users.graphql.filters import *


__all__ = (
    'DataFileFilter',
    'DataSourceFilter',
    'ObjectChangeFilter',
    'ContentTypeFilter',
)


@strawberry_django.filter(models.DataFile, lookups=True)
class DataFileFilter(BaseFilterMixin):
    id: ID | None = strawberry_django.filter_field()
    created: DatetimeFilterLookup[datetime] | None = strawberry_django.filter_field()
    last_updated: DatetimeFilterLookup[datetime] | None = strawberry_django.filter_field()
    source: Annotated['DataSourceFilter', strawberry.lazy('core.graphql.filters')] | None = (
        strawberry_django.filter_field()
    )
    source_id: ID | None = strawberry_django.filter_field()
    path: FilterLookup[str] | None = strawberry_django.filter_field()
    size: Annotated['IntegerLookup', strawberry.lazy('core.graphql.filter_lookups')] | None = (
        strawberry_django.filter_field()
    )
    hash: FilterLookup[str] | None = strawberry_django.filter_field()


@strawberry_django.filter(models.DataSource, lookups=True)
class DataSourceFilter(PrimaryModelFilterMixin):
    name: FilterLookup[str] | None = strawberry_django.filter_field()
    type: FilterLookup[str] | None = strawberry_django.filter_field()
    source_url: FilterLookup[str] | None = strawberry_django.filter_field()
    status: FilterLookup[str] | None = strawberry_django.filter_field()
    enabled: FilterLookup[bool] | None = strawberry_django.filter_field()
    ignore_rules: FilterLookup[str] | None = strawberry_django.filter_field()
    parameters: Annotated['JSONFilter', strawberry.lazy('core.graphql.filter_lookups')] | None = (
        strawberry_django.filter_field()
    )
    last_synced: DatetimeFilterLookup[datetime] | None = strawberry_django.filter_field()
    datafiles: Annotated['DataFileFilter', strawberry.lazy('core.graphql.filters')] | None = (
        strawberry_django.filter_field()
    )


@strawberry_django.filter(models.ObjectChange, lookups=True)
class ObjectChangeFilter(BaseFilterMixin):
    id: ID | None = strawberry_django.filter_field()
    time: DatetimeFilterLookup[datetime] | None = strawberry_django.filter_field()
    user: Annotated['UserFilter', strawberry.lazy('users.graphql.filters')] | None = strawberry_django.filter_field()
    user_name: FilterLookup[str] | None = strawberry_django.filter_field()
    request_id: FilterLookup[str] | None = strawberry_django.filter_field()
    action: FilterLookup[str] | None = strawberry_django.filter_field()
    changed_object_type: Annotated['ContentTypeFilter', strawberry.lazy('core.graphql.filters')] | None = (
        strawberry_django.filter_field()
    )
    changed_object_type_id: ID | None = strawberry_django.filter_field()
    changed_object_id: ID | None = strawberry_django.filter_field()
    related_object_type_id: ID | None = strawberry_django.filter_field()
    related_object_id: ID | None = strawberry_django.filter_field()
    object_repr: FilterLookup[str] | None = strawberry_django.filter_field()
    prechange_data: Annotated['JSONFilter', strawberry.lazy('core.graphql.filter_lookups')] | None = (
        strawberry_django.filter_field()
    )
    postchange_data: Annotated['JSONFilter', strawberry.lazy('core.graphql.filter_lookups')] | None = (
        strawberry_django.filter_field()
    )


@strawberry_django.filter(DjangoContentType, lookups=True)
class ContentTypeFilter(BaseFilterMixin):
    id: ID | None = strawberry_django.filter_field()
    app_label: FilterLookup[str] | None = strawberry_django.filter_field()
    model: FilterLookup[str] | None = strawberry_django.filter_field()
