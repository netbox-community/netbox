from typing import List

import strawberry
import strawberry_django

from core import models
from .types import *


@strawberry.type
class CoreQuery:
    @strawberry.field
    def data_file(self, id: int) -> DataFileType:
        return models.DataFile.objects.get(pk=id)
    data_file_list: List[DataFileType] = strawberry_django.field()

    @strawberry.field
    def data_source(self, id: int) -> DataSourceType:
        return models.DataSource.objects.get(pk=id)
    data_source_list: List[DataSourceType] = strawberry_django.field()
