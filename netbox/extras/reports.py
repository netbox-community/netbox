import importlib
import inspect
import logging
import pkgutil
from collections import OrderedDict

from django.conf import settings
from django.utils import timezone

from .constants import *
from .models import ReportResult
from .registry import registry


def is_report(obj):
    """
    Returns True if the given object is a Report.
    """
    return obj in Report.__subclasses__()


def get_report(module_name, report_name):
    """
    Return a specific report from within a module.
    """
    reports = get_reports()
    for grouping, report_list in reports:
        if grouping != module_name:
            continue
        for report in report_list:
            if report.name == report_name:
                return report

    return None


def get_reports(use_names=False):
    """
    Compile a list of all reports available across all modules in the reports path. Returns a list of tuples:

    [
        (module_name, (report, report, report, ...)),
        (module_name, (report, report, report, ...)),
        ...
    ]

    Set use_names to True to use each module's human-defined name in place of the actual module name.
    """
    module_list = []

    # Iterate through reports provided by plugins
    for module_name, report_classes in registry['plugin_reports'].items():
        if use_names and report_classes:
            module = inspect.getmodule(report_classes[0])
            if hasattr(module, "name"):
                module_name = module.name
        module_list.append((module_name, [report() for report in report_classes]))

    # Iterate through all modules within the reports path. These are the user-created files in which reports are
    # defined.
    for importer, module_name, _ in pkgutil.iter_modules([settings.REPORTS_ROOT]):
        module = importer.find_module(module_name).load_module(module_name)
        report_list = [cls() for _, cls in inspect.getmembers(module, is_report)]
        if use_names and hasattr(module, "name"):
            module_name = module.name
        module_list.append((module_name, report_list))

    return module_list


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
    def name(self):
        return self.__class__.__name__

    @property
    def full_name(self):
        return '.'.join([self.__module__, self.__class__.__name__])

    def _log(self, obj, message, level=LOG_DEFAULT):
        """
        Log a message from a test method. Do not call this method directly; use one of the log_* wrappers below.
        """
        if level not in LOG_LEVEL_CODES:
            raise Exception("Unknown logging level: {}".format(level))
        self._results[self.active_test]['log'].append((
            timezone.now().isoformat(),
            LOG_LEVEL_CODES.get(level),
            str(obj) if obj else None,
            obj.get_absolute_url() if getattr(obj, 'get_absolute_url', None) else None,
            message,
        ))

    def log(self, message):
        """
        Log a message which is not associated with a particular object.
        """
        self._log(None, message, level=LOG_DEFAULT)
        self.logger.info(message)

    def log_success(self, obj, message=None):
        """
        Record a successful test against an object. Logging a message is optional.
        """
        if message:
            self._log(obj, message, level=LOG_SUCCESS)
        self._results[self.active_test]['success'] += 1
        self.logger.info(f"Success | {obj}: {message}")

    def log_info(self, obj, message):
        """
        Log an informational message.
        """
        self._log(obj, message, level=LOG_INFO)
        self._results[self.active_test]['info'] += 1
        self.logger.info(f"Info | {obj}: {message}")

    def log_warning(self, obj, message):
        """
        Log a warning.
        """
        self._log(obj, message, level=LOG_WARNING)
        self._results[self.active_test]['warning'] += 1
        self.logger.info(f"Warning | {obj}: {message}")

    def log_failure(self, obj, message):
        """
        Log a failure. Calling this method will automatically mark the report as failed.
        """
        self._log(obj, message, level=LOG_FAILURE)
        self._results[self.active_test]['failure'] += 1
        self.logger.info(f"Failure | {obj}: {message}")
        self.failed = True

    def run(self):
        """
        Run the report and return its results. Each test method will be executed in order.
        """
        self.logger.info(f"Running report")

        for method_name in self.test_methods:
            self.active_test = method_name
            test_method = getattr(self, method_name)
            test_method()

        # Delete any previous ReportResult and create a new one to record the result.
        ReportResult.objects.filter(report=self.full_name).delete()
        result = ReportResult(report=self.full_name, failed=self.failed, data=self._results)
        result.save()
        self.result = result

        if self.failed:
            self.logger.warning("Report failed")
        else:
            self.logger.info("Report completed successfully")

        # Perform any post-run tasks
        self.post_run()

    def post_run(self):
        """
        Extend this method to include any tasks which should execute after the report has been run.
        """
        pass
