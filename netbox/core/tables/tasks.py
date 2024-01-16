import django_tables2 as tables
from django_tables2.utils import A  # alias for Accessor
from django.urls import reverse
from django.utils.html import mark_safe
from django.utils.translation import gettext_lazy as _

from netbox.tables import NetBoxTable, columns
from ..models import Job


class BackgroundTasksTable(tables.Table):
    name = tables.LinkColumn("core:background_tasks_queues", args=[A("index")], verbose_name=_("Name"))
    jobs = tables.LinkColumn("core:background_tasks_queues", args=[A("index")], verbose_name=_("Queued Jobs"))
    oldest_job_timestamp = tables.Column(verbose_name=_("Oldest Queued Job"))
    started_jobs = tables.Column(verbose_name=_("Active Jobs"))
    deferred_jobs = tables.Column(verbose_name=_("Deferred Jobs"))
    finished_jobs = tables.Column(verbose_name=_("Finished Jobs"))
    failed_jobs = tables.Column(verbose_name=_("Failed Jobs"))
    scheduled_jobs = tables.Column(verbose_name=_("Scheduled Jobs"))
    workers = tables.Column(verbose_name=_("Workers"))
    host = tables.Column(accessor="connection_kwargs__host", verbose_name=_("Host"))
    port = tables.Column(accessor="connection_kwargs__port", verbose_name=_("Port"))
    db = tables.Column(accessor="connection_kwargs__db", verbose_name=_("DB"))
    pid = tables.Column(accessor="scheduler__pid", verbose_name=_("Scheduler PID"))

    class Meta:
        attrs = {
            'class': 'table table-hover object-list',
        }


class BackgroundTasksQueueTable(tables.Table):
    # id = tables.LinkColumn("core:background_tasks_queues", args=[A("index")], verbose_name=_("ID"))
    id = tables.Column(empty_values=(), verbose_name=_("ID"))
    created_at = tables.Column(verbose_name=_("Created"))
    enqueued_at = tables.Column(verbose_name=_("Enqueued"))
    ended_at = tables.Column(verbose_name=_("Ended"))
    status = tables.Column(empty_values=(), verbose_name=_("Status"))
    callable = tables.Column(empty_values=(), verbose_name=_("Callable"))

    class Meta:
        attrs = {
            'class': 'table table-hover object-list',
        }

    def render_id(self, value, record):
        return mark_safe('<a href=' + reverse(
            "core:background_tasks_job_detail",
            args=[self.queue_index, value]) + '>' + value + '</a>'
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
