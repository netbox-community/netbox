# Application Registry

The registry is an in-memory data structure which houses various application-wide parameters, such as the list of enabled plugins. It is not exposed to the user and is not intended to be modified by any code outside of NetBox core.

The registry behaves essentially like a Python dictionary, with the notable exception that once a store (key) has been declared, it cannot be deleted or overwritten. The value of a store can, however, be modified; e.g. by appending a value to a list. Store values generally do not change once the application has been initialized.

The registry can be inspected by importing `registry` from `extras.registry`.

## Stores

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
        ...
    },
    ...
}
```

### `plugin_menu_items`

Navigation menu items provided by NetBox plugins. Each plugin is registered as a key with the list of menu items it provides. An example:

```python
{
    'Plugin A': (
        <MenuItem>, <MenuItem>, <MenuItem>,
    ),
    'Plugin B': (
        <MenuItem>, <MenuItem>, <MenuItem>,
    ),
}
```

### `plugin_template_extensions`

Plugin content that gets embedded into core NetBox templates. The store comprises NetBox models registered as dictionary keys, each pointing to a list of applicable template extension classes that exist. An example:

```python
{
    'dcim.site': [
        <TemplateExtension>, <TemplateExtension>, <TemplateExtension>,
    ],
    'dcim.rack': [
        <TemplateExtension>, <TemplateExtension>,
    ],
}
```
