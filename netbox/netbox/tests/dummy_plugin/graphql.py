
import strawberry
import strawberry_django

# Deliberate direct core-type import: schema modules load at assembly, after all extensions register.
from dcim.graphql.types import SiteType

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
    dummymodel_list: list[DummyModelType] = strawberry_django.field()
    dummy_plugin_site_list: list[SiteType] = strawberry_django.field()


schema = [
    DummyQuery,
]
