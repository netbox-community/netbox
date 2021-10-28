from django.db.models import QuerySet
from rest_framework.pagination import LimitOffsetPagination

from netbox.config import get_config


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
            self.count = queryset.count()
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
