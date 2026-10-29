# Exporters

!!! info "This feature was introduced in NetBox v4.8."

The "Export" button on object list views offers a choice of export formats. NetBox provides CSV and (for certain object types) YAML exporters. Plugins can register their own exporters to add formats, such as XLSX or JSON, by subclassing NetBox's `Exporter` class and implementing its `export()` method.

An exporter with `tabular = True` exports the rows of the list view's table. NetBox resolves the table's columns and passes `export()` a list of column headers (`headers`) and an iterator of cell values for each row (`rows`). Tabular exporters are offered under both "Current View" (the user's selected columns) and "All Data" (all columns).

```python title="exporters.py"
import io

from openpyxl import Workbook

from netbox.exporters import Exporter, register_exporter

@register_exporter
class XLSXExporter(Exporter):
    slug = 'my_plugin.xlsx'
    label = 'Excel (XLSX)'
    content_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    file_extension = 'xlsx'
    tabular = True

    def export(self, *, request, queryset, headers=None, rows=None):
        workbook = Workbook(write_only=True)
        sheet = workbook.create_sheet()
        sheet.append(headers)
        for row in rows:
            sheet.append(row)
        buffer = io.BytesIO()
        workbook.save(buffer)
        return buffer.getvalue()
```

A non-tabular exporter works on the queryset directly, and is offered under "All Data" only. Override `supports_model()` to limit any exporter to specific models.

```python title="exporters.py"
from netbox.exporters import Exporter, register_exporter

@register_exporter
class VendorDeviceTypeExporter(Exporter):
    slug = 'my_plugin.vendor_device_types'
    label = 'Vendor Format'
    content_type = 'application/json'
    file_extension = 'json'

    def supports_model(self, model):
        return model._meta.label == 'dcim.DeviceType'

    def export(self, *, request, queryset, headers=None, rows=None):
        ...
```

The queryset passed to an exporter has the user's filters applied, and is restricted to objects the user has permission to view. It isn't sorted to match the list view's table; only the rows passed to a tabular exporter follow the table's sort order. `export()` returns the exported data as a string or bytes, or as an iterable of chunks. NetBox streams an iterable to the client if [`STREAMING_EXPORTS`](../../configuration/miscellaneous.md#streaming_exports) is enabled; otherwise, it collects the chunks before responding.

The `register_exporter()` decorator registers an exporter with NetBox. Exporters can be defined anywhere within a plugin, but must be imported during plugin initialization, under the PluginConfig's `ready()` method:

```python
def ready(self):
    super().ready()
    from my_plugin import exporters
```

`slug` must begin with a lowercase letter, and may contain only letters, digits, underscores, and dot-separated segments. A dotted namespace prefix (e.g. `my_plugin.xlsx`) is strongly recommended to avoid collisions with other plugins or with exporters added to NetBox in the future.

!!! warning "Exporters must be stateless"
    Registration instantiates the class once, and that single instance serves every request. Don't store per-request data on `self`.

## YAML Export

NetBox's YAML exporter supports any model which defines a `to_yaml()` method, including plugin models. The method returns a YAML document representing the object, and the exporter joins the documents for all exported objects.

To avoid a database query per object, set `yaml_prefetch` on the model to the related objects which `to_yaml()` accesses through reverse or many-to-many relations. The exporter passes these to the queryset's `prefetch_related()`. Related objects accessed through foreign keys are fetched in batches automatically.

```python title="models.py"
import yaml

from netbox.models import NetBoxModel

class Widget(NetBoxModel):
    ...
    yaml_prefetch = ('parts',)

    def to_yaml(self):
        data = {
            'name': self.name,
            'parts': [part.name for part in self.parts.all()],
        }
        return yaml.dump(data, sort_keys=False)
```

## Export Formats

The `export_format` query parameter selects an exporter by its slug:

| URL                                  | Result                                                 |
|--------------------------------------|--------------------------------------------------------|
| `?export=table&export_format=<slug>` | Current view, in the given format                      |
| `?export&export_format=<slug>`       | All data, in the given format                          |
| `?export=table`                      | Current view, as CSV                                   |
| `?export`                            | All data, as [YAML](#yaml-export) if the model supports it, or as CSV |

An unknown slug, or an exporter that doesn't support the model (or the current view), returns a 404 response. Exporters are available only in the web UI. The REST API supports [export templates](../../customization/export-templates.md) only.

::: netbox.exporters.Exporter
