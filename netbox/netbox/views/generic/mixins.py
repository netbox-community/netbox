from django.shortcuts import get_object_or_404

from extras.models import TableConfig
from utilities.permissions import get_permission_for_model

__all__ = (
    'ActionsMixin',
    'TableMixin',
)


class ActionsMixin:
    """
    Maps action names to the set of required permissions for each. Object list views reference this mapping to
    determine whether to render the applicable button for each action: The button will be rendered only if the user
    possesses the specified permission(s).

    Standard actions include: add, import, export, bulk_edit, and bulk_delete. Some views extend this default map
    with custom actions, such as bulk_sync.
    """
    # actions = DEFAULT_ACTION_PERMISSIONS

    def get_permitted_actions(self, user, model=None):
        """
        Return a tuple of actions for which the given user is permitted to do.
        """
        model = model or self.queryset.model

        # Resolve required permissions for each action
        permitted_actions = []
        for action in self.actions:
            perms = action if type(action) is str else action.permissions_required  # Backward compatibility
            required_permissions = [
                get_permission_for_model(model, perm) for perm in perms
            ]
            if not required_permissions or user.has_perms(required_permissions):
                permitted_actions.append(action)

        return {
            action.name: action for action in permitted_actions
        }


class TableMixin:

    def get_table(self, data, request, bulk_actions=True):
        """
        Return the django-tables2 Table instance to be used for rendering the objects list.

        Args:
            data: Queryset or iterable containing table data
            request: The current request
            bulk_actions: Render checkboxes for object selection
        """

        # If a TableConfig has been specified, apply it & update the user's saved preference
        if tableconfig_id := request.GET.get('tableconfig_id'):
            tableconfig = get_object_or_404(TableConfig, pk=tableconfig_id)
            if request.user.is_authenticated:
                table = self.table.__name__
                request.user.config.set(f'tables.{table}.columns', tableconfig.columns)
                request.user.config.set(f'tables.{table}.ordering', tableconfig.ordering, commit=True)

        table = self.table(data, user=request.user)
        if 'pk' in table.base_columns and bulk_actions:
            table.columns.show('pk')
        table.configure(request)

        return table
