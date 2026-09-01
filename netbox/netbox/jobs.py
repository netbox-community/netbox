import logging
import os
import traceback
from abc import ABC, abstractmethod
from datetime import timedelta
from pathlib import Path

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.utils import timezone
from django.utils.functional import classproperty
from django.utils.translation import gettext_lazy as _
from django_pglocks import advisory_lock
from rq.timeouts import JobTimeoutException

from core.choices import JobStatusChoices
from core.exceptions import JobFailed
from core.models import Job, ObjectType
from netbox.constants import ADVISORY_LOCK_KEYS
from netbox.registry import registry
from utilities.request import apply_request_processors

__all__ = (
    'AsyncViewJob',
    'JobRunner',
    'system_job',
)

# The installation root, e.g. "/opt/netbox/". Used to strip absolute path
# prefixes from traceback file paths before recording them in the job log.
# jobs.py lives at <root>/netbox/netbox/jobs.py, so parents[2] is the root.
_INSTALL_ROOT = str(Path(__file__).resolve().parents[2]) + os.sep

# Margin added to a job's run timeout before a "running" system job is treated as stranded. A
# job still running this long past its RQ timeout can no longer be executing legitimately (its
# worker was killed), so the window is keyed on run duration rather than the recurrence interval.
# See reconcile_stale_system_jobs() and issue #22714.
STALE_RUNNING_JOB_GRACE_SECONDS = 600

# How long past its scheduled time a job in "scheduled" status must be before enqueue_once() treats
# it as stranded (its RQ-side scheduler entry was lost) rather than merely waiting its turn in the
# queue. This is queue latency, not run duration, so it's a separate margin from the running-job
# grace above. See enqueue_once() and issue #22714.
STALE_SCHEDULED_JOB_GRACE_SECONDS = 600


def system_job(interval):
    """
    Decorator for registering a `JobRunner` class as system background job.
    """
    if type(interval) is not int:
        raise ImproperlyConfigured("System job interval must be an integer (minutes).")

    def _wrapper(cls):
        registry['system_jobs'][cls] = {
            'interval': interval
        }
        return cls

    return _wrapper


def resolve_job_timeout(job_class, job):
    """
    Return the RQ run timeout (in seconds) a `JobRunner` runs under, falling back to
    `RQ_DEFAULT_TIMEOUT` when it declares none. There is no single timeout contract across job
    types: scripts expose `Meta.job_timeout` (class-level), some plugin runners expose an instance
    `@property`, and the base class declares nothing. Instantiate the runner so an instance property
    resolves correctly regardless of what it reads.
    """
    return getattr(job_class(job), 'job_timeout', None) or settings.RQ_DEFAULT_TIMEOUT


@advisory_lock(ADVISORY_LOCK_KEYS['job-schedules'])
def reconcile_stale_system_jobs(job_class, interval):
    """
    Fail any object-less system job of this class left stranded in "running" status by a worker
    that was killed mid-run (issue #22714). Such a row is never reset, and because "running" is
    an enqueued state, `enqueue_once()` mistakes it for a live schedule and never re-arms it.

    A running job is treated as stranded once its `started` timestamp is older than the job's own
    RQ run timeout plus a margin: past that point the run can no longer be executing legitimately.
    Keying on run duration rather than the recurrence `interval` lets recovery fire on the common
    case (a worker killed and restarted moments later) while still tolerating a legitimately long
    run that declares a large timeout. RQ is not consulted: a killed job's RQ entry can outlive the
    worker, and the schedule may be recovered with RQ state wiped.
    """
    running = list(
        Job.objects.filter(
            name=job_class.name,
            object_id__isnull=True,
            interval=interval,
            status=JobStatusChoices.STATUS_RUNNING,
        )
    )
    if not running:
        return

    # The timeout is a property of the runner, not the individual job, so resolve it once. Because
    # the window sits past the job's own RQ timeout (the deadline at which RQ itself would kill a
    # live run), a job still inside it is effectively never a live one, so this can't race a running
    # worker's own terminate() under normal operation.
    grace = resolve_job_timeout(job_class, running[0]) + STALE_RUNNING_JOB_GRACE_SECONDS
    cutoff = timezone.now() - timedelta(seconds=grace)

    for job in running:
        if not job.started or job.started > cutoff:
            continue
        # STATUS_ERRORED (not FAILED) records an unexpected fault rather than a self-declared
        # failure, as handle() does for an unhandled exception. For an object-less, userless
        # system job, terminate() sends no notification and triggers no event rule.
        job.terminate(
            status=JobStatusChoices.STATUS_ERRORED,
            error=_("Worker terminated before job completed"),
        )


class JobLogHandler(logging.Handler):
    """
    A logging handler which records entries on a Job.
    """
    def __init__(self, job, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.job = job

    def emit(self, record):
        # Enter the record in the log of the associated Job
        self.job.log(record)


class JobRunner(ABC):
    """
    Background Job helper class.

    This class handles the execution of a background job. It is responsible for maintaining its state, reporting errors,
    and scheduling recurring jobs.
    """

    class Meta:
        pass

    def __init__(self, job):
        """
        Args:
            job: The specific `Job` this `JobRunner` is executing.
        """
        self.job = job

        # Initiate the system logger
        self.logger = logging.getLogger(f"netbox.jobs.{self.__class__.__name__}")
        self.logger.setLevel(logging.DEBUG)
        self.logger.addHandler(JobLogHandler(job))

    @classproperty
    def name(cls):
        return getattr(cls.Meta, 'name', cls.__name__)

    @abstractmethod
    def run(self, *args, **kwargs):
        """
        Run the job.

        A `JobRunner` class needs to implement this method to execute all commands of the job.
        """
        pass

    @classmethod
    def handle(cls, job, *args, **kwargs):
        """
        Handle the execution of a `Job`.

        This method is called by the Job Scheduler to handle the execution of all job commands. It will maintain the
        job's metadata and handle errors. For periodic jobs, a new job is automatically scheduled using its `interval`.
        """
        logger = logging.getLogger('netbox.jobs')

        try:
            job.start()
            cls(job).run(*args, **kwargs)
            job.terminate()

        except JobFailed:
            logger.warning(f"Job {job} failed")
            job.terminate(status=JobStatusChoices.STATUS_FAILED)

        except Exception as e:
            tb_str = traceback.format_exc().replace(_INSTALL_ROOT, '')
            tb_record = logging.makeLogRecord({
                'levelno': logging.ERROR,
                'levelname': 'ERROR',
                'msg': tb_str,
            })
            job.log(tb_record)
            job.terminate(status=JobStatusChoices.STATUS_ERRORED, error=repr(e))
            if type(e) is JobTimeoutException:
                logger.error(e)

        # If the executed job is a periodic job, schedule its next execution at the specified interval.
        finally:
            if job.interval:
                # Determine the new scheduled time. Cannot be earlier than one minute in the future.
                new_scheduled_time = max(
                    (job.scheduled or job.started) + timedelta(minutes=job.interval),
                    timezone.now() + timedelta(minutes=1)
                )
                if job.object and getattr(job.object, "python_class", None):
                    kwargs["job_timeout"] = job.object.python_class.job_timeout

                enqueue_kwargs = dict(
                    instance=job.object,
                    name=job.name,
                    user=job.user,
                    schedule_at=new_scheduled_time,
                    interval=job.interval,
                    notifications=job.notifications,
                    **kwargs,
                )

                if cls in registry['system_jobs']:
                    # System jobs are also scheduled by `enqueue_once()` at worker startup,
                    # which races with this finally block and can produce duplicate schedules
                    # (see #22232). Acquire the same advisory lock used by `enqueue_once()`
                    # and skip rescheduling if a successor is already enqueued.
                    #
                    # This branch is limited to system jobs because generic recurring jobs
                    # (e.g. scheduled scripts) may have multiple legitimate schedules sharing
                    # the same runner/object/interval but differing in their runtime kwargs.
                    with advisory_lock(ADVISORY_LOCK_KEYS['job-schedules']):
                        successor_exists = Job.objects.filter(
                            name=cls.name,
                            object_id__isnull=True,
                            status__in=JobStatusChoices.ENQUEUED_STATE_CHOICES,
                            interval=job.interval,
                        ).exclude(pk=job.pk).exists()
                        if not successor_exists:
                            cls.enqueue(**enqueue_kwargs)
                else:
                    cls.enqueue(**enqueue_kwargs)

    @classmethod
    def get_jobs(cls, instance=None):
        """
        Get all jobs of this `JobRunner` related to a specific instance.
        """
        jobs = Job.objects.filter(name=cls.name)

        if instance:
            object_type = ObjectType.objects.get_for_model(instance, for_concrete_model=False)
            jobs = jobs.filter(
                object_type=object_type,
                object_id=instance.pk,
            )

        return jobs

    @classmethod
    def enqueue(cls, *args, **kwargs):
        """
        Enqueue a new `Job`.

        This method is a wrapper of `Job.enqueue()` using `handle()` as function callback. See its documentation for
        parameters.
        """
        name = kwargs.pop('name', None) or cls.name
        return Job.enqueue(cls.handle, name=name, *args, **kwargs)

    @classmethod
    @advisory_lock(ADVISORY_LOCK_KEYS['job-schedules'])
    def enqueue_once(cls, instance=None, schedule_at=None, interval=None, *args, **kwargs):
        """
        Enqueue a new `Job` once, i.e. skip duplicate jobs.

        Like `enqueue()`, this method adds a new `Job` to the job queue. However, if there's already a job of this
        class scheduled for `instance`, the existing job will be updated if necessary. This ensures that a particular
        schedule is only set up once at any given time, i.e. multiple calls to this method are idempotent.

        Note that this does not forbid running additional jobs with the `enqueue()` method, e.g. to schedule an
        immediate synchronization job in addition to a periodic synchronization schedule.

        For additional parameters see `enqueue()`.

        Args:
            instance: The NetBox object to which this job pertains (optional)
            schedule_at: Schedule the job to be executed at the passed date and time
            interval: Recurrence interval (in minutes)
        """
        job = cls.get_jobs(instance).filter(status__in=JobStatusChoices.ENQUEUED_STATE_CHOICES).first()
        if job:
            # If the job parameters haven't changed, don't schedule a new job and keep the current schedule.
            # Otherwise, delete the existing job and schedule a new job instead. A job still in "scheduled"
            # status well past its scheduled time is stale (its RQ-side scheduler entry was lost, e.g. by a
            # Redis restart) and must be replaced rather than reused, even though its parameters match. The
            # grace margin avoids mistaking a job that is merely waiting its turn in the queue (still
            # "scheduled" with a just-passed timestamp) for a stranded one. Running/pending jobs are exempt:
            # their `scheduled` timestamp is expected to be in the past (or unset) once they've started.
            stale_before = timezone.now() - timedelta(seconds=STALE_SCHEDULED_JOB_GRACE_SECONDS)
            is_stale = (
                job.status == JobStatusChoices.STATUS_SCHEDULED and
                job.scheduled and
                job.scheduled <= stale_before
            )
            if not is_stale and (not schedule_at or job.scheduled == schedule_at) and (job.interval == interval):
                return job
            job.delete()

        return cls.enqueue(instance=instance, schedule_at=schedule_at, interval=interval, *args, **kwargs)


class AsyncViewJob(JobRunner):
    """
    Execute a view as a background job.
    """
    class Meta:
        name = 'Async View'

    def run(self, view_cls, request, **kwargs):
        view = view_cls.as_view()
        request.job = self

        # Apply all registered request processors (e.g. event_tracking)
        with apply_request_processors(request):
            view(request)

        if self.job.error:
            raise JobFailed()
