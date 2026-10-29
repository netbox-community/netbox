# Exporters

!!! info "This feature was introduced in NetBox v4.8."

The "Export" button on object list views offers a choice of export formats. NetBox provides CSV and (for certain object types) YAML exporters. Plugins can register their own exporters to add formats, such as XLSX or JSON, by subclassing NetBox's `TableExporter` or `Exporter` class.

A `TableExporter` exports the rows of the list view's table. NetBox resolves the table's columns and calls the exporter's `export_rows()` method (rather than `export()`) with a list of column headers and an iterator of cell values for each row. Table exporters are offered under both "Current View" (the user's selected columns) and "All Data" (all columns).

```python title="exporters.py"
import io

from openpyxl import Workbook

from netbox.exporters import TableExporter, register_exporter

@register_exporter
class XLSXExporter(TableExporter):
    slug = 'my_plugin.xlsx'
    label = 'Excel (XLSX)'
    content_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    file_extension = 'xlsx'

    def export_rows(self, *, request, headers, rows):
        workbook = Workbook(write_only=True)
        sheet = workbook.create_sheet()
        sheet.append(headers)
        for row in rows:
            sheet.append(row)
        buffer = io.BytesIO()
        workbook.save(buffer)
        return buffer.getvalue()
```

An `Exporter` works on the queryset directly, and is offered under "All Data" only. Override `supports_model()` to limit any exporter to specific models.

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

    def export(self, *, request, queryset):
        ...
```

The queryset passed to an exporter has the user's filters applied, and is restricted to objects the user has permission to view. `export()` and `export_rows()` return the exported data as a string or bytes, or as an iterable of chunks. NetBox streams an iterable to the client if [`STREAMING_EXPORTS`](../../configuration/miscellaneous.md#streaming_exports) is enabled; otherwise, it collects the chunks before responding.

The `register_exporter()` decorator registers an exporter with NetBox. Exporters can be defined anywhere within a plugin, but must be imported during plugin initialization, under the PluginConfig's `ready()` method:

```python
def ready(self):
    super().ready()
    from my_plugin import exporters
```

`slug` must begin with a lowercase letter, and may contain only letters, digits, underscores, and dot-separated segments. A dotted namespace prefix (e.g. `my_plugin.xlsx`) is strongly recommended to avoid collisions with other plugins or with exporters added to NetBox in the future.

!!! warning "Exporters must be stateless"
    Registration instantiates the class once, and that single instance serves every request. Don't store per-request data on `self`.

## Export Formats

The `export_format` query parameter selects an exporter by its slug:

| URL                                  | Result                                                 |
|--------------------------------------|--------------------------------------------------------|
| `?export=table&export_format=<slug>` | Current view, in the given format                      |
| `?export&export_format=<slug>`       | All data, in the given format                          |
| `?export=table`                      | Current view, as CSV                                   |
| `?export`                            | All data, as YAML if the model supports it, or as CSV  |

An unknown slug, or an exporter that doesn't support the model (or the current view), returns a 404 response. Exporters are available only in the web UI. The REST API supports [export templates](../../customization/export-templates.md) only.

::: netbox.exporters.Exporter

::: netbox.exporters.TableExporter
