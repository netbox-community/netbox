import decimal
from itertools import count, groupby

from django.db.backends.postgresql.psycopg_any import NumericRange

__all__ = (
    'array_to_ranges',
    'array_to_string',
    'check_ranges_overlap',
    'deepmerge',
    'drange',
    'flatten_dict',
    'ranges_to_string',
    'ranges_to_string_list',
    'shallow_compare_dict',
    'string_to_ranges',
)


#
# Dictionary utilities
#

def deepmerge(original, new):
    """
    Deep merge two dictionaries (new into original) and return a new dict
    """
    merged = dict(original)
    for key, val in new.items():
        if key in original and isinstance(original[key], dict) and val and isinstance(val, dict):
            merged[key] = deepmerge(original[key], val)
        else:
            merged[key] = val
    return merged


def flatten_dict(d, prefix='', separator='.'):
    """
    Flatten nested dictionaries into a single level by joining key names with a separator.

    :param d: The dictionary to be flattened
    :param prefix: Initial prefix (if any)
    :param separator: The character to use when concatenating key names
    """
    ret = {}
    for k, v in d.items():
        key = separator.join([prefix, k]) if prefix else k
        if type(v) is dict:
            ret.update(flatten_dict(v, prefix=key, separator=separator))
        else:
            ret[key] = v
    return ret


def shallow_compare_dict(source_dict, destination_dict, exclude=tuple()):
    """
    Return a new dictionary of the different keys. The values of `destination_dict` are returned. Only the equality of
    the first layer of keys/values is checked. `exclude` is a list or tuple of keys to be ignored.
    """
    difference = {}

    for key, value in destination_dict.items():
        if key in exclude:
            continue
        if source_dict.get(key) != value:
            difference[key] = value

    return difference


#
# Array utilities
#

def array_to_ranges(array):
    """
    Convert an arbitrary array of integers to a list of consecutive values. Nonconsecutive values are returned as
    single-item tuples.

    Example:
        [0, 1, 2, 10, 14, 15, 16] => [(0, 2), (10,), (14, 16)]
    """
    group = (
        list(x) for _, x in groupby(sorted(array), lambda x, c=count(): next(c) - x)
    )
    return [
        (g[0], g[-1])[:len(g)] for g in group
    ]


def array_to_string(array):
    """
    Generate an efficient, human-friendly string from a set of integers. Intended for use with ArrayField.

    Example:
        [0, 1, 2, 10, 14, 15, 16] => "0-2, 10, 14-16"
    """
    ret = []
    ranges = array_to_ranges(array)
    for value in ranges:
        if len(value) == 1:
            ret.append(str(value[0]))
        else:
            ret.append(f'{value[0]}-{value[1]}')
    return ', '.join(ret)


#
# Range utilities
#

def drange(start, end, step=decimal.Decimal(1)):
    """
    Decimal-compatible implementation of Python's range()
    """
    start, end, step = decimal.Decimal(start), decimal.Decimal(end), decimal.Decimal(step)
    if start < end:
        while start < end:
            yield start
            start += step
    else:
        while start > end:
            yield start
            start += step


def check_ranges_overlap(ranges):
    """
    Check for overlap in an iterable of NumericRanges.
    """
    ranges.sort(key=lambda x: x.lower)

    for i in range(1, len(ranges)):
        prev_range = ranges[i - 1]
        prev_upper = prev_range.upper if prev_range.upper_inc else prev_range.upper - 1
        lower = ranges[i].lower if ranges[i].lower_inc else ranges[i].lower + 1
        if prev_upper >= lower:
            return True

    return False


def ranges_to_string_list(ranges):
    """
    Convert numeric ranges to a list of display strings.

    Each range is rendered as "lower-upper" or "lower" (for singletons).
    Bounds are normalized to inclusive values using ``lower_inc``/``upper_inc``.
    This underpins ``ranges_to_string()``, which joins the result with commas.

    Example:
        [NumericRange(1, 6), NumericRange(8, 9), NumericRange(10, 13)] => ["1-5", "8", "10-12"]
    """
    if not ranges:
        return []

    output: list[str] = []
    for r in ranges:
        # Compute inclusive bounds regardless of how the DB range is stored.
        lower = r.lower if r.lower_inc else r.lower + 1
        upper = r.upper if r.upper_inc else r.upper - 1
        output.append(f"{lower}-{upper}" if lower != upper else str(lower))
    return output


def ranges_to_string(ranges):
    """
    Converts a list of ranges into a string representation.

    This function takes a list of range objects and produces a string
    representation of those ranges. Each range is represented as a
    hyphen-separated pair of lower and upper bounds, with inclusive or
    exclusive bounds adjusted accordingly. If the lower and upper bounds
    of a range are the same, only the single value is added to the string.
    Intended for use with ArrayField.

    Example:
        [NumericRange(1, 5), NumericRange(8, 9), NumericRange(10, 12)] => "1-5,8,10-12"
    """
    if not ranges:
        return ''
    return ','.join(ranges_to_string_list(ranges))


def string_to_ranges(value):
    """
    Converts a string representation of numeric ranges into a list of NumericRange objects.

    This function parses a string containing numeric values and ranges separated by commas (e.g.,
    "1-5,8,10-12") and converts it into a list of NumericRange objects.
    In the case of a single integer, it is treated as a range where the start and end
    are equal. The returned ranges are represented as half-open intervals [lower, upper).
    Intended for use with ArrayField.

    Example:
        "1-5,8,10-12" => [NumericRange(1, 6), NumericRange(8, 9), NumericRange(10, 13)]
    """
    if not value:
        return None
    value.replace(' ', '')  # Remove whitespace
    values = []
    for data in value.split(','):
        dash_range = data.strip().split('-')
        if len(dash_range) == 1 and str(dash_range[0]).isdigit():
            # Single integer value; expand to a range
            lower = dash_range[0]
            upper = dash_range[0]
        elif len(dash_range) == 2 and str(dash_range[0]).isdigit() and str(dash_range[1]).isdigit():
            # The range has two values and both are valid integers
            lower = dash_range[0]
            upper = dash_range[1]
        else:
            return None
        values.append(NumericRange(int(lower), int(upper) + 1, bounds='[)'))
    return values
