import strawberry
import strawberry_django
from strawberry_django.pagination import OffsetPaginated

from .types import *


@strawberry.type(name="Query")
class CoreQuery:
    data_file: DataFileType = strawberry_django.field()
    data_file_list: OffsetPaginated[DataFileType] = strawberry_django.offset_paginated()

    data_source: DataSourceType = strawberry_django.field()
    data_source_list: OffsetPaginated[DataSourceType] = strawberry_django.offset_paginated()
