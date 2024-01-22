import django_tables2 as tables
from django_tables2.utils import A  # alias for Accessor
from django.urls import reverse
from django.utils.html import mark_safe
from django.utils.translation import gettext_lazy as _

from netbox.tables import BaseTable
from utilities.templatetags.helpers import annotated_date


class BackgroundQueueTable(BaseTable):
    name = tables.LinkColumn("core:background_task_list", args=[A("index"), "queued"], verbose_name=_("Name"))
    jobs = tables.LinkColumn("core:background_task_list", args=[A("index"), "queued"], verbose_name=_("Queued"))
    oldest_job_timestamp = tables.Column(verbose_name=_("Oldest Queued"))
    started_jobs = tables.LinkColumn("core:background_task_list", args=[A("index"), "started"], verbose_name=_("Active"))
    deferred_jobs = tables.LinkColumn("core:background_task_list", args=[A("index"), "deferred"], verbose_name=_("Deferred"))
    finished_jobs = tables.LinkColumn("core:background_task_list", args=[A("index"), "finished"], verbose_name=_("Finished"))
    failed_jobs = tables.LinkColumn("core:background_task_list", args=[A("index"), "failed"], verbose_name=_("Failed"))
    scheduled_jobs = tables.LinkColumn("core:background_task_list", args=[A("index"), "scheduled"], verbose_name=_("Scheduled"))
    workers = tables.LinkColumn("core:worker_list", args=[A("index")], verbose_name=_("Workers"))
    host = tables.Column(accessor="connection_kwargs__host", verbose_name=_("Host"))
    port = tables.Column(accessor="connection_kwargs__port", verbose_name=_("Port"))
    db = tables.Column(accessor="connection_kwargs__db", verbose_name=_("DB"))
    pid = tables.Column(accessor="scheduler__pid", verbose_name=_("Scheduler PID"))

    class Meta(BaseTable.Meta):
        empty_text = _('No tasks found')
        fields = (
            'name', 'jobs', 'oldest_job_timestamp', 'started_jobs', 'deferred_jobs', 'finished_jobs', 'failed_jobs', 'scheduled_jobs', 'workers', 'host', 'port', 'db', 'pid',
        )
        default_columns = (
            'name', 'jobs', 'started_jobs', 'deferred_jobs', 'finished_jobs', 'failed_jobs', 'scheduled_jobs', 'workers',
        )


class BackgroundTaskTable(BaseTable):
    id = tables.LinkColumn("core:background_task", args=[A("id")], verbose_name=_("ID"))
    created_at = tables.DateTimeColumn(verbose_name=_("Created"))
    enqueued_at = tables.DateTimeColumn(verbose_name=_("Enqueued"))
    ended_at = tables.DateTimeColumn(verbose_name=_("Ended"))
    status = tables.Column(empty_values=(), verbose_name=_("Status"))
    callable = tables.Column(empty_values=(), verbose_name=_("Callable"))

    class Meta(BaseTable.Meta):
        empty_text = _('No jobs found')
        fields = (
            'id', 'created_at', 'enqueued_at', 'ended_at', 'status', 'callable',
        )
        default_columns = (
            'id', 'created_at', 'enqueued_at', 'ended_at', 'status', 'callable',
        )

    def render_status(self, value, record):
        return record.get_status

    def render_callable(self, value, record):
        try:
            return record.func_name
        except Exception as e:
            return repr(e)

    def __init__(self, queue_index, *args, **kwargs):
        self.queue_index = queue_index
        super().__init__(*args, **kwargs)


class WorkerTable(BaseTable):
    name = tables.Column(verbose_name=_("Name"))
    state = tables.Column(verbose_name=_("State"))
    birth_date = tables.DateTimeColumn(verbose_name=_("Birth"))
    pid = tables.Column(verbose_name=_("PID"))

    class Meta(BaseTable.Meta):
        empty_text = _('No workers found')
        fields = (
            'name', 'state', 'birth_date', 'pid',
        )
        default_columns = (
            'name', 'state', 'birth_date', 'pid',
        )
