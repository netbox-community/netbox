from django_tables2 import RequestConfig

from utilities.paginator import EnhancedPaginator, get_paginate_count
from .columns import *
from .tables import *


def configure_table(table, request):
    """
    Paginate a table given a request context.
    """
    # Save ordering preference
    if request.user.is_authenticated:
        table_name = table.__class__.__name__
        if table.prefixed_order_by_field in request.GET:
            # If an ordering has been specified as a query parameter, save it as the
            # user's preferred ordering for this table.
            ordering = request.GET.getlist(table.prefixed_order_by_field)
            request.user.config.set(f'tables.{table_name}.ordering', ordering, commit=True)
        elif ordering := request.user.config.get(f'tables.{table_name}.ordering'):
            # If no ordering has been specified, set the preferred ordering (if any).
            table.order_by = ordering

    # Paginate the table results
    paginate = {
        'paginator_class': EnhancedPaginator,
        'per_page': get_paginate_count(request)
    }
    RequestConfig(request, paginate).configure(table)


#
# Callables
#

def linkify_phone(value):
    if value is None:
        return None
    return f"tel:{value}"
