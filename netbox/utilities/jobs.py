import logging
from abc import ABC, abstractmethod
from datetime import timedelta

from django.db.backends.signals import connection_created
from django.utils.functional import classproperty
from django_pglocks import advisory_lock
from rq.timeouts import JobTimeoutException

from core.choices import JobStatusChoices
from core.models import Job, ObjectType
from netbox.constants import ADVISORY_LOCK_KEYS

__all__ = (
    'BackgroundJob',
)


class BackgroundJob(ABC):
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
            job: The specific `Job` this `BackgroundJob` helper class is executing.
        """
        self.job = job

    @classproperty
    def name(cls):
        return getattr(cls.Meta, 'name', cls.__name__)

    @abstractmethod
    def run(self, *args, **kwargs):
        """
        Run the job.

        A `BackgroundJob` class needs to implement this method to execute all commands of the job.
        """
        pass

    @classmethod
    def handle(cls, job, *args, **kwargs):
        """
        Handle the execution of a `BackgroundJob`.

        This method is called by the Job Scheduler to handle the execution of all job commands. It will maintain the
        job's metadata and handle errors. For periodic jobs, a new job is automatically scheduled using its `interval'.
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
        Get all jobs of this `BackgroundJob` related to a specific instance.
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
        Enqueue a new `BackgroundJob`.

        This method is a wrapper of `Job.enqueue()` using `handle()` as function callback. See its documentation for
        parameters.
        """
        return Job.enqueue(cls.handle, name=cls.name, *args, **kwargs)

    @classmethod
    @advisory_lock(ADVISORY_LOCK_KEYS['job-schedules'])
    def enqueue_once(cls, instance=None, schedule_at=None, interval=None, *args, **kwargs):
        """
        Enqueue a new `BackgroundJob` once, i.e. skip duplicate jobs.

        Like `enqueue()`, this method adds a new `BackgroundJob` to the job queue. However, if there's already a
        `BackgroundJob` of this class scheduled for `instance`, the existing job will be updated if necessary. This
        ensures that a particular schedule is only set up once at any given time, i.e. multiple calls to this method are
        idempotent.

        Note that this does not forbid running additional jobs with the `enqueue()` method, e.g. to schedule an
        immediate synchronization job in addition to a periodic synchronization schedule.

        For additional parameters see `enqueue()`.

        Args:
            instance: The NetBox object to which this `BackgroundJob` pertains (optional)
            schedule_at: Schedule the job to be executed at the passed date and time
            interval: Recurrence interval (in minutes)
        """
        job = cls.get_jobs(instance).filter(status__in=JobStatusChoices.ENQUEUED_STATE_CHOICES).first()
        if job:
            # If the job parameters haven't changed, don't schedule a new job and keep the current schedule. Otherwise,
            # delete the existing job and schedule a new job instead.
            if (schedule_at and job.scheduled == schedule_at) and (job.interval == interval):
                return job
            job.delete()

        return cls.enqueue(instance=instance, schedule_at=schedule_at, interval=interval, *args, **kwargs)

    @classmethod
    def setup(cls, *args, **kwargs):
        """
        Setup a new `BackgroundJob` during plugin initialization.

        This method should be called from the plugins `ready()` function to set up the schedule as early as possible.
        For interactive setup of schedules (e.g. on user requests), use either `enqueue()` or `enqueue_once()` instead.
        """
        connection_created.connect(lambda sender, **signal_kwargs: cls.enqueue_once(*args, **kwargs))
