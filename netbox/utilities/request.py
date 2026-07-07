import warnings
from contextlib import ExitStack, contextmanager
from urllib.parse import urlparse

from django.conf import settings
from django.utils.datastructures import MultiValueDict
from django.utils.http import url_has_allowed_host_and_scheme
from django.utils.translation import gettext_lazy as _
from netaddr import AddrFormatError, IPAddress

from netbox.registry import registry

from .constants import HTTP_REQUEST_META_SAFE_COPY, HTTP_REQUEST_META_SENSITIVE

__all__ = (
    'NetBoxFakeRequest',
    'apply_request_processors',
    'copy_safe_request',
    'get_client_ip',
    'get_safe_request_context',
    'safe_for_redirect',
)


#
# Fake request object
#

class NetBoxFakeRequest:
    """
    A fake request object which is explicitly defined at the module level so it is able to be pickled. It simply
    takes what is passed to it as kwargs on init and sets them as instance variables.
    """
    def __init__(self, _dict):
        self.__dict__ = _dict


#
# Utility functions
#

def copy_safe_request(request, include_files=True):
    """
    Copy selected attributes from a request object into a new fake request object. This is needed in places where
    thread safe pickling of the useful request data is needed.

    Args:
        request: The original request object
        include_files: Whether to include request.FILES.
    """
    meta = {}
    for k, v in request.META.items():
        if not isinstance(v, str):
            continue
        if k in HTTP_REQUEST_META_SAFE_COPY:
            meta[k] = v
        elif k.startswith('HTTP_') and k not in HTTP_REQUEST_META_SENSITIVE:
            meta[k] = v
    data = {
        'META': meta,
        'COOKIES': request.COOKIES,
        'POST': request.POST,
        'GET': request.GET,
        'user': request.user,
        'method': request.method,
        'path': request.path,
        'path_info': request.path_info,
        'id': getattr(request, 'id', None),  # UUID assigned by middleware
    }
    if include_files:
        data['FILES'] = request.FILES
    else:
        data['FILES'] = MultiValueDict()

    return NetBoxFakeRequest(data)


def get_safe_request_context(request):
    """
    Return a sanitized subset of an HttpRequest suitable for exposure to user-authored templates
    (e.g. custom links). Excludes sensitive data such as cookies, headers, and session state. Returns a
    plain dict; Jinja2 resolves attribute access (e.g. request.path) against it via getitem fallback.
    """
    if request is None:
        return None
    return {
        'id': str(request.id) if hasattr(request, 'id') else None,  # UUID assigned by middleware
        'path': request.path,
        'path_info': request.path_info,
        'method': request.method,
        'GET': request.GET,
        'user': str(request.user),  # Username only; not the User instance
    }


def get_client_ip(request, additional_headers=()):
    """
    Return the client (source) IP address of the given request. Accepts an optional list of headers to inspect in
    addition to those configured under HTTP_CLIENT_IP_HEADERS.
    """
    headers = (
        *settings.HTTP_CLIENT_IP_HEADERS,
        *additional_headers,
    )
    for header in headers:
        if header in request.META:
            ip = request.META[header].split(',')[0].strip()
            try:
                return IPAddress(ip)
            except AddrFormatError:
                # Parse the string with urlparse() to remove port number or any other cruft
                ip = urlparse(f'//{ip}').hostname

            try:
                return IPAddress(ip)
            except AddrFormatError:
                # We did our best
                raise ValueError(_("Invalid IP address set for {header}: {ip}").format(header=header, ip=ip))

    # Could not determine the client IP address from request headers
    return None


def safe_for_redirect(url):
    """
    Returns True if the given URL is safe to use as an HTTP redirect; otherwise returns False.
    """
    return url_has_allowed_host_and_scheme(url, allowed_hosts=None)


@contextmanager
def apply_request_processors(request):
    """
    A context manager with applies all registered request processors (such as event_tracking).
    """
    with ExitStack() as stack:
        for request_processor in registry['request_processors']:
            try:
                stack.enter_context(request_processor(request))
            except Exception as e:
                warnings.warn(f'Failed to initialize request processor {request_processor.__name__}: {e}')
        yield
