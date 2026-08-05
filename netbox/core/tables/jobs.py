import django_tables2 as tables
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
    execution_time = tables.Column(
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
        if not record.completed:
            # The job is still running, so distinguish its (provisional) elapsed time from a final one
            return format_html(
                '<span class="text-primary" title="{}">{}</span>', _('Still running'), value
            )

        return value

    def value_execution_time(self, record):
        # Export the recorded execution time verbatim, as a raw number of seconds. A running job's
        # provisional elapsed time is deliberately omitted, as is the clamping of anomalous negative
        # values applied when rendering: an export is intended for analysis.
        if record.execution_time is None:
            return None
        return round(record.execution_time.total_seconds(), 3)

    def order_execution_time(self, queryset, is_descending):
        # Order by the value the column actually displays, so that a long-running job is not sorted
        # as though it had no execution time. Jobs which never started sort last in either
        # direction, and pk breaks ties to keep pagination stable.
        elapsed_time = Job.elapsed_time_expression()
        ordering = elapsed_time.desc(nulls_last=True) if is_descending else elapsed_time.asc(nulls_last=True)
        return queryset.order_by(ordering, 'pk'), True


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
