from django.conf import settings
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
    if not settings.API_TOKEN_PEPPERS:
        raise ValueError("API_TOKEN_PEPPERS is not defined")
    newest_id = sorted(settings.API_TOKEN_PEPPERS.keys())[-1]
    return newest_id, settings.API_TOKEN_PEPPERS[newest_id]
