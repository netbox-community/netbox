from typing import List

import strawberry
import strawberry_django

from .types import *


@strawberry.type(name="Query")
class CoreQuery:
    data_file: DataFileType = strawberry_django.field()
    data_file_list: List[DataFileType] = strawberry_django.field()

    data_source: DataSourceType = strawberry_django.field()
    data_source_list: List[DataSourceType] = strawberry_django.field()
