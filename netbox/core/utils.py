from django.http import Http404
from django_rq.utils import get_jobs
from rq.exceptions import NoSuchJobError
from rq.job import Job as RQ_Job, JobStatus as RQJobStatus
from rq.registry import (
    DeferredJobRegistry,
    FailedJobRegistry,
    FinishedJobRegistry,
    ScheduledJobRegistry,
    StartedJobRegistry,
)


def get_rq_jobs_from_status(queue, status):
    jobs = []

    try:
        registry_cls = {
            RQJobStatus.STARTED: StartedJobRegistry,
            RQJobStatus.DEFERRED: DeferredJobRegistry,
            RQJobStatus.FINISHED: FinishedJobRegistry,
            RQJobStatus.FAILED: FailedJobRegistry,
            RQJobStatus.SCHEDULED: ScheduledJobRegistry,
        }[status]
    except KeyError:
        raise Http404
    registry = registry_cls(queue.name, queue.connection)

    job_ids = registry.get_job_ids()
    if status != RQJobStatus.DEFERRED:
        jobs = get_jobs(queue, job_ids, registry)
    else:
        # Deferred jobs require special handling
        for job_id in job_ids:
            try:
                jobs.append(RQ_Job.fetch(job_id, connection=queue.connection, serializer=queue.serializer))
            except NoSuchJobError:
                pass

    if jobs and status == RQJobStatus.SCHEDULED:
        for job in jobs:
            job.scheduled_at = registry.get_scheduled_time(job)

    return jobs
