import django_tables2 as tables
from django.utils.translation import gettext_lazy as _

from netbox.tables import NetBoxTable, columns
from ..models import Job


class BackgroundTasksTable(tables.Table):
    name = tables.Column()
    jobs = tables.Column(verbose_name=_("Queued Jobs"))
    oldest_job_timestamp = tables.Column(verbose_name=_("Oldest Queued Job"))
    started_jobs = tables.Column(verbose_name=_("Active Jobs"))
    deferred_jobs = tables.Column()
    finished_jobs = tables.Column()
    failed_jobs = tables.Column()
    scheduled_jobs = tables.Column()
    workers = tables.Column()
    host = tables.Column(accessor="connection_kwargs__host")
    port = tables.Column(accessor="connection_kwargs__port")
    db = tables.Column(accessor="connection_kwargs__db")
    pid = tables.Column(accessor="scheduler__pid", verbose_name=_("Scheduler PID"))

    class Meta:
        attrs = {
            'class': 'table table-hover object-list',
        }
