def is_htmx(request):
    """
    Returns True if the request was made by HTMX; False otherwise.
    """
    return 'Hx-Request' in request.headers
