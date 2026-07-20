from typing import Annotated

import strawberry
from django.contrib.contenttypes.models import ContentType as DjangoContentType

from core import models
from netbox.graphql.types import BaseObjectType, PrimaryObjectType, register_type

from .filters import *

__all__ = (
    'ContentType',
    'DataFileType',
    'DataSourceType',
    'ObjectChangeType',
)


@register_type(
    models.DataFile,
    exclude=['data',],
    filters=DataFileFilter,
    pagination=True
)
class DataFileType(BaseObjectType):
    source: Annotated["DataSourceType", strawberry.lazy('core.graphql.types')]


@register_type(
    models.DataSource,
    fields='__all__',
    filters=DataSourceFilter,
    pagination=True
)
class DataSourceType(PrimaryObjectType):
    datafiles: list[Annotated["DataFileType", strawberry.lazy('core.graphql.types')]]


@register_type(
    models.ObjectChange,
    fields='__all__',
    filters=ObjectChangeFilter,
    pagination=True
)
class ObjectChangeType(BaseObjectType):
    pass


@register_type(
    DjangoContentType,
    fields='__all__',
    pagination=True
)
class ContentType:
    pass
