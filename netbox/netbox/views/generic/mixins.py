from collections import defaultdict

from utilities.permissions import get_permission_for_model

__all__ = (
    'ActionsMixin',
    'TableMixin',
)


class ActionsMixin:
    actions = ('add', 'import', 'export', 'bulk_edit', 'bulk_delete')
    action_perms = defaultdict(set, **{
        'add': {'add'},
        'import': {'add'},
        'bulk_edit': {'change'},
        'bulk_delete': {'delete'},
    })

    def get_permitted_actions(self, user, model=None):
        """
        Return a tuple of actions for which the given user is permitted to do.
        """
        model = model or self.queryset.model
        return [
            action for action in self.actions if user.has_perms([
                get_permission_for_model(model, name) for name in self.action_perms[action]
            ])
        ]


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
