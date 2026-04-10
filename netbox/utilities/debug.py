from django.conf import settings
from django.http import HttpRequest

__all__ = (
    'show_toolbar',
)


def show_toolbar(request: HttpRequest) -> bool:
    """
    Override django-debug-toolbar's default display conditions to allow for an empty INTERNAL_IPS.
    """
    if not settings.DEBUG:
        return False

    # If no internal IPs have been defined, enable the toolbar
    if not settings.INTERNAL_IPS:
        return True

    # If the request is from an internal IP, enable the toolbar
    if request.META.get('REMOTE_ADDR') in settings.INTERNAL_IPS:
        return True

    return False
