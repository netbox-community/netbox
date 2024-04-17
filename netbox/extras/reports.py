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


class Report(object):
    """
    NetBox users can extend this object to write custom reports to be used for validating data within NetBox. Each
    report must have one or more test methods named `test_*`.

    The `_results` attribute of a completed report will take the following form:

    {
        'test_bar': {
            'failures': 42,
            'log': [
                (<datetime>, <level>, <object>, <message>),
                ...
            ]
        },
        'test_foo': {
            'failures': 0,
            'log': [
                (<datetime>, <level>, <object>, <message>),
                ...
            ]
        }
    }
    """
    description = None
    scheduling_enabled = True
    job_timeout = None

    def __init__(self):

        self._results = {}
        self.active_test = None
        self.failed = False

        self.logger = logging.getLogger(f"netbox.reports.{self.__module__}.{self.__class__.__name__}")

        # Compile test methods and initialize results skeleton
        test_methods = []
        for method in dir(self):
            if method.startswith('test_') and callable(getattr(self, method)):
                test_methods.append(method)
                self._results[method] = {
                    'success': 0,
                    'info': 0,
                    'warning': 0,
                    'failure': 0,
                    'log': [],
                }
        self.test_methods = test_methods

    @classproperty
    def module(self):
        return self.__module__

    @classproperty
    def class_name(self):
        return self.__name__

    @classproperty
    def full_name(self):
        return f'{self.module}.{self.class_name}'

    @property
    def name(self):
        """
        Override this attribute to set a custom display name.
        """
        return self.class_name

    @property
    def filename(self):
        return inspect.getfile(self.__class__)

    @property
    def source(self):
        return inspect.getsource(self.__class__)

    @property
    def is_valid(self):
        """
        Indicates whether the report can be run.
        """
        return bool(self.test_methods)

    #
    # Logging methods
    #

    def _log(self, obj, message, level=LogLevelChoices.LOG_DEFAULT):
        """
        Log a message from a test method. Do not call this method directly; use one of the log_* wrappers below.
        """
        if level not in LogLevelChoices.values():
            raise Exception(f"Unknown logging level: {level}")
        self._results[self.active_test]['log'].append((
            timezone.now().isoformat(),
            level,
            str(obj) if obj else None,
            obj.get_absolute_url() if hasattr(obj, 'get_absolute_url') else None,
            message,
        ))

    def log(self, message):
        """
        Log a message which is not associated with a particular object.
        """
        self._log(None, message, level=LogLevelChoices.LOG_DEFAULT)
        self.logger.info(message)

    def log_success(self, obj, message=None):
        """
        Record a successful test against an object. Logging a message is optional.
        """
        if message:
            self._log(obj, message, level=LogLevelChoices.LOG_SUCCESS)
        self._results[self.active_test]['success'] += 1
        self.logger.info(f"Success | {obj}: {message}")

    def log_info(self, obj, message):
        """
        Log an informational message.
        """
        self._log(obj, message, level=LogLevelChoices.LOG_INFO)
        self._results[self.active_test]['info'] += 1
        self.logger.info(f"Info | {obj}: {message}")

    def log_warning(self, obj, message):
        """
        Log a warning.
        """
        self._log(obj, message, level=LogLevelChoices.LOG_WARNING)
        self._results[self.active_test]['warning'] += 1
        self.logger.info(f"Warning | {obj}: {message}")

    def log_failure(self, obj, message):
        """
        Log a failure. Calling this method will automatically mark the report as failed.
        """
        self._log(obj, message, level=LogLevelChoices.LOG_FAILURE)
        self._results[self.active_test]['failure'] += 1
        self.logger.info(f"Failure | {obj}: {message}")
        self.failed = True

    #
    # Run methods
    #

    def run(self, job):
        """
        Run the report and save its results. Each test method will be executed in order.
        """
        self.logger.info(f"Running report")

        # Perform any post-run tasks
        self.pre_run()

        try:
            for method_name in self.test_methods:
                self.active_test = method_name
                test_method = getattr(self, method_name)
                test_method()
            job.data = self._results
            if self.failed:
                self.logger.warning("Report failed")
                job.terminate(status=JobStatusChoices.STATUS_FAILED)
            else:
                self.logger.info("Report completed successfully")
                job.terminate()
        except Exception as e:
            stacktrace = traceback.format_exc()
            self.log_failure(None, f"An exception occurred: {type(e).__name__}: {e} <pre>{stacktrace}</pre>")
            logger.error(f"Exception raised during report execution: {e}")
            job.terminate(status=JobStatusChoices.STATUS_ERRORED, error=repr(e))

        # Perform any post-run tasks
        self.post_run()

    def pre_run(self):
        """
        Extend this method to include any tasks which should execute *before* the report is run.
        """
        pass

    def post_run(self):
        """
        Extend this method to include any tasks which should execute *after* the report is run.
        """
        pass
