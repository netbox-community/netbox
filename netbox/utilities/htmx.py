from urllib.parse import urlsplit

from django.http import HttpResponse
from django.urls import reverse

__all__ = (
    'htmx_current_url',
    'htmx_maybe_redirect_current_page',
    'htmx_partial',
)


def htmx_partial(request):
    """
    Determines whether to render partial (versus complete) HTML content
    in response to an HTMX request, based on the target element.
    """
    return request.htmx and not request.htmx.boosted


def htmx_current_url(request) -> str:
    """
    Extracts the current URL from the HTMX-specific headers in the given request object.

    This function checks for the `HX-Current-URL` header in the request's headers
    and `HTTP_HX_CURRENT_URL` in the META data of the request. It preferentially
    chooses the value present in the `HX-Current-URL` header and falls back to the
    `HTTP_HX_CURRENT_URL` META data if the former is unavailable. If neither value
    exists, it returns an empty string.
    """
    return request.headers.get('HX-Current-URL') or request.META.get('HTTP_HX_CURRENT_URL', '') or ''


def htmx_maybe_redirect_current_page(
    request, url_name: str, *, preserve_query: bool = True, status: int = 200
) -> HttpResponse | None:
    """
    Redirects the current page in an HTMX request if conditions are met.

    This function checks whether a request is an HTMX partial request and if the
    current URL matches the provided target URL. If the conditions are met, it
    returns an HTTP response signaling a redirect to the provided or updated target
    URL. Otherwise, it returns None.
    """
    if not htmx_partial(request):
        return None

    current = urlsplit(htmx_current_url(request))
    target_path = reverse(url_name)  # will raise NoReverseMatch if misconfigured

    if current.path.rstrip('/') != target_path.rstrip('/'):
        return None

    redirect_to = target_path
    if preserve_query and current.query:
        redirect_to = f'{target_path}?{current.query}'

    resp = HttpResponse(status=status)
    resp['HX-Redirect'] = redirect_to
    return resp
