import decimal
from itertools import count, groupby

__all__ = (
    'array_to_ranges',
    'array_to_string',
    'deepmerge',
    'drange',
    'flatten_dict',
    'deep_compare_dict',
    'make_diff',
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

#
# String utilities
#
def regular_line_ending(s: str):
    if s.endswith(","):
        return True
    return not (s.endswith("{") or s.endswith("["))


def begin_of_complex(s: str):
    return s.endswith("[") or s.endswith("{")


def has_indent(s: str, indent: str):
    return not s.removeprefix(indent).startswith(" ")


def extract_key(s: str):
    if '": ' not in s:
        return None
    idx = s.find(': ')
    substr = s[:idx].replace('"', '').strip()
    return substr

def make_diff(old: str, new: str):
    old_lines = old.splitlines(False)
    new_lines = new.splitlines(False)
    old_list: list[tuple[str, bool]] = []
    new_list: list[tuple[str, bool]] = []
    old_idx = 0
    new_idx = 0
    while True:
        if old_idx == len(old_lines) and new_idx == len(new_lines):
            break
        if old_idx == len(old_lines):
            while new_idx != len(new_lines):
                new_list.append((new_lines[new_idx], True))
                old_list.append(("", False))
                new_idx += 1
            break
        if new_idx == len(new_lines):
            while old_idx != len(old_lines):
                old_list.append((old_lines[old_idx], True))
                new_list.append(("", False))
                old_idx += 1
            break
        old_s = old_lines[old_idx]
        old_idx += 1
        old_k = extract_key(old_s)
        new_s = new_lines[new_idx]
        new_k = extract_key(new_s)
        new_idx += 1
        # Handle additions of keys
        if old_k is not None and new_k is not None and old_k != new_k:
            print("Found mismatch:", old_k, new_k)
            found_it = False
            for old_idx2 in range(old_idx, len(old_lines)):
                old_s2 = old_lines[old_idx2]
                old_k2 = extract_key(old_s2)
                print(">>", old_k2, new_k)
                if old_k2 == new_k:
                    print("Found it", old_k2, old_idx2, new_k)
                    old_list.append((old_s, False))
                    new_list.append(("  <O>", False))
                    old_s = "" if old_idx >= len(old_lines) else old_lines[old_idx]
                    for _ in range(old_idx + 1, old_idx2 + 1):
                        old_s = "" if old_idx >= len(old_lines) else old_lines[old_idx]
                        new_list.append(("  <<OLDFILLER>", False))
                        old_list.append((old_s, True))
                        old_idx += 1
                    old_list.append((old_s, False))
                    new_list.append((new_s, False))
                    old_idx += 1
                    found_it = True
                    break
            if found_it:
                continue
            for new_idx2 in range(new_idx, len(new_lines)):
                new_s2 = new_lines[new_idx2]
                new_k2 = extract_key(new_s2)
                print(">>22", old_k, new_k2)
                if new_k2 == old_k:
                    print("NEW Found it", new_k2, new_idx2, old_k)
                    old_list.append(("  <N>", False))
                    new_list.append((new_s, False))
                    new_s = "" if new_idx >= len(new_lines) else new_lines[new_idx]
                    for _ in range(new_idx + 1, new_idx2 + 1):
                        new_s = "" if new_idx >= len(new_lines) else new_lines[new_idx]
                        old_list.append(("  <<NEWFILLER>", False))
                        new_idx += 1
                        new_list.append((new_s, True))
                    old_list.append((old_s, False))
                    new_list.append((new_s, False))
                    new_idx += 1
                    found_it = True
                    break
            continue
        if "{" == old_s.strip() and "{" == new_s.strip():
            old_list.append(("{", False))
            new_list.append(("{", False))
            continue
        if "}" == old_s.strip() and "}" == new_s.strip():
            old_list.append(("}", False))
            new_list.append(("}", False))
            continue
        # Handle:
        #  "foo": null    "foo": [
        #                     "bar",
        #                     "baz",
        #                 "]"
        if regular_line_ending(old_s) and begin_of_complex(new_s):
            indent_of_new = new_s.replace(new_s.strip(), "")
            new_list.append((new_s, True))
            old_list.append((old_s, True))
            while not has_indent(new_lines[new_idx], indent_of_new):
                old_list.append(("", True))
                new_list.append((new_lines[new_idx], True))
                new_idx += 1
            old_list.append(("", True))
            new_list.append((new_lines[new_idx], True))
            new_idx += 1
            continue
        # Handle:
        # "foo": {         "foo": null
        #   "foo": "bar"
        # }
        if begin_of_complex(old_s) and regular_line_ending(new_s):
            indent_of_old = old_s.replace(old_s.strip(), "")
            old_list.append((old_s, True))
            new_list.append((new_s, True))
            while not has_indent(old_lines[old_idx], indent_of_old):
                new_list.append(("", True))
                old_list.append((old_lines[old_idx], True))
                old_idx += 1
            new_list.append(("", True))
            old_list.append((old_lines[old_idx], True))
            old_idx += 1
            continue
        if begin_of_complex(old_s) and begin_of_complex(new_s):
            indent_of_old = old_s.replace(old_s.strip(), "")
            indent_of_new = new_s.replace(new_s.strip(), "")
            old_list.append((old_s, False))
            new_list.append((new_s, False))
            old_tmp = []
            new_tmp = []
            while not has_indent(old_lines[old_idx], indent_of_old):
                old_tmp.append(old_lines[old_idx])
                old_idx += 1
            while not has_indent(new_lines[new_idx], indent_of_new):
                new_tmp.append(new_lines[new_idx])
                new_idx += 1
            a, b = make_diff("\n".join(old_tmp), "\n".join(new_tmp))
            assert len(a) == len(b)
            old_list += a
            new_list += b
            old_list.append((old_lines[old_idx], False))
            old_idx += 1
            new_list.append((new_lines[new_idx], False))
            new_idx += 1
            continue
        if old_s == new_s:
            old_list.append((old_s, False))
            new_list.append((new_s, False))
            continue
        # Handle:
        # "foo": 1(,)  "foo": 2(,)
        if regular_line_ending(old_s) and regular_line_ending(new_s):
            old_list.append((old_s, True))
            new_list.append((new_s, True))
            continue
    print(len(old_list), len(new_list))
    assert len(old_list) == len(new_list)
    return old_list, new_list