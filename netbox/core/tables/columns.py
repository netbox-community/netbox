import django_tables2 as tables
from django.utils.safestring import mark_safe

from core.constants import RQ_TASK_STATUSES
from netbox.registry import registry

__all__ = (
    'BackendTypeColumn',
    'RQJobStatusColumn',
)


class BackendTypeColumn(tables.Column):
    """
    Display a data backend type.
    """
    def render(self, value):
        if backend := registry['data_backends'].get(value):
            return backend.label
        return value

    def value(self, value):
        return value


class RQJobStatusColumn(tables.Column):
    """
    Render a colored label for the status of an RQ job.
    """
    def render(self, value):
        status = RQ_TASK_STATUSES.get(value)
        return mark_safe(f'<span class="badge text-bg-{status.color}">{status.label}</span>')

    def value(self, value):
        status = RQ_TASK_STATUSES.get(value)
        return status.label
