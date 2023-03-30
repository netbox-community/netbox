import django_tables2 as tables
from django.utils.translation import gettext as _

from netbox.tables import NetBoxTable, columns
from ..models import Job


class JobTable(NetBoxTable):
    id = tables.Column(
        linkify=True
    )
    name = tables.Column(
        linkify=True
    )
    object_type = columns.ContentTypeColumn(
        verbose_name=_('Type')
    )
    object = tables.Column(
        linkify=True
    )
    status = columns.ChoiceFieldColumn()
    created = columns.DateTimeColumn()
    scheduled = columns.DateTimeColumn()
    interval = columns.DurationColumn()
    started = columns.DateTimeColumn()
    completed = columns.DateTimeColumn()
    actions = columns.ActionsColumn(
        actions=('delete',)
    )

    class Meta(NetBoxTable.Meta):
        model = Job
        fields = (
            'pk', 'id', 'object_type', 'object', 'name', 'status', 'created', 'scheduled', 'interval', 'started',
            'completed', 'user', 'job_id',
        )
        default_columns = (
            'pk', 'id', 'object_type', 'object', 'name', 'status', 'created', 'started', 'completed', 'user',
        )
