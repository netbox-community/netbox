# Custom Model Actions

Plugins can register custom permission actions for their models. These actions appear as checkboxes in the ObjectPermission form, making it easy for administrators to grant or restrict access to plugin-specific functionality without manually entering action names.

For example, a plugin might define a "sync" action for a model that syncs data from an external source, or a "bypass" action that allows users to bypass certain restrictions.

## Registering Model Actions

To register custom actions for a model, call `register_model_actions()` in your plugin's `ready()` method:

```python
# __init__.py
from netbox.plugins import PluginConfig

class MyPluginConfig(PluginConfig):
    name = 'my_plugin'
    # ...

    def ready(self):
        super().ready()
        from utilities.permissions import ModelAction, register_model_actions
        from .models import MyModel

        register_model_actions(MyModel, [
            ModelAction('sync', help_text='Synchronize data from external source'),
            ModelAction('export', help_text='Export data to external system'),
        ])

config = MyPluginConfig
```

Once registered, these actions will appear grouped under your model's name when creating or editing an ObjectPermission that includes your model as an object type.

::: utilities.permissions.ModelAction

::: utilities.permissions.register_model_actions
