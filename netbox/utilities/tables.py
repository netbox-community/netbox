from django.apps import apps
from django.db.models import Q
from django.utils.module_loading import import_string
from django.utils.translation import gettext_lazy as _

from core.models import ObjectType
from netbox.registry import registry

__all__ = (
    'get_table_configs',
    'get_table_for_model',
    'get_table_ordering',
    'linkify_phone',
    'register_table_column'
)


def get_table_configs(table, user):
    """
    Return any available TableConfigs applicable to the given table & user.
    """
    TableConfig = apps.get_model('extras', 'TableConfig')
    return TableConfig.objects.filter(
        Q(shared=True) | Q(user=user if user.is_authenticated else None),
        object_type=ObjectType.objects.get_for_model(table.Meta.model),
        table=table.name,
        enabled=True,
    )


def get_table_for_model(model, name=None):
    name = name or f'{model.__name__}Table'
    try:
        return import_string(f'{model._meta.app_label}.tables.{name}')
    except ImportError:
        return


def get_table_ordering(request, table):
    """
    Given a request, return the prescribed table ordering, if any. This may be necessary to determine prior to rendering
    the table itself.
    """
    # Check for an explicit ordering
    if 'sort' in request.GET:
        return request.GET['sort'] or None

    # Check for a configured preference
    if request.user.is_authenticated:
        if preference := request.user.config.get(f'tables.{table.__name__}.ordering'):
            return preference


def linkify_phone(value):
    """
    Render a telephone number as a hyperlink.
    """
    if value is None:
        return None
    return f"tel:{value.replace(' ', '')}"


def register_table_column(column, name, *tables):
    """
    Register a custom column for use on one or more tables.

    Args:
        column: The column instance to register
        name: The name of the table column
        tables: One or more table classes
    """
    for table in tables:
        reg = registry['tables'][table]
        if name in reg:
            raise ValueError(_("A column named {name} is already defined for table {table_name}").format(
                name=name, table_name=table.__name__
            ))
        reg[name] = column
