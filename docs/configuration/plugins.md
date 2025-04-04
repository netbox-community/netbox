# Plugin Parameters

## PLUGINS

Default: Empty

A list of installed [NetBox plugins](../plugins/index.md) to enable. Plugins will not take effect unless they are listed here.

!!! warning
    Plugins extend NetBox by allowing external code to run with the same access and privileges as NetBox itself. Only install plugins from trusted sources. The NetBox maintainers make absolutely no guarantees about the integrity or security of your installation with plugins enabled.

---

## PLUGINS_CONFIG

Default: Empty

This parameter holds configuration settings for individual NetBox plugins. It is defined as a dictionary, with each key using the name of an installed plugin. The specific parameters supported are unique to each plugin: Reference the plugin's documentation to determine the supported parameters. An example configuration is shown below:

```python
PLUGINS_CONFIG = {
    'plugin1': {
        'foo': 123,
        'bar': True
    },
    'plugin2': {
        'foo': 456,
    },
}
```

Note that a plugin must be listed in `PLUGINS` for its configuration to take effect.

---

## PLUGINS_CONFIG

Default: Empty

This parameter holds configuration settings for how the individual plugins are displayed in the plugins table under Admin->System->Plugins.  Declaring `hidden` as True will make it so the plugin is not shown in the table.  Declaring `disabled` will make it show the plugin in the table, but it won't be linked to the details and installation page for the plugin. An example configuration is shown below:

```python
PLUGINS_TABLE_CONFIG = {
    'plugin1': {
        'hidden': True,
    },
    'plugin2': {
        'disabled': True,
    },
}
```

---
