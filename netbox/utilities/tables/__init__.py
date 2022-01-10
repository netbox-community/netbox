from django_tables2 import RequestConfig

from utilities.paginator import EnhancedPaginator, get_paginate_count
from .columns import *
from .tables import *


#
# Pagination
#

def paginate_table(table, request):
    """
    Paginate a table given a request context.
    """
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
