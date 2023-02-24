# Application Registry

The registry is an in-memory data structure which houses various application-wide parameters, such as the list of enabled plugins. It is not exposed to the user and is not intended to be modified by any code outside of NetBox core.

The registry behaves essentially like a Python dictionary, with the notable exception that once a store (key) has been declared, it cannot be deleted or overwritten. The value of a store can, however, be modified; e.g. by appending a value to a list. Store values generally do not change once the application has been initialized.

The registry can be inspected by importing `registry` from `extras.registry`.

## Stores

### `data_backends`

A dictionary mapping data backend types to their respective classes. These are used to interact with [remote data sources](../models/core/datasource.md).

### `denormalized_fields`

Stores registration made using `netbox.denormalized.register()`. For each model, a list of related models and their field mappings is maintained to facilitate automatic updates.

### `model_features`

A dictionary of particular features (e.g. custom fields) mapped to the NetBox models which support them, arranged by app. For example:

```python
{
    'custom_fields': {
        'circuits': ['provider', 'circuit'],
        'dcim': ['site', 'rack', 'devicetype', ...],
        ...
    },
    'webhooks': {
        'extras': ['configcontext', 'tag', ...],
        'dcim': ['site', 'rack', 'devicetype', ...],
    },
    ...
}
```

Supported model features are listed in the [features matrix](./models.md#features-matrix).

### `plugins`

This store maintains all registered items for plugins, such as navigation menus, template extensions, etc.

### `search`

A dictionary mapping each model (identified by its app and label) to its search index class, if one has been registered for it.

### `views`

A hierarchical mapping of registered views for each model. Mappings are added using the `register_model_view()` decorator, and URLs paths can be generated from these using `get_model_urls()`.
