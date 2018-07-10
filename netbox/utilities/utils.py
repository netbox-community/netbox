from __future__ import unicode_literals

import datetime
import json
import six

from django.core.serializers import serialize
from django.http import HttpResponse


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
        if not isinstance(value, six.string_types):
            value = '{}'.format(value)

        # Double-quote the value if it contains a comma
        if ',' in value or '\n' in value:
            csv.append('"{}"'.format(value))
        else:
            csv.append('{}'.format(value))

    return ','.join(csv)


def queryset_to_csv(queryset):
    """
    Export a queryset of objects as CSV, using the model's to_csv() method.
    """
    output = []

    # Start with the column headers
    headers = ','.join(queryset.model.csv_headers)
    output.append(headers)

    # Iterate through the queryset
    for obj in queryset:
        data = csv_format(obj.to_csv())
        output.append(data)

    # Build the HTTP response
    response = HttpResponse(
        '\n'.join(output),
        content_type='text/csv'
    )
    filename = 'netbox_{}.csv'.format(queryset.model._meta.verbose_name_plural)
    response['Content-Disposition'] = 'attachment; filename="{}"'.format(filename)

    return response


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
