from jinja2 import ChainableUndefined, DebugUndefined, StrictUndefined, Undefined

from core.events import *
from extras.choices import LogLevelChoices

# Custom fields
CUSTOMFIELD_EMPTY_VALUES = (None, '', [])

# ImageAttachment
IMAGE_ATTACHMENT_IMAGE_FORMATS = {
    'avif': 'image/avif',
    'bmp': 'image/bmp',
    'gif': 'image/gif',
    'jpeg': 'image/jpeg',
    'jpg': 'image/jpeg',
    'png': 'image/png',
    'webp': 'image/webp',
}

# Template Export
DEFAULT_MIME_TYPE = 'text/plain; charset=utf-8'

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

# Allowed Jinja2 environment parameters and their permitted values.
# Only keys listed here may appear in a template's environment_params.
#   None  = any JSON-serializable value accepted (scalars, booleans, etc.)
#   dict  = only dict keys accepted; dict values are the resolved Python objects
#
# Note: 'finalize' is intentionally absent. It is deprecated and handled as a
# legacy carve-out in RenderTemplateMixin (blocked from new use, but existing
# stored values continue to resolve via import_string at render time).
JINJA_ENV_PARAMS_ALLOWED = {
    # Boolean / scalar params (accept any JSON-serializable value)
    'auto_reload': None,
    'autoescape': None,
    'cache_size': None,
    'enable_async': None,
    'keep_trailing_newline': None,
    'lstrip_blocks': None,
    'optimized': None,
    'trim_blocks': None,
    # String params (template syntax delimiters)
    'block_start_string': None,
    'block_end_string': None,
    'comment_start_string': None,
    'comment_end_string': None,
    'line_comment_prefix': None,
    'line_statement_prefix': None,
    'newline_sequence': None,
    'variable_start_string': None,
    'variable_end_string': None,
    # Mapped params (value must be a key in the dict; resolved to the dict value)
    'undefined': {
        'jinja2.ChainableUndefined': ChainableUndefined,
        'jinja2.DebugUndefined': DebugUndefined,
        'jinja2.StrictUndefined': StrictUndefined,
        'jinja2.Undefined': Undefined,
    },
    # Excluded (dangerous — accept callables or trigger imports):
    #   'bytecode_cache' — accepts arbitrary object
    #   'extensions'     — Jinja2 internally calls import_string() on string entries
    #   'finalize'       — deprecated; legacy carve-out in RenderTemplateMixin
    #   'loader'         — accepts arbitrary object
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
            'feed_url': 'https://api.netbox.oss.netboxlabs.com/v1/newsfeed/',
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
    LogLevelChoices.LOG_INFO: 1,
    LogLevelChoices.LOG_SUCCESS: 2,
    LogLevelChoices.LOG_WARNING: 3,
    LogLevelChoices.LOG_FAILURE: 4,
}

# Config context cache: fields whose modification on an object requires re-rendering its config
# context cache, keyed by model label.
CC_FIELDS_BY_MODEL = {
    'dcim.device': (
        'site_id', 'location_id', 'device_type_id', 'role_id', 'tenant_id', 'platform_id',
        'cluster_id', 'local_context_data',
    ),
    'virtualization.virtualmachine': (
        'site_id', 'cluster_id', 'device_id', 'tenant_id', 'platform_id', 'role_id',
        'local_context_data',
    ),
}
