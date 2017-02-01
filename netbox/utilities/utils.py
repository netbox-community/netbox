import six


def csv_format(data):
    """
    Encapsulate any data which contains a comma within double quotes.
    """
    csv = []
    for value in data:

        # Represent None or False with empty string
        if value in [None, False]:
            csv.append(u'')
            continue

        # Force conversion to string first so we can check for any commas
        if not isinstance(value, six.string_types):
            value = u'{}'.format(value)

        # Double-quote the value if it contains a comma
        if u',' in value:
            csv.append(u'"{}"'.format(value))
        else:
            csv.append(u'{}'.format(value))

    return u','.join(csv)
