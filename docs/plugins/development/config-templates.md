# Jinja2 Config Templates

NetBox uses [Jinja2](https://jinja.palletsprojects.com/) to render [configuration templates](../../features/config-templates.md). Plugins can extend this rendering pipeline in two complementary ways:

1. **Register custom filters** — make new template filters available by name in every config template.
2. **Inject context variables** — add extra variables that are available inside every config template render.

---

## Registering Jinja2 Filters

### Via `jinja2_env.py` (auto-discovery)

Create a file named `jinja2_env.py` in your plugin root and expose a dict called `filters`. NetBox will auto-discover and register it when the plugin loads.

```python title="my_plugin/jinja2_env.py"
def prefix_list(device):
    """Return all prefixes assigned to a device's interfaces."""
    return [
        str(ip.address)
        for iface in device.interfaces.all()
        for ip in iface.ip_addresses.all()
    ]

filters = {
    'prefix_list': prefix_list,
}
```

The filter is then available in any config template:

```jinja2
{% for prefix in device | prefix_list %}
  network {{ prefix }}
{% endfor %}
```

### Via `register_jinja2_filters()`

You can also register filters programmatically inside your plugin's `ready()` method:

```python title="my_plugin/__init__.py"
from netbox.plugins import PluginConfig

class MyPluginConfig(PluginConfig):
    name = 'my_plugin'
    # ...

    def ready(self):
        super().ready()
        from netbox.plugins.registration import register_jinja2_filters
        from .jinja2_env import filters
        register_jinja2_filters(filters)
```

`register_jinja2_filters()` accepts a `dict` mapping filter names to callables. It raises `TypeError` if passed a non-dict or if any value is not callable.

### Precedence

Plugin-registered filters can be overridden on a per-instance basis via the [`JINJA2_FILTERS`](../../configuration/system.md#jinja2_filters) configuration parameter. Instance-level filters always take precedence over plugin-registered filters of the same name.

---

## Injecting Context Variables

Override `get_jinja2_context()` in your `PluginConfig` subclass to inject additional variables into every config template render context.

```python title="my_plugin/__init__.py"
from netbox.plugins import PluginConfig

class MyPluginConfig(PluginConfig):
    name = 'my_plugin'
    # ...

    def get_jinja2_context(self):
        from .utils import MyNamespace
        return {
            'my_plugin': MyNamespace(),
        }
```

The returned dict is merged into the template context, so `my_plugin` becomes available by name inside every config template:

```jinja2
{% set records = my_plugin.lookup(device.name) %}
```

!!! warning "Startup cost"
    `get_jinja2_context()` is called on **every** config template render, not once at startup. Keep it fast. Defer expensive lookups to the object you return rather than performing them in `get_jinja2_context()` itself.

!!! note "Conflict avoidance"
    Choose context variable names that are unlikely to collide with NetBox's built-in template variables (`device`, `queryset`, etc.) or with those contributed by other plugins. Prefixing with your plugin name is strongly recommended.
