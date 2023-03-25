# Events
EVENT_CREATE = 'create'
EVENT_UPDATE = 'update'
EVENT_DELETE = 'delete'
EVENT_JOB_START = 'job_start'
EVENT_JOB_END = 'job_end'


# Webhooks
HTTP_CONTENT_TYPE_JSON = 'application/json'

WEBHOOK_EVENT_TYPES = {
    EVENT_CREATE: 'created',
    EVENT_UPDATE: 'updated',
    EVENT_DELETE: 'deleted',
    EVENT_JOB_START: 'job_started',
    EVENT_JOB_END: 'job_ended',
}

# Dashboard
DEFAULT_DASHBOARD = [
    {
        'widget': 'extras.ObjectCountsWidget',
        'width': 4,
        'height': 2,
        'title': 'Organization',
        'config': {
            'models': [
                'dcim.site',
                'tenancy.tenant',
                'tenancy.contact',
            ]
        }
    },
    {
        'widget': 'extras.ObjectCountsWidget',
        'width': 4,
        'height': 3,
        'title': 'IPAM',
        'config': {
            'models': [
                'ipam.vrf',
                'ipam.aggregate',
                'ipam.prefix',
                'ipam.iprange',
                'ipam.ipaddress',
                'ipam.vlan',
            ]
        }
    },
    {
        'widget': 'extras.NoteWidget',
        'width': 4,
        'height': 2,
        'title': 'Welcome!',
        'color': 'green',
        'config': {
            'content': (
                'This is your personal dashboard. Feel free to customize it by rearranging, resizing, or removing '
                'widgets. You can also add new widgets using the "add widget" button below. Any changes affect only '
                '_your_ dashboard, so feel free to experiment!'
            )
        }
    },
    {
        'widget': 'extras.ObjectCountsWidget',
        'width': 4,
        'height': 2,
        'title': 'Circuits',
        'config': {
            'models': [
                'circuits.provider',
                'circuits.circuit',
                'circuits.providernetwork',
            ]
        }
    },
    {
        'widget': 'extras.RSSFeedWidget',
        'width': 4,
        'height': 4,
        'title': 'NetBox News',
        'config': {
            'feed_url': 'http://netbox.dev/rss/',
            'max_entries': 10,
            'cache_timeout': 14400,
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
                'dcim.devicetype',
                'dcim.device',
                'dcim.cable',
            ],
        }
    },
    {
        'widget': 'extras.ObjectCountsWidget',
        'width': 4,
        'height': 2,
        'title': 'Virtualization',
        'config': {
            'models': [
                'virtualization.cluster',
                'virtualization.virtualmachine',
            ]
        }
    },
    {
        'widget': 'extras.ObjectListWidget',
        'width': 12,
        'height': 5,
        'title': 'Change Log',
        'color': 'blue',
        'config': {
            'model': 'extras.objectchange',
            'page_size': 25,
        }
    },
]
