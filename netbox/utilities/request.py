import warnings
from contextlib import ExitStack, contextmanager
from urllib.parse import urlparse

from django.utils.http import url_has_allowed_host_and_scheme
from django.utils.translation import gettext_lazy as _
from netaddr import AddrFormatError, IPAddress

from netbox.registry import registry
from .constants import HTTP_REQUEST_META_SAFE_COPY

__all__ = (
    'NetBoxFakeRequest',
    'apply_request_processors',
    'copy_safe_request',
    'get_client_ip',
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

def copy_safe_request(request):
    """
    Copy selected attributes from a request object into a new fake request object. This is needed in places where
    thread safe pickling of the useful request data is needed.
    """
    meta = {
        k: request.META[k]
        for k in HTTP_REQUEST_META_SAFE_COPY
        if k in request.META and isinstance(request.META[k], str)
    }
    return NetBoxFakeRequest({
        'META': meta,
        'COOKIES': request.COOKIES,
        'POST': request.POST,
        'GET': request.GET,
        'FILES': request.FILES,
        'user': request.user,
        'method': request.method,
        'path': request.path,
        'id': getattr(request, 'id', None),  # UUID assigned by middleware
    })


def get_client_ip(request, additional_headers=()):
    """
    Return the client (source) IP address of the given request.
    """
    HTTP_HEADERS = (
        'HTTP_X_REAL_IP',
        'HTTP_X_FORWARDED_FOR',
        'REMOTE_ADDR',
        *additional_headers
    )
    for header in HTTP_HEADERS:
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
