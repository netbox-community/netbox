import logging
from abc import ABC, abstractmethod
from datetime import timedelta

from django.core.exceptions import ImproperlyConfigured
from django.utils.functional import classproperty
from django_pglocks import advisory_lock
from rq.timeouts import JobTimeoutException

from core.choices import JobStatusChoices
from core.models import Job, ObjectType
from netbox.constants import ADVISORY_LOCK_KEYS
from netbox.registry import registry

__all__ = (
    'JobRunner',
    'system_job',
)


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
        try:
            job.start()
            cls(job).run(*args, **kwargs)
            job.terminate()

        except Exception as e:
            job.terminate(status=JobStatusChoices.STATUS_ERRORED, error=repr(e))
            if type(e) is JobTimeoutException:
                logging.error(e)

        # If the executed job is a periodic job, schedule its next execution at the specified interval.
        finally:
            if job.interval:
                new_scheduled_time = (job.scheduled or job.started) + timedelta(minutes=job.interval)
                if job.object and getattr(job.object, "python_class", None):
                    kwargs["job_timeout"] = job.object.python_class.job_timeout
                cls.enqueue(
                    instance=job.object,
                    user=job.user,
                    schedule_at=new_scheduled_time,
                    interval=job.interval,
                    **kwargs,
                )

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
            # If the job parameters haven't changed, don't schedule a new job and keep the current schedule. Otherwise,
            # delete the existing job and schedule a new job instead.
            if (not schedule_at or job.scheduled == schedule_at) and (job.interval == interval):
                return job
            job.delete()

        return cls.enqueue(instance=instance, schedule_at=schedule_at, interval=interval, *args, **kwargs)
