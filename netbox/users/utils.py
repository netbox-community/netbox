from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from social_core.storage import NO_ASCII_REGEX, NO_SPECIAL_REGEX

__all__ = (
    'clean_username',
    'get_current_pepper',
)


def clean_username(value):
    """Clean username removing any unsupported character"""
    value = NO_ASCII_REGEX.sub('', value)
    value = NO_SPECIAL_REGEX.sub('', value)
    value = value.replace(':', '')
    return value


def get_current_pepper():
    """
    Return the ID and value of the newest (highest ID) cryptographic pepper.
    """
    if len(settings.API_TOKEN_PEPPERS) < 1:
        raise ImproperlyConfigured("Must define API_TOKEN_PEPPERS to use v2 API tokens")
    newest_id = sorted(settings.API_TOKEN_PEPPERS)[-1]
    return newest_id, settings.API_TOKEN_PEPPERS[newest_id]
