import re

__all__ = (
    'enum_key',
    'humanize_duration',
    'remove_linebreaks',
    'title',
    'trailing_slash',
)


def humanize_duration(value):
    """
    Express a timedelta in a human-friendly format. Example: 1h 5m 23s. Durations of a second or
    more are rounded to whole seconds; shorter durations are rounded to the millisecond (e.g.
    0.43s). Returns an empty string for None; zero and negative durations render as "0s".
    """
    if value is None:
        return ''

    # Negative durations (which can result from clock skew) are clamped to zero
    total_seconds = max(value.total_seconds(), 0)

    # Render sub-second durations to the millisecond, as rounding them to whole seconds would
    # report every short-lived duration as zero. Trailing zeros are stripped.
    if 0 < total_seconds < 1:
        milliseconds = f'{total_seconds:.3f}'.rstrip('0').rstrip('.')
        if milliseconds != '0':
            return f'{milliseconds}s'

    # Round to whole seconds and decompose
    days, remainder = divmod(round(total_seconds), 86400)
    hours, remainder = divmod(remainder, 3600)
    minutes, seconds = divmod(remainder, 60)

    ret = ''
    if days:
        ret += f'{days}d '
    if hours:
        ret += f'{hours}h '
    if minutes:
        ret += f'{minutes}m '
    if seconds or not ret:
        ret += f'{seconds}s'
    return ret.strip()


def enum_key(value):
    """
    Convert the given value to a string suitable for use as an Enum key.
    """
    value = str(value).upper()
    return re.sub(r'[^_A-Z0-9]', '_', value)


def remove_linebreaks(value):
    """
    Remove all line breaks from a string and return the result. Useful for log sanitization purposes.
    """
    return value.replace('\n', '').replace('\r', '')


def title(value):
    """
    Improved implementation of str.title(); retains all existing uppercase letters.
    """
    return ' '.join([w[0].upper() + w[1:] for w in str(value).split()])


def trailing_slash(value):
    """
    Remove a leading slash (if any) and include a trailing slash, except for empty strings.
    """
    return f'{value.strip("/")}/' if value else ''
