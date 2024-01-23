from netaddr import AddrFormatError, IPAddress
from urllib.parse import urlparse

__all__ = (
    'get_client_ip',
)


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
                raise ValueError(f"Invalid IP address set for {header}: {ip}")

    # Could not determine the client IP address from request headers
    return None
