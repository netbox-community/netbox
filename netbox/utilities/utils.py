import datetime
import json
from collections import OrderedDict
from itertools import count, groupby

from django.core.serializers import serialize
from django.db.models import Count, OuterRef, Subquery
from django.db.models.functions import Coalesce
from jinja2 import Environment
from mptt.models import MPTTModel

from dcim.choices import CableLengthUnitChoices
from extras.utils import is_taggable
from utilities.constants import HTTP_REQUEST_META_SAFE_COPY


def csv_format(data):
    """
    Encapsulate any data which contains a comma within double quotes.
    """
    csv = []
    for value in data:

        # Represent None or False with empty string
        if value is None or value is False:
            csv.append('')
            continue

        # Convert dates to ISO format
        if isinstance(value, (datetime.date, datetime.datetime)):
            value = value.isoformat()

        # Force conversion to string first so we can check for any commas
        if not isinstance(value, str):
            value = '{}'.format(value)

        # Double-quote the value if it contains a comma or line break
        if ',' in value or '\n' in value:
            value = value.replace('"', '""')  # Escape double-quotes
            csv.append('"{}"'.format(value))
        else:
            csv.append('{}'.format(value))

    return ','.join(csv)


def foreground_color(bg_color):
    """
    Return the ideal foreground color (black or white) for a given background color in hexadecimal RGB format.
    """
    bg_color = bg_color.strip('#')
    r, g, b = [int(bg_color[c:c + 2], 16) for c in (0, 2, 4)]
    if r * 0.299 + g * 0.587 + b * 0.114 > 186:
        return '000000'
    else:
        return 'ffffff'


def dynamic_import(name):
    """
    Dynamically import a class from an absolute path string
    """
    components = name.split('.')
    mod = __import__(components[0])
    for comp in components[1:]:
        mod = getattr(mod, comp)
    return mod


def count_related(model, field):
    """
    Return a Subquery suitable for annotating a child object count.
    """
    subquery = Subquery(
        model.objects.filter(
            **{field: OuterRef('pk')}
        ).order_by().values(
            field
        ).annotate(
            c=Count('*')
        ).values('c')
    )

    return Coalesce(subquery, 0)


def serialize_object(obj, extra=None):
    """
    Return a generic JSON representation of an object using Django's built-in serializer. (This is used for things like
    change logging, not the REST API.) Optionally include a dictionary to supplement the object data. A list of keys
    can be provided to exclude them from the returned dictionary. Private fields (prefaced with an underscore) are
    implicitly excluded.
    """
    json_str = serialize('json', [obj])
    data = json.loads(json_str)[0]['fields']

    # Exclude any MPTTModel fields
    if issubclass(obj.__class__, MPTTModel):
        for field in ['level', 'lft', 'rght', 'tree_id']:
            data.pop(field)

    # Include custom_field_data as "custom_fields"
    if hasattr(obj, 'custom_field_data'):
        data['custom_fields'] = data.pop('custom_field_data')

    # Include any tags. Check for tags cached on the instance; fall back to using the manager.
    if is_taggable(obj):
        tags = getattr(obj, '_tags', None) or obj.tags.all()
        data['tags'] = [tag.name for tag in tags]

    # Append any extra data
    if extra is not None:
        data.update(extra)

    # Copy keys to list to avoid 'dictionary changed size during iteration' exception
    for key in list(data):
        # Private fields shouldn't be logged in the object change
        if isinstance(key, str) and key.startswith('_'):
            data.pop(key)

    return data


def dict_to_filter_params(d, prefix=''):
    """
    Translate a dictionary of attributes to a nested set of parameters suitable for QuerySet filtering. For example:

        {
            "name": "Foo",
            "rack": {
                "facility_id": "R101"
            }
        }

    Becomes:

        {
            "name": "Foo",
            "rack__facility_id": "R101"
        }

    And can be employed as filter parameters:

        Device.objects.filter(**dict_to_filter(attrs_dict))
    """
    params = {}
    for key, val in d.items():
        k = prefix + key
        if isinstance(val, dict):
            params.update(dict_to_filter_params(val, k + '__'))
        else:
            params[k] = val
    return params


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


def deepmerge(original, new):
    """
    Deep merge two dictionaries (new into original) and return a new dict
    """
    merged = OrderedDict(original)
    for key, val in new.items():
        if key in original and isinstance(original[key], dict) and isinstance(val, dict):
            merged[key] = deepmerge(original[key], val)
        else:
            merged[key] = val
    return merged


def to_meters(length, unit):
    """
    Convert the given length to meters.
    """
    length = int(length)
    if length < 0:
        raise ValueError("Length must be a positive integer")

    valid_units = CableLengthUnitChoices.values()
    if unit not in valid_units:
        raise ValueError(
            "Unknown unit {}. Must be one of the following: {}".format(unit, ', '.join(valid_units))
        )

    if unit == CableLengthUnitChoices.UNIT_METER:
        return length
    if unit == CableLengthUnitChoices.UNIT_CENTIMETER:
        return length / 100
    if unit == CableLengthUnitChoices.UNIT_FOOT:
        return length * 0.3048
    if unit == CableLengthUnitChoices.UNIT_INCH:
        return length * 0.3048 * 12
    raise ValueError("Unknown unit {}. Must be 'm', 'cm', 'ft', or 'in'.".format(unit))


def render_jinja2(template_code, context):
    """
    Render a Jinja2 template with the provided context. Return the rendered content.
    """
    return Environment().from_string(source=template_code).render(**context)


def prepare_cloned_fields(instance):
    """
    Compile an object's `clone_fields` list into a string of URL query parameters. Tags are automatically cloned where
    applicable.
    """
    params = []
    for field_name in getattr(instance, 'clone_fields', []):
        field = instance._meta.get_field(field_name)
        field_value = field.value_from_object(instance)

        # Pass False as null for boolean fields
        if field_value is False:
            params.append((field_name, ''))

        # Omit empty values
        elif field_value not in (None, ''):
            params.append((field_name, field_value))

    # Copy tags
    if is_taggable(instance):
        for tag in instance.tags.all():
            params.append(('tags', tag.pk))

    # Concatenate parameters into a URL query string
    param_string = '&'.join([f'{k}={v}' for k, v in params])

    return param_string


def shallow_compare_dict(source_dict, destination_dict, exclude=None):
    """
    Return a new dictionary of the different keys. The values of `destination_dict` are returned. Only the equality of
    the first layer of keys/values is checked. `exclude` is a list or tuple of keys to be ignored.
    """
    difference = {}

    for key in destination_dict:
        if source_dict.get(key) != destination_dict[key]:
            if isinstance(exclude, (list, tuple)) and key in exclude:
                continue
            difference[key] = destination_dict[key]

    return difference


def flatten_dict(d, prefix='', separator='.'):
    """
    Flatten netsted dictionaries into a single level by joining key names with a separator.

    :param d: The dictionary to be flattened
    :param prefix: Initial prefix (if any)
    :param separator: The character to use when concatenating key names
    """
    ret = {}
    for k, v in d.items():
        key = separator.join([prefix, k]) if prefix else k
        if type(v) is dict:
            ret.update(flatten_dict(v, prefix=key))
        else:
            ret[key] = v
    return ret


# Taken from django.utils.functional (<3.0)
def curry(_curried_func, *args, **kwargs):
    def _curried(*moreargs, **morekwargs):
        return _curried_func(*args, *moreargs, **{**kwargs, **morekwargs})
    return _curried


def array_to_string(array):
    """
    Generate an efficient, human-friendly string from a set of integers. Intended for use with ArrayField.
    For example:
        [0, 1, 2, 10, 14, 15, 16] => "0-2, 10, 14-16"
    """
    group = (list(x) for _, x in groupby(sorted(array), lambda x, c=count(): next(c) - x))
    return ', '.join('-'.join(map(str, (g[0], g[-1])[:len(g)])) for g in group)


def content_type_name(contenttype):
    """
    Return a proper ContentType name.
    """
    meta = contenttype.model_class()._meta
    return f'{meta.app_config.verbose_name} > {meta.verbose_name}'


#
# Fake request object
#

class NetBoxFakeRequest:
    """
    A fake request object which is explicitly defined at the module level so it is able to be pickled. It simply
    takes what is passed to it as kwargs on init and sets them as instance variables.
    """
    def __init__(self, _dict):
        self.__dict__ = _dict


def copy_safe_request(request):
    """
    Copy selected attributes from a request object into a new fake request object. This is needed in places where
    thread safe pickling of the useful request data is needed.
    """
    meta = {
        k: request.META[k]
        for k in HTTP_REQUEST_META_SAFE_COPY
        if k in request.META and isinstance(request.META[k], str)
    }
    return NetBoxFakeRequest({
        'META': meta,
        'POST': request.POST,
        'GET': request.GET,
        'FILES': request.FILES,
        'user': request.user,
        'path': request.path,
        'id': getattr(request, 'id', None),  # UUID assigned by middleware
    })
