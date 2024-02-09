import django_tables2 as tables
from django.utils.translation import gettext_lazy as _
from django_tables2.utils import A

from core.tables.columns import RQJobStatusColumn
from netbox.tables import BaseTable


class BackgroundQueueTable(BaseTable):
    name = tables.Column(
        verbose_name=_("Name")
    )
    jobs = tables.Column(
        linkify=("core:background_task_list", [A("index"), "queued"]),
        verbose_name=_("Queued")
    )
    oldest_job_timestamp = tables.Column(
        verbose_name=_("Oldest Task")
    )
    started_jobs = tables.Column(
        linkify=("core:background_task_list", [A("index"), "started"]),
        verbose_name=_("Active")
    )
    deferred_jobs = tables.Column(
        linkify=("core:background_task_list", [A("index"), "deferred"]),
        verbose_name=_("Deferred")
    )
    finished_jobs = tables.Column(
        linkify=("core:background_task_list", [A("index"), "finished"]),
        verbose_name=_("Finished")
    )
    failed_jobs = tables.Column(
        linkify=("core:background_task_list", [A("index"), "failed"]),
        verbose_name=_("Failed")
    )
    scheduled_jobs = tables.Column(
        linkify=("core:background_task_list", [A("index"), "scheduled"]),
        verbose_name=_("Scheduled")
    )
    workers = tables.Column(
        linkify=("core:worker_list", [A("index")]),
        verbose_name=_("Workers")
    )
    host = tables.Column(
        accessor="connection_kwargs__host",
        verbose_name=_("Host")
    )
    port = tables.Column(
        accessor="connection_kwargs__port",
        verbose_name=_("Port")
    )
    db = tables.Column(
        accessor="connection_kwargs__db",
        verbose_name=_("DB")
    )
    pid = tables.Column(
        accessor="scheduler__pid",
        verbose_name=_("Scheduler PID")
    )

    class Meta(BaseTable.Meta):
        empty_text = _('No queues found')
        fields = (
            'name', 'jobs', 'oldest_job_timestamp', 'started_jobs', 'deferred_jobs', 'finished_jobs', 'failed_jobs',
            'scheduled_jobs', 'workers', 'host', 'port', 'db', 'pid',
        )
        default_columns = (
            'name', 'jobs', 'started_jobs', 'deferred_jobs', 'finished_jobs', 'failed_jobs', 'scheduled_jobs',
            'workers',
        )


class BackgroundTaskTable(BaseTable):
    id = tables.Column(
        linkify=("core:background_task", [A("id")]),
        verbose_name=_("ID")
    )
    created_at = tables.DateTimeColumn(
        verbose_name=_("Created")
    )
    enqueued_at = tables.DateTimeColumn(
        verbose_name=_("Enqueued")
    )
    ended_at = tables.DateTimeColumn(
        verbose_name=_("Ended")
    )
    status = RQJobStatusColumn(
        verbose_name=_("Status"),
        accessor='get_status'
    )
    callable = tables.Column(
        empty_values=(),
        verbose_name=_("Callable")
    )

    class Meta(BaseTable.Meta):
        empty_text = _('No tasks found')
        fields = (
            'id', 'created_at', 'enqueued_at', 'ended_at', 'status', 'callable',
        )
        default_columns = (
            'id', 'created_at', 'enqueued_at', 'ended_at', 'status', 'callable',
        )

    def render_callable(self, value, record):
        try:
            return record.func_name
        except Exception as e:
            return repr(e)


class WorkerTable(BaseTable):
    name = tables.Column(
        linkify=("core:worker", [A("name")]),
        verbose_name=_("Name")
    )
    state = tables.Column(
        verbose_name=_("State")
    )
    birth_date = tables.DateTimeColumn(
        verbose_name=_("Birth")
    )
    pid = tables.Column(
        verbose_name=_("PID")
    )

    class Meta(BaseTable.Meta):
        empty_text = _('No workers found')
        fields = (
            'name', 'state', 'birth_date', 'pid',
        )
        default_columns = (
            'name', 'state', 'birth_date', 'pid',
        )
