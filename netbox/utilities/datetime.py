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
    # Work around UTC issue for Python < 3.11; see
    # https://docs.python.org/3/library/datetime.html#datetime.datetime.fromisoformat
    # TODO: Remove this once Python 3.10 is no longer supported
    if type(value) is str and value.endswith('Z'):
        value = f'{value[:-1]}+00:00'
    return datetime.datetime.fromisoformat(value)
