import datetime
import json
from collections import OrderedDict

from django.core.serializers import serialize
from django.db.models import Count, OuterRef, Subquery
from django.http import QueryDict
from jinja2 import Environment

from dcim.choices import CableLengthUnitChoices
from extras.utils import is_taggable


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

        # Double-quote the value if it contains a comma
        if ',' in value or '\n' in value:
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


def get_subquery(model, field):
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

    return subquery


def serialize_object(obj, extra=None):
    """
    Return a generic JSON representation of an object using Django's built-in serializer. (This is used for things like
    change logging, not the REST API.) Optionally include a dictionary to supplement the object data.
    """
    json_str = serialize('json', [obj])
    data = json.loads(json_str)[0]['fields']

    # Include any custom fields
    if hasattr(obj, 'get_custom_fields'):
        data['custom_fields'] = {
            field: str(value) for field, value in obj.cf.items()
        }

    # Include any tags
    if is_taggable(obj):
        data['tags'] = [tag.name for tag in obj.tags.all()]

    # Append any extra data
    if extra is not None:
        data.update(extra)

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
    params = {}
    for field_name in getattr(instance, 'clone_fields', []):
        field = instance._meta.get_field(field_name)
        field_value = field.value_from_object(instance)

        # Swap out False with URL-friendly value
        if field_value is False:
            field_value = ''

        # Omit empty values
        if field_value not in (None, ''):
            params[field_name] = field_value

        # Copy tags
        if is_taggable(instance):
            params['tags'] = ','.join([t.name for t in instance.tags.all()])

    # Concatenate parameters into a URL query string
    param_string = '&'.join(
        ['{}={}'.format(k, v) for k, v in params.items()]
    )

    return param_string


def querydict_to_dict(querydict):
    """
    Convert a django.http.QueryDict object to a regular Python dictionary, preserving lists of multiple values.
    (QueryDict.dict() will return only the last value in a list for each key.)
    """
    assert isinstance(querydict, QueryDict)
    return {
        key: querydict.get(key) if len(value) == 1 and key != 'pk' else querydict.getlist(key)
        for key, value in querydict.lists()
    }


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
