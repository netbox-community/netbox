from typing import Annotated, List

import strawberry
import strawberry_django
from django.contrib.contenttypes.models import ContentType as DjangoContentType

from core import models
from netbox.graphql.types_v1 import BaseObjectTypeV1, PrimaryObjectTypeV1
from .filters_v1 import *

__all__ = (
    'ContentTypeV1',
    'DataFileTypeV1',
    'DataSourceTypeV1',
    'ObjectChangeTypeV1',
)


@strawberry_django.type(
    models.DataFile,
    exclude=['data',],
    filters=DataFileFilterV1,
    pagination=True
)
class DataFileTypeV1(BaseObjectTypeV1):
    source: Annotated["DataSourceTypeV1", strawberry.lazy('core.graphql.types_v1')]


@strawberry_django.type(
    models.DataSource,
    fields='__all__',
    filters=DataSourceFilterV1,
    pagination=True
)
class DataSourceTypeV1(PrimaryObjectTypeV1):
    datafiles: List[Annotated["DataFileTypeV1", strawberry.lazy('core.graphql.types_v1')]]


@strawberry_django.type(
    models.ObjectChange,
    fields='__all__',
    filters=ObjectChangeFilterV1,
    pagination=True
)
class ObjectChangeTypeV1(BaseObjectTypeV1):
    pass


@strawberry_django.type(
    DjangoContentType,
    fields='__all__',
    pagination=True
)
class ContentTypeV1:
    pass
