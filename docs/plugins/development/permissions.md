# Custom Model Actions

Plugins can register custom permission actions for their models. These actions appear as checkboxes in the [ObjectPermission](../../models/users/objectpermission.md) form alongside the standard view/add/change/delete actions, making it easy for administrators to grant or restrict access to plugin-specific functionality without manually entering action names.

For example, a plugin might define a `sync` action for a model that fetches data from an external source, or a `bypass` action that allows users to skip certain restrictions.

## Registering Model Actions

The preferred way to register custom actions is via Django's `Meta.permissions` on the model class. NetBox automatically registers these as model actions when the app is loaded:

```python title="models.py"
from netbox.models import NetBoxModel

class WidgetSync(NetBoxModel):
    # ... fields ...

    class Meta:
        permissions = [
            ('sync', 'Synchronize widgets from external source'),
            ('export', 'Export widgets to external system'),
        ]
```

Once registered, these actions appear as checkboxes in a flat list when creating or editing an ObjectPermission. The first element of each tuple is the action's identifier (used in code) and the second is the help text shown to administrators in the UI.

!!! note "Reserved action names"
    Action names that conflict with NetBox's built-in CRUD verbs (`view`, `add`, `change`, `delete`) are reserved and cannot be reused as custom actions.

## Granting an Action

Custom actions are granted just like any standard permission:

1. Open **Admin → Object Permissions** and create a new permission.
2. Select the relevant object type(s) (e.g. `my_plugin | widget sync`).
3. Tick the custom action's checkbox (e.g. `sync`).
4. Assign the permission to the desired users and/or groups.

Optional [constraints](../../models/users/objectpermission.md#constraints) may be added to limit the permission to a subset of objects.

## Checking an Action at Runtime

Custom actions follow Django's standard permission naming convention `<app_label>.<action>_<model>`. To check whether the current user is authorized to perform a custom action against a model, call `user.has_perm()`:

```python
if request.user.has_perm('my_plugin.sync_widgetsync'):
    # User is permitted to invoke the sync action
    ...
```

Per-object permission checks (which respect any [constraints](../../models/users/objectpermission.md#constraints) on the granting permission) work the same way:

```python
if request.user.has_perm('my_plugin.sync_widgetsync', obj=widget):
    ...
```

For class-based views, NetBox provides `ObjectPermissionRequiredMixin` from `utilities.views`, which integrates cleanly with these custom actions:

```python title="views.py"
from utilities.views import ObjectPermissionRequiredMixin
from django.views.generic import View

class SyncWidgetView(ObjectPermissionRequiredMixin, View):
    queryset = WidgetSync.objects.all()
    permission_required = 'my_plugin.sync_widgetsync'

    def post(self, request, pk):
        widget = self.get_object()
        widget.sync()
        return redirect(widget.get_absolute_url())
```
