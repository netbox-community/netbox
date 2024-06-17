import logging
from abc import ABC, abstractmethod
from datetime import timedelta

from rq.timeouts import JobTimeoutException

from core.choices import JobStatusChoices
from core.models import Job


class BackgroundJob(ABC):
    """
    Background Job helper class.

    This class handles the execution of a background job. It is responsible for maintaining its state, reporting errors,
    and scheduling recurring jobs.
    """

    @classmethod
    @abstractmethod
    def run(cls, *args, **kwargs) -> None:
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
            cls.run(job, *args, **kwargs)
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
                    name=job.name,
                    user=job.user,
                    schedule_at=new_scheduled_time,
                    interval=job.interval,
                    **kwargs,
                )

    @classmethod
    def enqueue(cls, *args, **kwargs):
        """
        Enqueue a new `BackgroundJob`.

        This method is a wrapper of `Job.enqueue` using `handle()` as function callback. See its documentation for
        parameters.
        """
        return Job.enqueue(cls.handle, *args, **kwargs)
