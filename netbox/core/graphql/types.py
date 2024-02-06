import strawberry
import strawberry_django

from core import models
from netbox.graphql.types import BaseObjectType, NetBoxObjectType
from .filters import *

__all__ = (
    'DataFileType',
    'DataSourceType',
)


@strawberry_django.type(
    models.DataFile,
    fields='__all__',
    filters=DataFileFilter
)
class DataFileType(BaseObjectType):
    pass


@strawberry_django.type(
    models.DataSource,
    fields='__all__',
    filters=DataSourceFilter
)
class DataSourceType(NetBoxObjectType):
    pass
