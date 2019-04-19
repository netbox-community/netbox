from collections import OrderedDict

import datetime
import json

from django.core.serializers import serialize
from django.db.models import Count, OuterRef, Subquery

from dcim.constants import LENGTH_UNIT_CENTIMETER, LENGTH_UNIT_FOOT, LENGTH_UNIT_INCH, LENGTH_UNIT_METER


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


def model_names_to_filter_dict(names):
    """
    Accept a list of content types in the format ['<app>.<model>', '<app>.<model>', ...] and return a dictionary
    suitable for QuerySet filtering.
    """
    # TODO: This should match on the app_label as well as the model name to avoid potential duplicate names
    return {
        'model__in': [model.split('.')[1] for model in names],
    }


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
            field.name: str(value) for field, value in obj.get_custom_fields().items()
        }

    # Include any tags
    if hasattr(obj, 'tags'):
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
    if unit == LENGTH_UNIT_METER:
        return length
    if unit == LENGTH_UNIT_CENTIMETER:
        return length / 100
    if unit == LENGTH_UNIT_FOOT:
        return length * 0.3048
    if unit == LENGTH_UNIT_INCH:
        return length * 0.3048 * 12
    raise ValueError("Unknown unit {}. Must be 'm', 'cm', 'ft', or 'in'.".format(unit))
