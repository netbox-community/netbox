from __future__ import unicode_literals

import datetime
import six

from django.http import HttpResponse


def csv_format(data):
    """
    Encapsulate any data which contains a comma within double quotes.
    """
    csv = []
    for value in data:

        # Represent None or False with empty string
        if value in [None, False]:
            csv.append('')
            continue

        # Convert dates to ISO format
        if isinstance(value, (datetime.date, datetime.datetime)):
            value = value.isoformat()

        # Force conversion to string first so we can check for any commas
        if not isinstance(value, six.string_types):
            value = '{}'.format(value)

        # Double-quote the value if it contains a comma
        if ',' in value:
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
