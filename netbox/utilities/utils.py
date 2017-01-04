def csv_format(data):
    """
    Encapsulate any data which contains a comma within double quotes.
    """
    csv = []
    for d in data:
        if d in [None, False]:
            csv.append(u'')
        elif type(d) not in (str, unicode):
            csv.append(u'{}'.format(d))
        elif u',' in d:
            csv.append(u'"{}"'.format(d))
        else:
            csv.append(d)
    return u','.join(csv)
