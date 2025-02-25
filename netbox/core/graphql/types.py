from typing import Annotated, List

import strawberry
import strawberry_django
from django.contrib.contenttypes.models import ContentType as DjangoContentType
from core import models
from netbox.graphql.types import BaseObjectType, NetBoxObjectType
from .filters import *

__all__ = (
    'DataFileType',
    'DataSourceType',
    'ObjectChangeType',
    'ContentType',
)


@strawberry_django.type(
    models.DataFile,
    exclude=['data',],
    filters=DataFileFilter
)
class DataFileType(BaseObjectType):
    source: Annotated["DataSourceType", strawberry.lazy('core.graphql.types')]


@strawberry_django.type(
    models.DataSource,
    fields='__all__',
    filters=DataSourceFilter
)
class DataSourceType(NetBoxObjectType):

    datafiles: List[Annotated["DataFileType", strawberry.lazy('core.graphql.types')]]


@strawberry_django.type(
    models.ObjectChange,
    fields='__all__',
    filters=ObjectChangeFilter
)
class ObjectChangeType(BaseObjectType):
    pass


@strawberry_django.type(DjangoContentType, fields='__all__')
class ContentType:
    pass
