from django.db.models import QuerySet
from django.utils.encoding import force_str
from django.utils.translation import gettext_lazy as _
from rest_framework.pagination import LimitOffsetPagination, CursorPagination, BasePagination, _reverse_ordering
from rest_framework.response import Response

from netbox.config import get_config
from rest_framework.compat import coreapi, coreschema


class OptionalLimitOffsetPagination(LimitOffsetPagination):
    """
    Override the stock paginator to allow setting limit=0 to disable pagination for a request. This returns all objects
    matching a query, but retains the same format as a paginated request. The limit can only be disabled if
    MAX_PAGE_SIZE has been set to 0 or None.
    """
    def __init__(self):
        self.default_limit = get_config().PAGINATE_COUNT

    def paginate_queryset(self, queryset, request, view=None):

        if isinstance(queryset, QuerySet):
            self.count = self.get_queryset_count(queryset)
        else:
            # We're dealing with an iterable, not a QuerySet
            self.count = len(queryset)

        self.limit = self.get_limit(request)
        self.offset = self.get_offset(request)
        self.request = request

        if self.limit and self.count > self.limit and self.template is not None:
            self.display_page_controls = True

        if self.count == 0 or self.offset > self.count:
            return list()

        if self.limit:
            return list(queryset[self.offset:self.offset + self.limit])
        else:
            return list(queryset[self.offset:])

    def get_limit(self, request):
        if self.limit_query_param:
            try:
                limit = int(request.query_params[self.limit_query_param])
                if limit < 0:
                    raise ValueError()
                # Enforce maximum page size, if defined
                MAX_PAGE_SIZE = get_config().MAX_PAGE_SIZE
                if MAX_PAGE_SIZE:
                    return MAX_PAGE_SIZE if limit == 0 else min(limit, MAX_PAGE_SIZE)
                return limit
            except (KeyError, ValueError):
                pass

        return self.default_limit

    def get_queryset_count(self, queryset):
        return queryset.count()

    def get_next_link(self):

        # Pagination has been disabled
        if not self.limit:
            return None

        return super().get_next_link()

    def get_previous_link(self):

        # Pagination has been disabled
        if not self.limit:
            return None

        return super().get_previous_link()


class CursorPaginationWithNoLimit(CursorPagination):
    """
    Allow setting limit=0 to disable pagination for a request. The limit can only be disabled if
    MAX_PAGE_SIZE has been set to 0 or None.
    """
    page_size_query_param = 'limit'

    def __init__(self) -> None:
        self.default_page_size = get_config().PAGINATE_COUNT

    def paginate_queryset(self, queryset, request, view=None):
        """
        Reuses the implementation from CursorPagination with minor modification to handle limit=0.
        """
        self.page_size = self.get_page_size(request)

        self.base_url = request.build_absolute_uri()
        self.ordering = self.get_ordering(request, queryset, view)

        self.cursor = self.decode_cursor(request)
        if self.cursor is None:
            (offset, reverse, current_position) = (0, False, None)
        else:
            (offset, reverse, current_position) = self.cursor

        # Cursor pagination always enforces an ordering.
        if reverse:
            queryset = queryset.order_by(*_reverse_ordering(self.ordering))
        else:
            queryset = queryset.order_by(*self.ordering)

        # If we have a cursor with a fixed position then filter by that.
        if current_position is not None:
            order = self.ordering[0]
            is_reversed = order.startswith('-')
            order_attr = order.lstrip('-')

            # Test for: (cursor reversed) XOR (queryset reversed)
            if self.cursor.reverse != is_reversed:
                kwargs = {order_attr + '__lt': current_position}
            else:
                kwargs = {order_attr + '__gt': current_position}

            queryset = queryset.filter(**kwargs)

        if self.page_size:
            # If we have an offset cursor then offset the entire page by that amount.
            # We also always fetch an extra item in order to determine if there is a
            # page following on from this one.
            results = list(queryset[offset:offset + self.page_size + 1])
            self.page = list(results[:self.page_size])
        else:
            self.page = results = list(queryset[offset:])

        # Determine the position of the final item following the page.
        if len(results) > len(self.page):
            has_following_position = True
            following_position = self._get_position_from_instance(results[-1], self.ordering)
        else:
            has_following_position = False
            following_position = None

        if reverse:
            # If we have a reverse queryset, then the query ordering was in reverse
            # so we need to reverse the items again before returning them to the user.
            self.page = list(reversed(self.page))

            # Determine next and previous positions for reverse cursors.
            self.has_next = (current_position is not None) or (offset > 0)
            self.has_previous = has_following_position
            if self.has_next:
                self.next_position = current_position
            if self.has_previous:
                self.previous_position = following_position
        else:
            # Determine next and previous positions for forward cursors.
            self.has_next = has_following_position
            self.has_previous = (current_position is not None) or (offset > 0)
            if self.has_next:
                self.next_position = following_position
            if self.has_previous:
                self.previous_position = current_position

        # Display page controls in the browsable API if there is more
        # than one page.
        if (self.has_previous or self.has_next) and self.template is not None:
            self.display_page_controls = True

        return self.page

    def get_page_size(self, request):
        if self.page_size_query_param:
            try:
                page_size = int(request.query_params[self.page_size_query_param])
                if page_size < 0:
                    raise ValueError()
                # Enforce maximum page size, if defined
                MAX_PAGE_SIZE = get_config().MAX_PAGE_SIZE
                if MAX_PAGE_SIZE:
                    return MAX_PAGE_SIZE if page_size == 0 else min(page_size, MAX_PAGE_SIZE)
                return page_size
            except (KeyError, ValueError):
                pass

        return self.default_page_size


class TwoModePagination(BasePagination):
    """
    Pagination that allows user to toggle between LimitOffsetPagination and CursorPagination. The default
    is LimitOffsetPagination.
    """
    pagination_mode_param = 'pagination_mode'
    pagination_mode_description = _(
        'Mode selector for LimitOffsetPagination (default) and CursorPagination.\n'
        '`offset` and `limit` are used for LimitOffsetPagination.\n'
        '`cursor` and `limit` are used for CursorPagination.')
    limit_offset_key = 'limit_offset'
    cursor_pagination_key = 'cursor'

    def __init__(
        self,
        limit_offset_paginator=OptionalLimitOffsetPagination,
        cursor_paginator=CursorPaginationWithNoLimit,
    ) -> None:
        self._limit_offset_pagination = limit_offset_paginator()
        self._cursor_pagination = cursor_paginator()

        self._chosen_pagination = self._limit_offset_pagination

    def paginate_queryset(self, queryset, request: Response, view=None):
        mode = request.query_params.get(self.pagination_mode_param)
        if mode == self.cursor_pagination_key:
            self._chosen_pagination = self._cursor_pagination
        return self._chosen_pagination.paginate_queryset(queryset, request, view)

    def get_paginated_response(self, data):
        return self._chosen_pagination.get_paginated_response(data)

    def get_paginated_response_schema(self, schema):
        return self._chosen_pagination.get_paginated_response_schema(schema)

    def to_html(self):  # pragma: no cover
        return self._chosen_pagination.to_html()

    def get_schema_fields(self, view):
        mode_field = coreapi.Field(
            name=self.pagination_mode_param,
            required=False,
            location='query',
            schema=coreschema.Enum(
                title='Pagination Mode',
                description=force_str(self.pagination_mode_description),
                enum=[self.limit_offset_key, self.cursor_pagination_key],
            )
        )
        return [mode_field] \
            + self._limit_offset_pagination.get_schema_fields(view) \
            + self._cursor_pagination.get_schema_fields(view)[:1]  # "limit" is shared between the two modes

    def get_schema_operation_parameters(self, view):
        return self._chosen_pagination.get_schema_operation_parameters(view)
