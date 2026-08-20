import django_tables2 as tables
from django.utils.html import format_html
from django.utils.translation import gettext as _

from extras.choices import CustomFieldStatusChoices
from netbox.tables.columns import ActionsColumn, ActionsItem

__all__ = (
    'CustomFieldStatusColumn',
    'NotificationActionsColumn',
)


class CustomFieldStatusColumn(tables.Column):
    """
    Render a custom field's status as an icon: a checkmark where the field is live, and a warning
    where a bulk update of its stored data is still pending (see CustomFieldStatusChoices).

    An icon because the status is worth noting only in the exceptional case, which is any state
    other than active. The full label is given as hover text, and is what an export records.
    """
    ICONS = {
        True: ('text-bg-green', 'mdi-check-bold'),
        False: ('text-bg-orange', 'mdi-alert'),
    }

    def render(self, record):
        css_class, icon = self.ICONS[record.status == CustomFieldStatusChoices.STATUS_ACTIVE]
        return format_html(
            '<span class="badge {}" title="{}"><i class="mdi {}"></i></span>',
            css_class, record.get_status_display(), icon
        )

    def value(self, record):
        return record.get_status_display()


class NotificationActionsColumn(ActionsColumn):
    actions = {
        'dismiss': ActionsItem(_('Dismiss'), 'trash-can-outline', 'delete', 'danger'),
    }
