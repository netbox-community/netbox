from urllib.parse import urlencode

from django.http import QueryDict
from django.utils.datastructures import MultiValueDict
from netbox.models import CloningMixin

__all__ = (
    'dict_to_querydict',
    'normalize_querydict',
    'prepare_cloned_fields',
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


def prepare_cloned_fields(instance):
    """
    Generate a QueryDict comprising attributes from an object's clone() method.
    """
    # Generate the clone attributes from the instance
    if not issubclass(type(instance), CloningMixin):
        return QueryDict(mutable=True)
    attrs = instance.clone()

    # Prepare QueryDict parameters
    params = []
    for key, value in attrs.items():
        if type(value) in (list, tuple):
            params.extend([(key, v) for v in value])
        elif value is not False and value is not None:
            params.append((key, value))
        else:
            params.append((key, ''))

    # Return a QueryDict with the parameters
    return QueryDict(urlencode(params), mutable=True)
