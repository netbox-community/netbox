from typing import TYPE_CHECKING, Annotated

import strawberry
import strawberry_django
from django.contrib.contenttypes.models import ContentType as DjangoContentType
from strawberry.scalars import ID
from strawberry_django import BaseFilterLookup, DatetimeFilterLookup, FilterLookup, StrFilterLookup

from core import models
from netbox.graphql.filters import BaseModelFilter, PrimaryModelFilter, register_filter

from .enums import *

if TYPE_CHECKING:
    from netbox.graphql.filter_lookups import IntegerLookup, JSONFilter
    from users.graphql.filters import UserFilter

__all__ = (
    'ContentTypeFilter',
    'DataFileFilter',
    'DataSourceFilter',
    'ObjectChangeFilter',
)


@register_filter(models.DataFile, lookups=True)
class DataFileFilter(BaseModelFilter):
    created: DatetimeFilterLookup | None = strawberry_django.filter_field()
    last_updated: DatetimeFilterLookup | None = strawberry_django.filter_field()
    source: Annotated['DataSourceFilter', strawberry.lazy('core.graphql.filters')] | None = (
        strawberry_django.filter_field()
    )
    source_id: ID | None = strawberry_django.filter_field()
    path: StrFilterLookup | None = strawberry_django.filter_field()
    size: Annotated['IntegerLookup', strawberry.lazy('netbox.graphql.filter_lookups')] | None = (
        strawberry_django.filter_field()
    )
    hash: StrFilterLookup | None = strawberry_django.filter_field()


@register_filter(models.DataSource, lookups=True)
class DataSourceFilter(PrimaryModelFilter):
    name: StrFilterLookup | None = strawberry_django.filter_field()
    type: StrFilterLookup | None = strawberry_django.filter_field()
    source_url: StrFilterLookup | None = strawberry_django.filter_field()
    status: (
        BaseFilterLookup[Annotated['DataSourceStatusEnum', strawberry.lazy('core.graphql.enums')]] | None
    ) = strawberry_django.filter_field()
    enabled: FilterLookup[bool] | None = strawberry_django.filter_field()
    ignore_rules: StrFilterLookup | None = strawberry_django.filter_field()
    parameters: Annotated['JSONFilter', strawberry.lazy('netbox.graphql.filter_lookups')] | None = (
        strawberry_django.filter_field()
    )
    last_synced: DatetimeFilterLookup | None = strawberry_django.filter_field()
    datafiles: Annotated['DataFileFilter', strawberry.lazy('core.graphql.filters')] | None = (
        strawberry_django.filter_field()
    )


@register_filter(models.ObjectChange, lookups=True)
class ObjectChangeFilter(BaseModelFilter):
    time: DatetimeFilterLookup | None = strawberry_django.filter_field()
    user: Annotated['UserFilter', strawberry.lazy('users.graphql.filters')] | None = strawberry_django.filter_field()
    user_name: StrFilterLookup | None = strawberry_django.filter_field()
    request_id: StrFilterLookup | None = strawberry_django.filter_field()
    action: (
        BaseFilterLookup[Annotated['ObjectChangeActionEnum', strawberry.lazy('core.graphql.enums')]] | None
    ) = strawberry_django.filter_field()
    changed_object_type: Annotated['ContentTypeFilter', strawberry.lazy('core.graphql.filters')] | None = (
        strawberry_django.filter_field()
    )
    changed_object_type_id: ID | None = strawberry_django.filter_field()
    changed_object_id: ID | None = strawberry_django.filter_field()
    related_object_type: Annotated['ContentTypeFilter', strawberry.lazy('core.graphql.filters')] | None = (
        strawberry_django.filter_field()
    )
    related_object_id: ID | None = strawberry_django.filter_field()
    object_repr: StrFilterLookup | None = strawberry_django.filter_field()
    prechange_data: Annotated['JSONFilter', strawberry.lazy('netbox.graphql.filter_lookups')] | None = (
        strawberry_django.filter_field()
    )
    postchange_data: Annotated['JSONFilter', strawberry.lazy('netbox.graphql.filter_lookups')] | None = (
        strawberry_django.filter_field()
    )


@register_filter(DjangoContentType, lookups=True)
class ContentTypeFilter(BaseModelFilter):
    app_label: StrFilterLookup | None = strawberry_django.filter_field()
    model: StrFilterLookup | None = strawberry_django.filter_field()
