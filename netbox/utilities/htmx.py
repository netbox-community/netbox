__all__ = (
    'htmx_partial',
)

PAGE_CONTAINER_ID = 'page-content'


def htmx_partial(request):
    """
    Determines whether to render partial (versus complete) HTML content
    in response to an HTMX request, based on the target element.
    """
    return request.htmx and request.htmx.target != PAGE_CONTAINER_ID
