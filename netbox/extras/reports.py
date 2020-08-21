import importlib
import inspect
import logging
import pkgutil
import traceback
from collections import OrderedDict

from django.conf import settings
from django.utils import timezone
from django_rq import job

from .choices import JobResultStatusChoices, LogLevelChoices
from .models import JobResult


logger = logging.getLogger(__name__)


def is_report(obj):
    """
    Returns True if the given object is a Report.
    """
    return obj in Report.__subclasses__()


def get_report(module_name, report_name):
    """
    Return a specific report from within a module.
    """
    file_path = '{}/{}.py'.format(settings.REPORTS_ROOT, module_name)

    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(module)
    except FileNotFoundError:
        return None

    report = getattr(module, report_name, None)
    if report is None:
        return None

    return report()


def get_reports():
    """
    Compile a list of all reports available across all modules in the reports path. Returns a list of tuples:

    [
        (module_name, (report, report, report, ...)),
        (module_name, (report, report, report, ...)),
        ...
    ]
    """
    module_list = []

    # Iterate through all modules within the reports path. These are the user-created files in which reports are
    # defined.
    for importer, module_name, _ in pkgutil.iter_modules([settings.REPORTS_ROOT]):
        module = importer.find_module(module_name).load_module(module_name)
        report_list = [cls() for _, cls in inspect.getmembers(module, is_report)]
        module_list.append((module_name, report_list))

    return module_list


@job('default')
def run_report(job_result, *args, **kwargs):
    """
    Helper function to call the run method on a report. This is needed to get around the inability to pickle an instance
    method for queueing into the background processor.
    """
    module_name, report_name = job_result.name.split('.', 1)
    report = get_report(module_name, report_name)

    try:
        report.run(job_result)
    except Exception as e:
        print(e)
        job_result.set_status(JobResultStatusChoices.STATUS_ERRORED)
        job_result.save()
        logging.error(f"Error during execution of report {job_result.name}")

    # Delete any previous terminal state results
    JobResult.objects.filter(
        obj_type=job_result.obj_type,
        name=job_result.name,
        status__in=JobResultStatusChoices.TERMINAL_STATE_CHOICES
    ).exclude(
        pk=job_result.pk
    ).delete()


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

    def __init__(self):

        self._results = OrderedDict()
        self.active_test = None
        self.failed = False

        self.logger = logging.getLogger(f"netbox.reports.{self.full_name}")

        # Compile test methods and initialize results skeleton
        test_methods = []
        for method in dir(self):
            if method.startswith('test_') and callable(getattr(self, method)):
                test_methods.append(method)
                self._results[method] = OrderedDict([
                    ('success', 0),
                    ('info', 0),
                    ('warning', 0),
                    ('failure', 0),
                    ('log', []),
                ])
        if not test_methods:
            raise Exception("A report must contain at least one test method.")
        self.test_methods = test_methods

    @property
    def module(self):
        return self.__module__

    @property
    def class_name(self):
        return self.__class__.__name__

    @property
    def name(self):
        """
        Override this attribute to set a custom display name.
        """
        return self.class_name

    @property
    def full_name(self):
        return f'{self.module}.{self.class_name}'

    def _log(self, obj, message, level=LogLevelChoices.LOG_DEFAULT):
        """
        Log a message from a test method. Do not call this method directly; use one of the log_* wrappers below.
        """
        if level not in LogLevelChoices.as_dict():
            raise Exception("Unknown logging level: {}".format(level))
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

    def run(self, job_result):
        """
        Run the report and save its results. Each test method will be executed in order.
        """
        self.logger.info(f"Running report")
        job_result.status = JobResultStatusChoices.STATUS_RUNNING
        job_result.save()

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
            job_result.set_status(JobResultStatusChoices.STATUS_ERRORED)

        job_result.data = self._results
        job_result.completed = timezone.now()
        job_result.save()

        # Perform any post-run tasks
        self.post_run()

    def post_run(self):
        """
        Extend this method to include any tasks which should execute after the report has been run.
        """
        pass
