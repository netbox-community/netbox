import django_tables2 as tables
from django.utils.translation import gettext_lazy as _

from core.models import ObjectChange
from netbox.tables import NetBoxTable, columns
from .template_code import *

__all__ = (
    'ObjectChangeTable',
)


class ObjectChangeTable(NetBoxTable):
    time = columns.DateTimeColumn(
        verbose_name=_('Time'),
        timespec='minutes',
        linkify=True
    )
    user_name = tables.Column(
        verbose_name=_('Username')
    )
    full_name = tables.TemplateColumn(
        accessor=tables.A('user'),
        template_code=OBJECTCHANGE_FULL_NAME,
        verbose_name=_('Full Name'),
        orderable=False
    )
    action = columns.ChoiceFieldColumn(
        verbose_name=_('Action'),
    )
    changed_object_type = columns.ContentTypeColumn(
        verbose_name=_('Type')
    )
    object_repr = tables.TemplateColumn(
        accessor=tables.A('changed_object'),
        template_code=OBJECTCHANGE_OBJECT,
        verbose_name=_('Object'),
        orderable=False
    )
    request_id = tables.TemplateColumn(
        template_code=OBJECTCHANGE_REQUEST_ID,
        verbose_name=_('Request ID')
    )
    actions = columns.ActionsColumn(
        actions=()
    )

    class Meta(NetBoxTable.Meta):
        model = ObjectChange
        fields = (
            'pk', 'time', 'user_name', 'full_name', 'action', 'changed_object_type', 'object_repr', 'request_id',
            'actions',
        )
