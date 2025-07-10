import django_tables2 as tables
from django.utils.translation import gettext_lazy as _

from netbox.tables import BaseTable, NetBoxTable, columns
from core.constants import JOB_LOG_ENTRY_LEVELS
from core.models import Job
from core.tables.columns import BadgeColumn


class JobTable(NetBoxTable):
    id = tables.Column(
        verbose_name=_('ID'),
        linkify=True
    )
    name = tables.Column(
        verbose_name=_('Name'),
        linkify=True
    )
    object_type = columns.ContentTypeColumn(
        verbose_name=_('Type')
    )
    object = tables.Column(
        verbose_name=_('Object'),
        linkify=True,
        orderable=False
    )
    status = columns.ChoiceFieldColumn(
        verbose_name=_('Status'),
    )
    created = columns.DateTimeColumn(
        verbose_name=_('Created'),
    )
    scheduled = columns.DateTimeColumn(
        verbose_name=_('Scheduled'),
    )
    interval = columns.DurationColumn(
        verbose_name=_('Interval'),
    )
    started = columns.DateTimeColumn(
        verbose_name=_('Started'),
    )
    completed = columns.DateTimeColumn(
        verbose_name=_('Completed'),
    )
    log_entries = tables.Column(
        verbose_name=_('Log Entries'),
    )
    actions = columns.ActionsColumn(
        actions=('delete',)
    )

    class Meta(NetBoxTable.Meta):
        model = Job
        fields = (
            'pk', 'id', 'object_type', 'object', 'name', 'status', 'created', 'scheduled', 'interval', 'started',
            'completed', 'user', 'error', 'job_id',
        )
        default_columns = (
            'pk', 'id', 'object_type', 'object', 'name', 'status', 'created', 'started', 'completed', 'user',
        )

    def render_log_entries(self, value):
        return len(value)


class JobLogEntryTable(BaseTable):
    timestamp = columns.DateTimeColumn(
        timespec='milliseconds',
        verbose_name=_('Time'),
    )
    level = BadgeColumn(
        badges=JOB_LOG_ENTRY_LEVELS,
        verbose_name=_('Level'),
    )
    message = tables.Column(
        verbose_name=_('Message'),
    )

    class Meta(BaseTable.Meta):
        empty_text = _('No log entries')
        fields = ('timestamp', 'level', 'message')
