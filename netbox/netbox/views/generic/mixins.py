from collections import defaultdict

from utilities.permissions import get_permission_for_model

__all__ = (
    'ActionsMixin',
    'TableMixin',
)


class ActionsMixin:
    actions = {
        'add': {'add'},
        'import': {'add'},
        'export': {'view'},
        'bulk_edit': {'change'},
        'bulk_delete': {'delete'},
    }

    def get_permitted_actions(self, user, model=None):
        """
        Return a tuple of actions for which the given user is permitted to do.
        """
        model = model or self.queryset.model

        # TODO: Remove backward compatibility in Netbox v4.0
        # Determine how permissions are being mapped to actions for the view
        if type(self.actions) is dict:
            # New actions format (3.7+)
            permissions_map = self.actions
        elif hasattr(self, 'action_perms'):
            # Backward compatibility for <3.7
            permissions_map = self.action_perms
        else:
            # actions is still defined as a list or tuple (<3.7) but no custom mapping is defined; use the old
            # default mapping
            permissions_map = {
                'add': {'add'},
                'import': {'add'},
                'bulk_edit': {'change'},
                'bulk_delete': {'delete'},
            }

        # Resolve required permissions for each action
        permitted_actions = []
        for action in self.actions:
            required_permissions = [
                get_permission_for_model(model, name) for name in permissions_map.get(action, set())
            ]
            if not required_permissions or user.has_perms(required_permissions):
                permitted_actions.append(action)

        return permitted_actions


class TableMixin:

    def get_table(self, data, request, bulk_actions=True):
        """
        Return the django-tables2 Table instance to be used for rendering the objects list.

        Args:
            data: Queryset or iterable containing table data
            request: The current request
            bulk_actions: Render checkboxes for object selection
        """
        table = self.table(data, user=request.user)
        if 'pk' in table.base_columns and bulk_actions:
            table.columns.show('pk')
        table.configure(request)

        return table
