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
            MAX_PAGE_SIZE = get_config().MAX_PAGE_SIZE
            if MAX_PAGE_SIZE:
                MAX_PAGE_SIZE = max(MAX_PAGE_SIZE, self.default_limit)
            try:
                limit = int(request.query_params[self.limit_query_param])
                if limit < 0:
                    raise ValueError()
                # Enforce maximum page size, if defined
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


class StripCountAnnotationsPaginator(OptionalLimitOffsetPagination):
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
