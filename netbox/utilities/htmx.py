from urllib.parse import urlparse

__all__ = (
    'is_embedded',
)


def is_embedded(request):
    """
    Returns True if the request indicates that it originates from a URL different from
    the path being requested.
    """
    hx_current_url = request.headers.get('HX-Current-URL', None)
    if not hx_current_url:
        return False
    return request.path != urlparse(hx_current_url).path
