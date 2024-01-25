import inspect
import logging
import traceback
from datetime import timedelta

from django.utils import timezone
from django.utils.functional import classproperty
from django_rq import job

from core.choices import JobStatusChoices
from core.models import Job
from .choices import LogLevelChoices
from .models import ReportModule
from .scripts import BaseScript

__all__ = (
    'Report',
    'get_module_and_report',
    'run_report',
)

logger = logging.getLogger(__name__)


def get_module_and_report(module_name, report_name):
    module = ReportModule.objects.get(file_path=f'{module_name}.py')
    report = module.reports.get(report_name)()
    return module, report


@job('default')
def run_report(job, *args, **kwargs):
    """
    Helper function to call the run method on a report. This is needed to get around the inability to pickle an instance
    method for queueing into the background processor.
    """
    job.start()

    module = ReportModule.objects.get(pk=job.object_id)
    report = module.reports.get(job.name)()

    try:
        report.run(job)
    except Exception as e:
        job.terminate(status=JobStatusChoices.STATUS_ERRORED, error=repr(e))
        logging.error(f"Error during execution of report {job.name}")
    finally:
        # Schedule the next job if an interval has been set
        if job.interval:
            new_scheduled_time = job.scheduled + timedelta(minutes=job.interval)
            Job.enqueue(
                run_report,
                instance=job.object,
                name=job.name,
                user=job.user,
                job_timeout=report.job_timeout,
                schedule_at=new_scheduled_time,
                interval=job.interval
            )


class Report(BaseScript):
    def log_success(self, obj, message=None):
        super().log_success(message, obj)

    def log_info(self, obj, message):
        super().log_info(message, obj)

    def log_warning(self, obj, message):
        super().log_warning(message, obj)

    def log_failure(self, obj, message):
        super().log_failure(message, obj)
