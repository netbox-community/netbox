import logging
from django.http import QueryDict
from django.utils.translation import gettext_lazy as _
from netaddr import AddrFormatError, IPAddress
from urllib.parse import urlparse
from .constants import HTTP_REQUEST_META_SAFE_COPY, HTTP_REQUEST_J2_SAFE_COPY

__all__ = (
    'NetBoxFakeRequest',
    'copy_safe_request',
    'get_client_ip',
)

logger = logging.getLogger('netbox.utilities.request')

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
        'path': request.path,
        'id': getattr(request, 'id', None),  # UUID assigned by middleware
    })


def make_request_safe_j2(request):
    """
    Return a copy of the request object with only safe attributes.
    """
    try:
        q = QueryDict(request.META["QUERY_STRING"])
        q_dict = q.dict()
        dict_return = {"request_query": q_dict,
                    "path": request.path,
                    "query_string": request.META["QUERY_STRING"]}
        for attr in HTTP_REQUEST_J2_SAFE_COPY:
            if hasattr(request, attr):
                dict_return[attr] = getattr(request, attr, None)
        return dict_return
    except Exception as e:
        logger.debug(f"Could not make request safe for Jinja2: {e}")
        return {}


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
