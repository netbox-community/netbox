# Jinja Config Templates

NetBox uses [Jinja](https://jinja.palletsprojects.com/) to render [configuration templates](../../features/configuration-rendering.md#configuration-templates). Plugins can extend this rendering pipeline in two complementary ways:

1. **Register custom filters** — make new template filters available by name in every config template.
2. **Inject context variables** — add extra variables that are available inside every config template render.

---

## Registering Jinja Filters

### Via `jinja_env.py` (auto-discovery)

Create a file named `jinja_env.py` in your plugin root and expose a dict called `filters`. NetBox will auto-discover and register it when the plugin loads.

```python title="my_plugin/jinja_env.py"
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

### Via `register_jinja_filters()`

You can also register filters programmatically inside your plugin's `ready()` method:

```python title="my_plugin/__init__.py"
from netbox.plugins import PluginConfig

class MyPluginConfig(PluginConfig):
    name = 'my_plugin'
    # ...

    def ready(self):
        super().ready()
        from netbox.plugins.registration import register_jinja_filters
        from .jinja_env import filters
        register_jinja_filters(filters)
```

`register_jinja_filters()` accepts a `dict` mapping filter names to callables. It raises `TypeError` if passed a non-dict or if any value is not callable.

### Precedence

The full filter precedence from lowest to highest is: **NetBox built-in filters** (e.g. `env`) → **plugin-registered filters** → **instance [`JINJA_FILTERS`](../../configuration/system.md#jinja_filters)**. Instance-level filters always win, so site admins can override anything without touching a plugin.

If two plugins register a filter with the same name, the later-loaded plugin's version wins and NetBox will log a warning.

For example, if `my_plugin` registers a `prefix_list` filter but a site needs different behaviour, the operator can replace it in `configuration.py` without touching the plugin:

```python title="configuration.py"
def prefix_list(device):
    # Site-local override: include only loopback prefixes
    return [
        str(ip.address)
        for iface in device.interfaces.filter(type='loopback')
        for ip in iface.ip_addresses.all()
    ]

JINJA_FILTERS = {
    'prefix_list': prefix_list,
}
```

---

## Injecting Context Variables

Override `get_jinja_context()` in your `PluginConfig` subclass to inject additional variables into every config template render context.

```python title="my_plugin/__init__.py"
from netbox.plugins import PluginConfig

class MyPluginConfig(PluginConfig):
    name = 'my_plugin'
    # ...

    def get_jinja_context(self):
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
    `get_jinja_context()` is called on **every** config template render, not once at startup. Keep it fast. Defer expensive lookups to the object you return rather than performing them in `get_jinja_context()` itself.

!!! note "Conflict avoidance"
    Choose context variable names that are unlikely to collide with NetBox's built-in template variables (`device`, `queryset`, etc.) or with those contributed by other plugins. Prefixing with your plugin name is strongly recommended.

    In addition, avoid top-level app-label names (`dcim`, `ipam`, `virtualization`, etc.). The auto-populated template context maps each app label to a dict of its public model classes; returning a key like `'dcim'` from `get_jinja_context()` will silently replace that entire namespace.

!!! note "No per-render context"
    `get_jinja_context()` receives no arguments — it has no access to the object being rendered or the caller-supplied context. It is intended for plugin-global namespaces (e.g. a lazily-evaluated query helper). Per-object logic belongs in the template itself or in a custom filter.
