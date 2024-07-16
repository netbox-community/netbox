from django.utils.translation import gettext as _

from netbox.events import *

__all__ = (
    'JOB_COMPLETED',
    'JOB_ERRORED',
    'JOB_FAILED',
    'JOB_STARTED',
    'OBJECT_CREATED',
    'OBJECT_DELETED',
    'OBJECT_UPDATED',
)

# Object events
OBJECT_CREATED = 'object_created'
OBJECT_UPDATED = 'object_updated'
OBJECT_DELETED = 'object_deleted'

# Job events
JOB_STARTED = 'job_started'
JOB_COMPLETED = 'job_completed'
JOB_FAILED = 'job_failed'
JOB_ERRORED = 'job_errored'

# Register core events
Event(name=OBJECT_CREATED, text=_('Object created')).register()
Event(name=OBJECT_UPDATED, text=_('Object updated')).register()
Event(name=OBJECT_DELETED, text=_('Object deleted')).register()
Event(name=JOB_STARTED, text=_('Job started')).register()
Event(name=JOB_COMPLETED, text=_('Job completed'), type=EVENT_TYPE_SUCCESS).register()
Event(name=JOB_FAILED, text=_('Job failed'), type=EVENT_TYPE_WARNING).register()
Event(name=JOB_ERRORED, text=_('Job errored'), type=EVENT_TYPE_DANGER).register()
