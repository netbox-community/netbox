from django.contrib.contenttypes.models import ContentType

# Webhook content types
HTTP_CONTENT_TYPE_JSON = 'application/json'

# Dashboard
DEFAULT_DASHBOARD = [
    {
        'widget': 'extras.ObjectCountsWidget',
        'width': 4,
        'height': 3,
        'title': 'IPAM',
        'config': {
            'models': [
                ContentType.objects.get_by_natural_key('ipam', 'aggregate').pk,
                ContentType.objects.get_by_natural_key('ipam', 'prefix').pk,
                ContentType.objects.get_by_natural_key('ipam', 'ipaddress').pk,
            ]
        }
    },
    {
        'widget': 'extras.ObjectCountsWidget',
        'width': 4,
        'height': 3,
        'title': 'DCIM',
        'config': {
            'models': [
                ContentType.objects.get_by_natural_key('dcim', 'site').pk,
                ContentType.objects.get_by_natural_key('dcim', 'rack').pk,
                ContentType.objects.get_by_natural_key('dcim', 'device').pk,
            ]
        }
    },
    {
        'widget': 'extras.NoteWidget',
        'width': 4,
        'height': 3,
        'config': {
            'content': 'Welcome to **NetBox**!'
        }
    },
    {
        'widget': 'extras.ChangeLogWidget',
        'width': 12,
        'height': 6,
    },
]
