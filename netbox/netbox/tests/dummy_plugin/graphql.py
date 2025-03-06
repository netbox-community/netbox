from typing import List
import strawberry
import strawberry_django

from . import models


@strawberry_django.type(
    models.DummyModel,
    fields='__all__',
)
class DummyModelType:
    pass


@strawberry.type(name="Query")
class DummyQuery:
    dummymodel: DummyModelType = strawberry_django.field()
    dummymodel_list: List[DummyModelType] = strawberry_django.field()


schema = [
    DummyQuery,
]
