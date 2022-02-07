# GraphQL API

## Defining the Schema Class

A plugin can extend NetBox's GraphQL API by registering its own schema class. By default, NetBox will attempt to import `graphql.schema` from the plugin, if it exists. This path can be overridden by defining `graphql_schema` on the PluginConfig instance as the dotted path to the desired Python class. This class must be a subclass of `graphene.ObjectType`.

### Example

```python
# graphql.py
import graphene
from netbox.graphql.fields import ObjectField, ObjectListField
from . import filtersets, models

class MyModelType(graphene.ObjectType):

    class Meta:
        model = models.MyModel
        fields = '__all__'
        filterset_class = filtersets.MyModelFilterSet

class MyQuery(graphene.ObjectType):
    mymodel = ObjectField(MyModelType)
    mymodel_list = ObjectListField(MyModelType)

schema = MyQuery
```

## GraphQL Objects

NetBox provides two object type classes for use by plugins.

::: netbox.graphql.types.BaseObjectType
    selection:
      members: false
    rendering:
      show_source: false

::: netbox.graphql.types.NetBoxObjectType
    selection:
      members: false
    rendering:
      show_source: false

## GraphQL Fields

NetBox provides two field classes for use by plugins.

::: netbox.graphql.fields.ObjectField
    selection:
      members: false
    rendering:
      show_source: false

::: netbox.graphql.fields.ObjectListField
    selection:
      members: false
    rendering:
      show_source: false
