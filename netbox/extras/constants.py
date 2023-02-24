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
                'ipam.aggregate',
                'ipam.prefix',
                'ipam.ipaddress',
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
                'dcim.site',
                'dcim.rack',
                'dcim.device',
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
