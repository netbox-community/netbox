import django_tables2 as tables
from django.db.models import F
from django.utils.html import conditional_escape, format_html
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _

from core.constants import JOB_LOG_ENTRY_LEVELS
from core.models import Job
from core.tables.columns import BadgeColumn
from netbox.tables import BaseTable, NetBoxTable, columns
from utilities.string import humanize_duration


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
    execution_time = columns.DurationColumn(
        verbose_name=_('Execution Time'),
        # Render running jobs (which have no recorded execution time yet) rather than the placeholder
        empty_values=(),
    )
    queue_name = tables.Column(
        verbose_name=_('Queue'),
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
            'completed', 'execution_time', 'user', 'queue_name', 'log_entries', 'error', 'job_id',
        )
        default_columns = (
            'pk', 'id', 'object_type', 'object', 'name', 'status', 'created', 'started', 'execution_time', 'user',
        )

    def render_log_entries(self, value):
        return len(value)

    def render_execution_time(self, record):
        if (duration := record.elapsed_time) is None:
            return self.default

        value = humanize_duration(duration)
        if record.execution_time is None:
            # The job is still running, so distinguish its (provisional) elapsed time from a final one
            return format_html(
                '<span class="text-primary" title="{}">{}</span>', _('Still running'), value
            )

        return value

    def value_execution_time(self, record):
        # Export the raw number of seconds rather than the humanized rendering
        if (duration := record.elapsed_time) is None:
            return None
        return max(duration.total_seconds(), 0)

    def order_execution_time(self, queryset, is_descending):
        # Jobs with no recorded execution time are sorted last irrespective of the sort direction
        field = F('execution_time')
        ordering = field.desc(nulls_last=True) if is_descending else field.asc(nulls_last=True)
        return queryset.order_by(ordering), True


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

    def render_message(self, record, value):
        if record.get('level') == 'error' and '\n' in value:
            value = conditional_escape(value)
            return mark_safe(f'<pre class="p-0">{value}</pre>')
        return value
