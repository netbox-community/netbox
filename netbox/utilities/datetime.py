from django.utils import timezone
from django.utils.timezone import localtime

__all__ = (
    'local_now',
)


def local_now():
    """
    Return the current date & time in the system timezone.
    """
    return localtime(timezone.now())
