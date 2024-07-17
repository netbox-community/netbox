from django.utils.translation import gettext as _

from netbox.tables.columns import ActionsColumn, ActionsItem

__all__ = (
    'NotificationActionsColumn',
)


class NotificationActionsColumn(ActionsColumn):
    actions = {
        'dismiss': ActionsItem(_('Dismiss'), 'trash-can-outline', 'delete', 'danger'),
    }
