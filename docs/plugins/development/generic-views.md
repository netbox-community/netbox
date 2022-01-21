# Generic Views

NetBox provides several generic view classes to facilitate common operations, such as creating, viewing, modifying, and deleting objects. Plugins can subclass these views for their own use.

| View Class | Description |
|------------|-------------|
| `ObjectView` | View a single object |
| `ObjectEditView` | Create or edit a single object |
| `ObjectDeleteView` | Delete a single object |
| `ObjectListView` | View a list of objects |
| `BulkImportView` | Import a set of new objects |
| `BulkEditView` | Edit multiple objects |
| `BulkDeleteView` | Delete multiple objects |

!!! note
    Please note that only the classes which appear in this documentation are currently supported. Although other classes may be present within the `views.generic` module, they are not yet supported for use by plugins.

### Example Usage

```python
# views.py
from netbox.views.generic import ObjectEditView
from .models import Thing

class ThingEditView(ObjectEditView):
    queryset = Thing.objects.all()
    template_name = 'myplugin/thing.html'
    ...
```

## Object Views

Below is the class definition for NetBox's BaseObjectView. The attributes and methods defined here are available on all generic views which handle a single object.

::: netbox.views.generic.base.BaseObjectView
    rendering:
      show_source: false

::: netbox.views.generic.ObjectView
    selection:
      members:
        - get_object
        - get_template_name
    rendering:
      show_source: false

::: netbox.views.generic.ObjectEditView
    selection:
      members:
        - get_object
        - alter_object
    rendering:
      show_source: false

::: netbox.views.generic.ObjectDeleteView
    selection:
      members:
        - get_object
    rendering:
      show_source: false

## Multi-Object Views

Below is the class definition for NetBox's BaseMultiObjectView. The attributes and methods defined here are available on all generic views which deal with multiple objects.

::: netbox.views.generic.base.BaseMultiObjectView
    rendering:
      show_source: false

::: netbox.views.generic.ObjectListView
    selection:
      members:
        - get_table
        - export_table
        - export_template
    rendering:
      show_source: false

::: netbox.views.generic.BulkImportView
    selection:
      members: false
    rendering:
      show_source: false

::: netbox.views.generic.BulkEditView
    selection:
      members: false
    rendering:
      show_source: false

::: netbox.views.generic.BulkDeleteView
    selection:
      members:
        - get_form
    rendering:
      show_source: false
