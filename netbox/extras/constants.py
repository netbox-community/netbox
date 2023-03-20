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
        'widget': 'extras.ObjectListWidget',
        'width': 12,
        'height': 6,
        'title': 'Change Log',
        'config': {
            'model': 'extras.objectchange',
        }
    },
]
