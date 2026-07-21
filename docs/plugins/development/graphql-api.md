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
    def mymodel(self, id: int) -> MyModelType:
        return None
    mymodel_list: list[MyModelType] = strawberry_django.field()


schema = [
    MyQuery,
]
```

## Extending Core Types & Filters

!!! info "This feature was introduced in NetBox v4.6."

In addition to registering its own top-level query fields, a plugin can inject fields and filters onto NetBox's **existing** core GraphQL types (e.g. `DeviceType`). This allows a plugin's related data to be traversed within a single query rooted at a core object, rather than requiring a separate top-level query. This mirrors the `PluginTemplateExtension` mechanism used to extend core object views in the UI.

An extension is a mixin class declaring a `models` attribute: a list of the lowercased `app_label.model` labels of the core types it extends. Output-type extensions are collected from `graphql.type_extensions` and filter extensions from `graphql.filter_extensions` by default; these paths can be overridden via the `graphql_type_extensions` and `graphql_filter_extensions` attributes on the PluginConfig.

Each declared path must resolve to a list named `type_extensions` (or `filter_extensions`) - for example, defined in `graphql.py` alongside the schema, or re-exported from the plugin's `graphql` package.

### Type Extensions

An output-type extension is a `@strawberry.type` class whose fields and resolvers are spliced into the target type:

```python
# graphql.py (or graphql/type_extensions.py)
from typing import Annotated

import strawberry
import strawberry_django

from utilities.querysets import RestrictedPrefetch
from my_plugin.models import Widget


@strawberry.type
class DeviceTypeExtension:
    models = ['dcim.device']

    @strawberry_django.field(
        prefetch_related=lambda info: RestrictedPrefetch(
            'widgets', info.context.request.user, 'view', queryset=Widget.objects.all()
        ),
    )
    def widgets(self) -> list[Annotated['WidgetType', strawberry.lazy('my_plugin.graphql.types')]]:
        return self.widgets.all()


type_extensions = [
    DeviceTypeExtension,
]
```

!!! note
    Scope any related-object resolver with `RestrictedPrefetch(..., info.context.request.user, 'view', ...)`, as shown above. Object permissions are only applied to the top-level queryset, so a plain `prefetch_related='widgets'` returns related objects the requesting user may not be permitted to see.

### Filter Extensions

A filter extension is a `@strawberry.type` class declaring additional filters - either as annotated filter fields or as custom filter methods - which are spliced into the target filter:

```python
# graphql.py (or graphql/filter_extensions.py)
import strawberry
import strawberry_django
from django.db.models import Q


@strawberry.type
class DeviceFilterExtension:
    models = ['dcim.device']

    @strawberry_django.filter_field()
    def has_widgets(self, value: bool, prefix) -> Q:
        return Q(**{f'{prefix}widgets__isnull': not value})


filter_extensions = [
    DeviceFilterExtension,
]
```

With both registered, a client can fetch a device and its plugin-provided data in a single query:

```graphql
query {
  device_list(filters: { has_widgets: true }) {
    name
    widgets { id name }
  }
}
```

!!! note
    Extensions are strictly additive: they can only add new fields, never replace existing ones. If an extension declares a name the core type already provides, the core definition always takes precedence and the extension's version is ignored. If two extensions on the same type declare the same new name, the one whose plugin is loaded first (earlier in `PLUGINS`) wins. Both cases are logged as warnings under the `netbox.graphql` logger.

## GraphQL Objects

NetBox provides two object type classes for use by plugins.

::: netbox.graphql.types.BaseObjectType
    options:
      members: false

::: netbox.graphql.types.NetBoxObjectType
    options:
      members: false

## GraphQL Filters

NetBox provides a base filter class for use by plugins which employ subclasseses of `NetBoxModel`.

::: netbox.graphql.filters.NetBoxModelFilter
    options:
      members: false

Additionally, the following filter classes are available for subclasses of standard base models.

| Model Class           | FilterSet Class                                    |
|-----------------------|----------------------------------------------------|
| `PrimaryModel`        | `netbox.graphql.filters.PrimaryModelFilter`        |
| `OrganizationalModel` | `netbox.graphql.filters.OrganizationalModelFilter` |
| `NestedGroupModel`    | `netbox.graphql.filters.NestedGroupModelFilter`    |
