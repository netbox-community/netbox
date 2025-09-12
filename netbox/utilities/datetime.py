import datetime

from django.utils import timezone
from django.utils.timezone import localtime

__all__ = (
    'datetime_from_timestamp',
    'local_now',
)


def local_now():
    """
    Return the current date & time in the system timezone.
    """
    return localtime(timezone.now())


def datetime_from_timestamp(value):
    """
    Convert an ISO 8601 or RFC 3339 timestamp to a datetime object.
    """
    return datetime.datetime.fromisoformat(value)
