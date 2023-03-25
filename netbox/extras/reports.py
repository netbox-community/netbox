import logging
import traceback
from datetime import timedelta

from django.utils import timezone
from django.utils.functional import classproperty
from django_rq import job

from .choices import JobResultStatusChoices, LogLevelChoices
from .models import JobResult, ReportModule

logger = logging.getLogger(__name__)


def get_report(module_name, report_name):
    """
    Return a specific report from within a module.
    """
    module = ReportModule.objects.get(file_path=f'{module_name}.py')
    return module.reports.get(report_name)


@job('default')
def run_report(job_result, *args, **kwargs):
    """
    Helper function to call the run method on a report. This is needed to get around the inability to pickle an instance
    method for queueing into the background processor.
    """
    module_name, report_name = job_result.name.split('.', 1)
    report = get_report(module_name, report_name)()

    try:
        job_result.start()
        report.run(job_result)
    except Exception:
        job_result.terminate(status=JobResultStatusChoices.STATUS_ERRORED)
        logging.error(f"Error during execution of report {job_result.name}")
    finally:
        # Schedule the next job if an interval has been set
        start_time = job_result.scheduled or job_result.started
        if start_time and job_result.interval:
            new_scheduled_time = start_time + timedelta(minutes=job_result.interval)
            JobResult.enqueue_job(
                run_report,
                name=job_result.name,
                obj_type=job_result.obj_type,
                user=job_result.user,
                job_timeout=report.job_timeout,
                schedule_at=new_scheduled_time,
                interval=job_result.interval
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
        if not test_methods:
            raise Exception("A report must contain at least one test method.")
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

    def run(self, job_result):
        """
        Run the report and save its results. Each test method will be executed in order.
        """
        self.logger.info(f"Running report")
        job_result.status = JobResultStatusChoices.STATUS_RUNNING
        job_result.save()

        # Perform any post-run tasks
        self.pre_run()

        try:
            for method_name in self.test_methods:
                self.active_test = method_name
                test_method = getattr(self, method_name)
                test_method()
            if self.failed:
                self.logger.warning("Report failed")
                job_result.status = JobResultStatusChoices.STATUS_FAILED
            else:
                self.logger.info("Report completed successfully")
                job_result.status = JobResultStatusChoices.STATUS_COMPLETED
        except Exception as e:
            stacktrace = traceback.format_exc()
            self.log_failure(None, f"An exception occurred: {type(e).__name__}: {e} <pre>{stacktrace}</pre>")
            logger.error(f"Exception raised during report execution: {e}")
            job_result.terminate(status=JobResultStatusChoices.STATUS_ERRORED)
        finally:
            job_result.terminate()

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
