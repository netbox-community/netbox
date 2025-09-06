from dataclasses import dataclass

from django.utils.translation import gettext_lazy as _
from rq.job import JobStatus

__all__ = (
    'JOB_LOG_ENTRY_LEVELS',
    'RQ_TASK_STATUSES',
)


@dataclass
class Badge:
    label: str
    color: str


RQ_TASK_STATUSES = {
    JobStatus.QUEUED: Badge(_('Queued'), 'cyan'),
    JobStatus.FINISHED: Badge(_('Finished'), 'green'),
    JobStatus.FAILED: Badge(_('Failed'), 'red'),
    JobStatus.STARTED: Badge(_('Started'), 'blue'),
    JobStatus.DEFERRED: Badge(_('Deferred'), 'gray'),
    JobStatus.SCHEDULED: Badge(_('Scheduled'), 'purple'),
    JobStatus.STOPPED: Badge(_('Stopped'), 'orange'),
    JobStatus.CANCELED: Badge(_('Cancelled'), 'yellow'),
}

JOB_LOG_ENTRY_LEVELS = {
    'debug': Badge(_('Debug'), 'gray'),
    'info': Badge(_('Info'), 'blue'),
    'warning': Badge(_('Warning'), 'orange'),
    'error': Badge(_('Error'), 'red'),
}
