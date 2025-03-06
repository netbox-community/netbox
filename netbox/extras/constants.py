from core.events import *
from extras.choices import LogLevelChoices

# Custom fields
CUSTOMFIELD_EMPTY_VALUES = (None, '', [])

# Webhooks
HTTP_CONTENT_TYPE_JSON = 'application/json'

WEBHOOK_EVENT_TYPES = {
    # Map registered event types to public webhook "event" equivalents
    OBJECT_CREATED: 'created',
    OBJECT_UPDATED: 'updated',
    OBJECT_DELETED: 'deleted',
    JOB_STARTED: 'job_started',
    JOB_COMPLETED: 'job_ended',
    JOB_FAILED: 'job_ended',
    JOB_ERRORED: 'job_ended',
}

# Dashboard
DEFAULT_DASHBOARD = [
    {
        'widget': 'extras.BookmarksWidget',
        'width': 4,
        'height': 5,
        'title': 'Bookmarks',
        'color': 'orange',
    },
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
        'widget': 'extras.RSSFeedWidget',
        'width': 4,
        'height': 4,
        'title': 'NetBox News',
        'config': {
            'feed_url': 'http://netbox.dev/rss/',
            'max_entries': 10,
            'cache_timeout': 14400,
            'requires_internet': True,
        }
    },
    {
        'widget': 'extras.ObjectCountsWidget',
        'width': 4,
        'height': 3,
        'title': 'Circuits',
        'config': {
            'models': [
                'circuits.provider',
                'circuits.circuit',
                'circuits.providernetwork',
                'circuits.provideraccount',
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
            'model': 'core.objectchange',
            'page_size': 25,
        }
    },
]

LOG_LEVEL_RANK = {
    LogLevelChoices.LOG_DEBUG: 0,
    LogLevelChoices.LOG_DEFAULT: 1,
    LogLevelChoices.LOG_INFO: 2,
    LogLevelChoices.LOG_SUCCESS: 3,
    LogLevelChoices.LOG_WARNING: 4,
    LogLevelChoices.LOG_FAILURE: 5,
}
