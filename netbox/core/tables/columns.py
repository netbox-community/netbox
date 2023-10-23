import django_tables2 as tables

from netbox.registry import registry

__all__ = (
    'BackendTypeColumn',
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
