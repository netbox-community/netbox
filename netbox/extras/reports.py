from __future__ import unicode_literals

from collections import OrderedDict
import importlib
import inspect
import pkgutil
import sys

from django.conf import settings
from django.utils import timezone

from .constants import LOG_DEFAULT, LOG_FAILURE, LOG_INFO, LOG_LEVEL_CODES, LOG_SUCCESS, LOG_WARNING
from .models import ReportResult


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

    # Python 3.5+
    if sys.version_info >= (3, 5):
        spec = importlib.util.spec_from_file_location(module_name, file_path)
        module = importlib.util.module_from_spec(spec)
        try:
            spec.loader.exec_module(module)
        except FileNotFoundError:
            return None

    # Python 2.7
    else:
        import imp
        try:
            module = imp.load_source(module_name, file_path)
        except IOError:
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
        return '.'.join([self.module, self.name])

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

    def log_success(self, obj, message=None):
        """
        Record a successful test against an object. Logging a message is optional.
        """
        if message:
            self._log(obj, message, level=LOG_SUCCESS)
        self._results[self.active_test]['success'] += 1

    def log_info(self, obj, message):
        """
        Log an informational message.
        """
        self._log(obj, message, level=LOG_INFO)
        self._results[self.active_test]['info'] += 1

    def log_warning(self, obj, message):
        """
        Log a warning.
        """
        self._log(obj, message, level=LOG_WARNING)
        self._results[self.active_test]['warning'] += 1

    def log_failure(self, obj, message):
        """
        Log a failure. Calling this method will automatically mark the report as failed.
        """
        self._log(obj, message, level=LOG_FAILURE)
        self._results[self.active_test]['failure'] += 1
        self.failed = True

    def run(self):
        """
        Run the report and return its results. Each test method will be executed in order.
        """
        for method_name in self.test_methods:
            self.active_test = method_name
            test_method = getattr(self, method_name)
            test_method()

        # Delete any previous ReportResult and create a new one to record the result.
        ReportResult.objects.filter(report=self.full_name).delete()
        result = ReportResult(report=self.full_name, failed=self.failed, data=self._results)
        result.save()
        self.result = result

        # Perform any post-run tasks
        self.post_run()

    def post_run(self):
        """
        Extend this method to include any tasks which should execute after the report has been run.
        """
        pass
