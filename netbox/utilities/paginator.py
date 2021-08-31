from django.conf import settings
from django.core.paginator import Paginator, Page


class EnhancedPaginator(Paginator):

    def __init__(self, object_list, per_page, orphans=None, **kwargs):

        # Determine the page size
        try:
            per_page = int(per_page)
            if per_page < 1:
                per_page = settings.PAGINATE_COUNT
        except ValueError:
            per_page = settings.PAGINATE_COUNT

        # Set orphans count based on page size
        if orphans is None and per_page <= 50:
            orphans = 5
        elif orphans is None:
            orphans = 10

        super().__init__(object_list, per_page, orphans=orphans, **kwargs)

    def _get_page(self, *args, **kwargs):
        return EnhancedPage(*args, **kwargs)


class EnhancedPage(Page):

    def smart_pages(self):

        # When dealing with five or fewer pages, simply return the whole list.
        if self.paginator.num_pages <= 5:
            return self.paginator.page_range

        # Show first page, last page, next/previous two pages, and current page
        n = self.number
        pages_wanted = [1, n - 2, n - 1, n, n + 1, n + 2, self.paginator.num_pages]
        page_list = sorted(set(self.paginator.page_range).intersection(pages_wanted))

        # Insert skip markers
        skip_pages = [x[1] for x in zip(page_list[:-1], page_list[1:]) if (x[1] - x[0] != 1)]
        for i in skip_pages:
            page_list.insert(page_list.index(i), False)

        return page_list


def get_paginate_count(request):
    """
    Determine the desired length of a page, using the following in order:

        1. per_page URL query parameter
        2. Saved user preference
        3. PAGINATE_COUNT global setting.

    Return the lesser of the calculated value and MAX_PAGE_SIZE.
    """
    if 'per_page' in request.GET:
        try:
            per_page = int(request.GET.get('per_page'))
            if request.user.is_authenticated:
                request.user.config.set('pagination.per_page', per_page, commit=True)
            return min(per_page, settings.MAX_PAGE_SIZE)
        except ValueError:
            pass

    if request.user.is_authenticated:
        per_page = request.user.config.get('pagination.per_page', settings.PAGINATE_COUNT)
        return min(per_page, settings.MAX_PAGE_SIZE)

    return min(settings.PAGINATE_COUNT, settings.MAX_PAGE_SIZE)
