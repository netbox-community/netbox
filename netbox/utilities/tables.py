from netbox.registry import registry

__all__ = (
    'get_table_ordering',
    'linkify_phone',
    'register_table_column'
)


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
    return f"tel:{value}"


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
            raise ValueError(f"A column named {name} is already defined for table {table.__name__}")
        reg[name] = column
