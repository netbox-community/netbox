from django.http import QueryDict
from django.utils.datastructures import MultiValueDict

__all__ = (
    'dict_to_querydict',
    'normalize_querydict',
)


def dict_to_querydict(d, mutable=True):
    """
    Create a QueryDict instance from a regular Python dictionary.
    """
    qd = QueryDict(mutable=True)
    for k, v in d.items():
        item = MultiValueDict({k: v}) if isinstance(v, (list, tuple, set)) else {k: v}
        qd.update(item)
    if not mutable:
        qd._mutable = False
    return qd


def normalize_querydict(querydict):
    """
    Convert a QueryDict to a normal, mutable dictionary, preserving list values. For example,

        QueryDict('foo=1&bar=2&bar=3&baz=')

    becomes:

        {'foo': '1', 'bar': ['2', '3'], 'baz': ''}

    This function is necessary because QueryDict does not provide any built-in mechanism which preserves multiple
    values.
    """
    return {
        k: v if len(v) > 1 else v[0] for k, v in querydict.lists()
    }
