
import strawberry
import strawberry_django
from django.db.models import Q

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


schema = [
    DummyQuery,
]


#
# Extensions to core GraphQL types & filters (see netbox.graphql.types.register_type /
# netbox.graphql.filters.register_filter). These exercise the plugin extension point.
#

@strawberry.type
class SiteTypeExtension:
    models = ['dcim.site']

    @strawberry_django.field
    def dummy_plugin_field(self) -> str:
        return 'dummy-plugin-value'


@strawberry.type
class SiteFilterExtension:
    models = ['dcim.site']

    @strawberry_django.filter_field()
    def dummy_plugin_filter(self, value: str, prefix) -> Q:
        return Q(**{f'{prefix}name': value})


type_extensions = [
    SiteTypeExtension,
]

filter_extensions = [
    SiteFilterExtension,
]
