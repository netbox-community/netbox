from typing import List

import strawberry
import strawberry_django

from .types_v1 import *


@strawberry.type(name="Query")
class CoreQueryV1:
    data_file: DataFileTypeV1 = strawberry_django.field()
    data_file_list: List[DataFileTypeV1] = strawberry_django.field()

    data_source: DataSourceTypeV1 = strawberry_django.field()
    data_source_list: List[DataSourceTypeV1] = strawberry_django.field()
