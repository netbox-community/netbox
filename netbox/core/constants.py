from dataclasses import dataclass

from django.utils.translation import gettext_lazy as _
from rq.job import JobStatus

__all__ = (
    'RQ_TASK_STATUSES',
)


@dataclass
class Status:
    label: str
    color: str


RQ_TASK_STATUSES = {
    JobStatus.QUEUED: Status(_('Queued'), 'cyan'),
    JobStatus.FINISHED: Status(_('Finished'), 'green'),
    JobStatus.FAILED: Status(_('Failed'), 'red'),
    JobStatus.STARTED: Status(_('Started'), 'blue'),
    JobStatus.DEFERRED: Status(_('Deferred'), 'gray'),
    JobStatus.SCHEDULED: Status(_('Scheduled'), 'purple'),
    JobStatus.STOPPED: Status(_('Stopped'), 'orange'),
    JobStatus.CANCELED: Status(_('Cancelled'), 'yellow'),
}
