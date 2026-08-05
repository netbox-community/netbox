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
    0.43s). A negative duration is rendered with a leading minus sign, so that an anomalous value
    remains recognizable as one. Returns an empty string for None; zero renders as "0s".
    """
    if value is None:
        return ''

    total_seconds = value.total_seconds()
    magnitude = abs(total_seconds)

    # Render sub-second durations to the millisecond, as rounding them to whole seconds would
    # report every short-lived duration as zero. Trailing zeros are stripped.
    if 0 < magnitude < 1:
        rendered = f'{magnitude:.3f}'.rstrip('0').rstrip('.')
        # A magnitude below a millisecond has no representation here, so fall through to "0s".
        # Rounding up to a whole second (e.g. 0.9996) likewise falls through, to "1s".
        if rendered not in ('0', '1'):
            return f'-{rendered}s' if total_seconds < 0 else f'{rendered}s'

    # Round to whole seconds and decompose
    days, remainder = divmod(round(magnitude), 86400)
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
    ret = ret.strip()

    # Zero carries no sign, however the original value was signed
    if total_seconds < 0 and ret != '0s':
        ret = f'-{ret}'
    return ret


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
