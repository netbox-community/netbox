__all__ = (
    'htmx_partial',
)


def htmx_partial(request):
    """
    Determines whether to render partial (versus complete) HTML content
    in response to an HTMX request, based on the target element.
    """
    return request.htmx and not request.htmx.boosted
