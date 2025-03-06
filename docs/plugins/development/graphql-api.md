# GraphQL API

## Defining the Schema Class

A plugin can extend NetBox's GraphQL API by registering its own schema class. By default, NetBox will attempt to import `graphql.schema` from the plugin, if it exists. This path can be overridden by defining `graphql_schema` on the PluginConfig instance as the dotted path to the desired Python class.

### Example

```python
# graphql.py
import strawberry
import strawberry_django

from . import models


@strawberry_django.type(
    models.MyModel,
    fields='__all__',
)
class MyModelType:
    pass


@strawberry.type
class MyQuery:
    @strawberry.field
    def dummymodel(self, id: int) -> DummyModelType:
        return None
    dummymodel_list: list[DummyModelType] = strawberry_django.field()


schema = [
    MyQuery,
]
```

## GraphQL Objects

NetBox provides two object type classes for use by plugins.

::: netbox.graphql.types.BaseObjectType
    options:
      members: false

::: netbox.graphql.types.NetBoxObjectType
    options:
      members: false
