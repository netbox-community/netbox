from django.utils.translation import gettext as _

from netbox.events import EventType, EVENT_TYPE_KIND_DANGER, EVENT_TYPE_KIND_SUCCESS, EVENT_TYPE_KIND_WARNING

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
EventType(OBJECT_CREATED, _('Object created')).register()
EventType(OBJECT_UPDATED, _('Object updated')).register()
EventType(OBJECT_DELETED, _('Object deleted')).register()
EventType(JOB_STARTED, _('Job started')).register()
EventType(JOB_COMPLETED, _('Job completed'), kind=EVENT_TYPE_KIND_SUCCESS).register()
EventType(JOB_FAILED, _('Job failed'), kind=EVENT_TYPE_KIND_WARNING).register()
EventType(JOB_ERRORED, _('Job errored'), kind=EVENT_TYPE_KIND_DANGER).register()
