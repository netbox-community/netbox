# NDX Importers

!!! info "This feature was introduced in NetBox v4.8."

NetBox imports device types, module types, and rack types from the [NetBox Data Exchange](../../features/ndx.md) catalog. Plugins can register importers for additional types of catalog entries by subclassing NetBox's `Importer` class.

Each catalog entry has a `type` (such as `device-type`), which determines the importer used. An importer must define the following attributes:

| Name         | Description                                                    |
|--------------|----------------------------------------------------------------|
| `entry_type` | The catalog entry type handled by the importer                 |
| `model`      | The model of the object created from an entry                  |
| `label`      | A human-friendly name for the entry type (displayed in the UI) |

An importer must also implement two methods:

* `find_existing(entry)` returns the existing object corresponding to a catalog entry (or `None`). It must not write to the database. It is called only when no object is already tracked by an import record for the entry.
* `import_entry(entry, instance, user, result)` creates or updates the object for an entry and returns it. `instance` is the existing object (if any) and `result` is the entry's `ImportResult`, to which any warnings can be appended.

`import_entry()` is called within a database transaction. Raise `ImportSkipped` to skip an entry, or Django's `ValidationError` to report an entry which cannot be imported. NetBox records the [import record](../../models/ndx/importrecord.md) and enrichment data for each imported object, and enforces object-level permissions on the object returned.

By default, importing an entry requires permission to add (or, for an existing object, to change) objects of the importer's model. Override `get_required_permissions(entry, instance)` to require additional permissions. An importer may also override `post_import(obj, entry, client, result)` to perform work outside the database transaction once an entry has been imported, such as retrieving files from the catalog. An exception raised by `post_import()` is reported as a warning; the import itself stands.

```python title="ndx_importers.py"
from ndx.importers import Importer, ImportSkipped, register_importer

from .models import Widget


@register_importer
class WidgetImporter(Importer):
    entry_type = 'my_plugin.widget'
    model = Widget
    label = 'Widget'

    def find_existing(self, entry):
        return Widget.objects.filter(slug=entry['slug']).first()

    def import_entry(self, entry, instance, user, result):
        if entry.get('deprecated'):
            raise ImportSkipped('This widget has been deprecated.')
        widget = instance or Widget(slug=entry['slug'])
        if instance:
            widget.snapshot()
        widget.name = entry['model']
        widget.full_clean()
        widget.save()
        return widget
```

Import the module from your plugin's `ready()` method to register its importers:

```python title="__init__.py"
from netbox.plugins import PluginConfig


class MyPluginConfig(PluginConfig):
    ...

    def ready(self):
        super().ready()
        from . import ndx_importers  # noqa: F401
```

An object deleted from NetBox has its import record deleted automatically.
