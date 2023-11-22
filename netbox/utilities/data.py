import decimal
from itertools import count, groupby

__all__ = (
    'array_to_ranges',
    'array_to_string',
    'deepmerge',
    'drange',
    'flatten_dict',
    'deep_compare_dict',
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


def deep_compare_dict(old, new, exclude=tuple()):
    """
    Return a tuple of two dictionaries `(removed_diffs, added_diffs)` in a format
    that is compatible with the requirements of `ObjectChangeView`.
    `exclude` is a list or tuple of keys to be ignored.
    """
    added_diffs = {}
    removed_diffs = {}

    for key in old:
        if key in exclude:
            continue

        old_data = old[key]
        new_data = new[key]

        if old_data != new_data:
            if isinstance(old_data, dict) and isinstance(new_data, dict):
                (sub_added, sub_removed) = deep_compare_dict(old_data, new_data, exclude=exclude)
                if len(sub_removed) > 0:
                    removed_diffs[key] = sub_removed
                if len(sub_added) > 0:
                    added_diffs[key] = sub_added
            else:
                removed_diffs[key] = old_data
                added_diffs[key] = new_data

    return added_diffs, removed_diffs


#
# Array utilities
#

def array_to_ranges(array):
    """
    Convert an arbitrary array of integers to a list of consecutive values. Nonconsecutive values are returned as
    single-item tuples. For example:
        [0, 1, 2, 10, 14, 15, 16] => [(0, 2), (10,), (14, 16)]"
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
    For example:
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
