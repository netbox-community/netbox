# Custom Model Actions

Plugins can register custom permission actions for their models. These actions appear as checkboxes in the ObjectPermission form, making it easy for administrators to grant or restrict access to plugin-specific functionality without manually entering action names.

For example, a plugin might define a "sync" action for a model that syncs data from an external source, or a "bypass" action that allows users to bypass certain restrictions.

## Registering Model Actions

The preferred way to register custom actions is via Django's `Meta.permissions` on the model class. NetBox will automatically register these as model actions when the app is loaded:

```python
from netbox.models import NetBoxModel

class MyModel(NetBoxModel):
    # ...

    class Meta:
        permissions = [
            ('sync', 'Synchronize data from external source'),
            ('export', 'Export data to external system'),
        ]
```

Once registered, these actions appear as checkboxes in a flat list when creating or editing an ObjectPermission.
