from social_core.storage import NO_ASCII_REGEX, NO_SPECIAL_REGEX


def clean_username(value):
    """Clean username removing any unsupported character"""
    value = NO_ASCII_REGEX.sub('', value)
    value = NO_SPECIAL_REGEX.sub('', value)
    value = value.replace(':', '')
    return value
