import django_tables2 as tables
from django.utils.safestring import mark_safe

from netbox.registry import registry

__all__ = (
    'BackendTypeColumn',
    'BadgeColumn',
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


class BadgeColumn(tables.Column):
    """
    Render a colored badge for a value.

    Args:
        badges: A dictionary mapping of values to core.constants.Badge instances.
    """
    def __init__(self, badges, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.badges = badges

    def render(self, value):
        badge = self.badges.get(value)
        return mark_safe(f'<span class="badge text-bg-{badge.color}">{badge.label}</span>')

    def value(self, value):
        badge = self.badges.get(value)
        return badge.label
