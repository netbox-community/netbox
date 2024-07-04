from django.utils.translation import gettext as _

from netbox.events import Event

OBJECT_CREATED = 'object_created'
OBJECT_UPDATED = 'object_updated'
OBJECT_DELETED = 'object_deleted'
JOB_STARTED = 'job_started'
JOB_ENDED = 'job_ended'

# Register core events
Event(name=OBJECT_CREATED, text=_('Object created')).register()
Event(name=OBJECT_UPDATED, text=_('Object updated')).register()
Event(name=OBJECT_DELETED, text=_('Object deleted')).register()
Event(name=JOB_STARTED, text=_('Job started')).register()
Event(name=JOB_ENDED, text=_('Job ended')).register()
