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
                'ipam.Aggregate',
                'ipam.Prefix',
                'ipam.IPRange',
                'ipam.IPAddress',
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
                'dcim.Site',
                'dcim.Rack',
                'dcim.Device',
                'dcim.Cable',
            ]
        }
    },
    {
        'widget': 'extras.StaticContentWidget',
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
