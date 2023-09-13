__all__ = (
    'get_table_ordering',
    'linkify_phone',
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
