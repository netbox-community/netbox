from django.db.models import QuerySet
from rest_framework.exceptions import ValidationError
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.utils.urls import remove_query_param, replace_query_param

from netbox.api.exceptions import QuerySetNotOrdered
from netbox.config import get_config


class NetBoxPagination(LimitOffsetPagination):
    """
    Provides two mutually exclusive pagination mechanisms: offset-based and cursor-based.

    Offset-based pagination employs `offset` and (optionally) `limit` parameters to page through results following the
    model's natural order. `offset` indicates the number of results to skip. This provides very human-friendly behavior,
    but performance can suffer when querying very large data sets due the overhead required to determine the starting
    point in the database.

    Cursor-based pagination employs `start` and (optionally) `limit` parameters to page through results as ordered by
    the model's primary key (i.e. `id`). `start` indicates the numeric ID of the first object to return; `limit`
    indicates the maximum number of objects to return beginning with the specified ID. Objects *must* be ordered by ID
    to ensure pagination is consistent. This approach is less human-friendly but offers superior performance to
    offset-based pagination. In cursor mode, `count` is omitted (null) for performance.

    Offset- and cursor-based pagination are mutually exclusive: Only `offset` _or_ `start` is permitted for a request.

    `limit` may be set to zero (`?limit=0`). This returns all objects matching a query, but retains the same format as
    a paginated request. The limit can only be disabled if `MAX_PAGE_SIZE` has been set to 0 or None.
    """
    start_query_param = 'start'

    def __init__(self):
        self.default_limit = get_config().PAGINATE_COUNT
        self.start = None
        self._page_length = 0
        self._last_pk = None

    def paginate_queryset(self, queryset, request, view=None):

        if isinstance(queryset, QuerySet) and not queryset.ordered:
            raise QuerySetNotOrdered(
                "Paginating over an unordered queryset is unreliable. Ensure that a minimal "
                "ordering has been applied to the queryset for this API endpoint."
            )

        self.start = self.get_start(request)
        self.limit = self.get_limit(request)
        self.request = request

        # Cursor-based pagination
        if self.start is not None:
            if self.offset_query_param in request.query_params:
                raise ValidationError(
                    f"'{self.start_query_param}' and '{self.offset_query_param}' are mutually exclusive."
                )

            self.count = None
            self.offset = 0

            queryset = queryset.filter(pk__gte=self.start).order_by('pk')
            results = list(queryset[:self.limit]) if self.limit else list(queryset)

            self._page_length = len(results)
            if results:
                self._last_pk = results[-1].pk if hasattr(results[-1], 'pk') else results[-1]['pk']

            return results

        # Offset-based pagination
        if isinstance(queryset, QuerySet):
            self.count = self.get_queryset_count(queryset)
        else:
            # We're dealing with an iterable, not a QuerySet
            self.count = len(queryset)

        self.offset = self.get_offset(request)

        if self.limit and self.count > self.limit and self.template is not None:
            self.display_page_controls = True

        if self.count == 0 or self.offset > self.count:
            return list()

        if self.limit:
            return list(queryset[self.offset:self.offset + self.limit])
        return list(queryset[self.offset:])

    def get_start(self, request):
        try:
            value = int(request.query_params[self.start_query_param])
            if value < 0:
                raise ValidationError(f"Invalid '{self.start_query_param}' parameter: must be a non-negative integer.")
            return value
        except KeyError:
            return None
        except (ValueError, TypeError):
            raise ValidationError(f"Invalid '{self.start_query_param}' parameter: must be a non-negative integer.")

    def get_limit(self, request):
        max_limit = self.default_limit
        MAX_PAGE_SIZE = get_config().MAX_PAGE_SIZE
        if MAX_PAGE_SIZE:
            max_limit = min(max_limit, MAX_PAGE_SIZE)

        if self.limit_query_param:
            try:
                limit = int(request.query_params[self.limit_query_param])
                if limit < 0:
                    raise ValueError()

                if MAX_PAGE_SIZE:
                    if limit == 0:
                        max_limit = MAX_PAGE_SIZE
                    else:
                        max_limit = min(MAX_PAGE_SIZE, limit)
                else:
                    max_limit = limit
            except (KeyError, ValueError):
                pass

        return max_limit

    def get_queryset_count(self, queryset):
        return queryset.count()

    def get_next_link(self):

        # Pagination has been disabled
        if not self.limit:
            return None

        # Cursor mode
        if self.start is not None:
            if self._page_length < self.limit:
                return None
            url = self.request.build_absolute_uri()
            url = replace_query_param(url, self.start_query_param, self._last_pk + 1)
            url = replace_query_param(url, self.limit_query_param, self.limit)
            url = remove_query_param(url, self.offset_query_param)
            return url

        return super().get_next_link()

    def get_previous_link(self):

        # Pagination has been disabled
        if not self.limit:
            return None

        # Cursor mode: forward-only
        if self.start is not None:
            return None

        return super().get_previous_link()

    def get_schema_operation_parameters(self, view):
        parameters = super().get_schema_operation_parameters(view)
        parameters.append({
            'name': self.start_query_param,
            'required': False,
            'in': 'query',
            'description': (
                'Cursor-based pagination: return results with pk >= start, ordered by pk. '
                'Mutually exclusive with offset.'
            ),
            'schema': {
                'type': 'integer',
            },
        })
        return parameters


class StripCountAnnotationsPaginator(NetBoxPagination):
    """
    Strips the annotations on the queryset before getting the count
    to optimize pagination of complex queries.
    """
    def get_queryset_count(self, queryset):
        # Clone the queryset to avoid messing up the actual query
        cloned_queryset = queryset.all()
        cloned_queryset.query.annotations.clear()

        return cloned_queryset.count()


class LimitOffsetListPagination(LimitOffsetPagination):
    """
    DRF LimitOffset Paginator but for list instead of queryset
    """
    count = 0
    offset = 0

    def paginate_list(self, data, request, view=None):
        self.request = request
        self.limit = self.get_limit(request)
        self.count = len(data)
        self.offset = self.get_offset(request)

        if self.limit is None:
            self.limit = self.count

        if self.count == 0 or self.offset > self.count:
            return []

        if self.count > self.limit and self.template is not None:
            self.display_page_controls = True

        return data[self.offset:self.offset + self.limit]
