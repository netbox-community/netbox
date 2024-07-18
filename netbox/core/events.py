from django.utils.translation import gettext as _

from netbox.events import Event, EVENT_TYPE_DANGER, EVENT_TYPE_SUCCESS, EVENT_TYPE_WARNING

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
Event(OBJECT_CREATED, _('Object created')).register()
Event(OBJECT_UPDATED, _('Object updated')).register()
Event(OBJECT_DELETED, _('Object deleted')).register()
Event(JOB_STARTED, _('Job started')).register()
Event(JOB_COMPLETED, _('Job completed'), type=EVENT_TYPE_SUCCESS).register()
Event(JOB_FAILED, _('Job failed'), type=EVENT_TYPE_WARNING).register()
Event(JOB_ERRORED, _('Job errored'), type=EVENT_TYPE_DANGER).register()
