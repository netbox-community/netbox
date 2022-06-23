from netaddr import IPAddress

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
            client_ip = request.META[header].split(',')[0]
            try:
                return IPAddress(client_ip)
            except ValueError:
                raise ValueError(f"Invalid IP address set for {header}: {client_ip}")

    # Could not determine the client IP address from request headers
    return None
