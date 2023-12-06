from netaddr import AddrFormatError, IPAddress

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
            # Check if the IP address is v6 or v4
            if ip.count(':') > 1:
                client_ip = ip
            else:
                client_ip = ip.partition(':')[0]
            try:
                return IPAddress(client_ip)
            except (AddrFormatError, ValueError):
                raise ValueError(f"Invalid IP address set for {header}: {client_ip}")

    # Could not determine the client IP address from request headers
    return None
