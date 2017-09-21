from collections import OrderedDict

from django.utils import timezone

from .constants import LOG_DEFAULT, LOG_FAILURE, LOG_INFO, LOG_LEVEL_CODES, LOG_SUCCESS, LOG_WARNING


class Report(object):
    """
    NetBox users can extend this object to write custom reports to be used for validating data within NetBox. Each
    report must have one or more test methods named `test_*`.

    The `results` attribute of a completed report will take the following form:

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

    def __init__(self):

        self.results = OrderedDict()
        self.active_test = None
        self.failed = False

        # Compile test methods and initialize results skeleton
        test_methods = []
        for method in dir(self):
            if method.startswith('test_') and callable(getattr(self, method)):
                test_methods.append(method)
                self.results[method] = OrderedDict([
                    ('success', 0),
                    ('info', 0),
                    ('warning', 0),
                    ('failed', 0),
                    ('log', []),
                ])
        if not test_methods:
            raise Exception("A report must contain at least one test method.")
        self.test_methods = test_methods

    def _log(self, obj, message, level=LOG_DEFAULT):
        """
        Log a message from a test method. Do not call this method directly; use one of the log_* wrappers below.
        """
        if level not in LOG_LEVEL_CODES:
            raise Exception("Unknown logging level: {}".format(level))
        logline = [timezone.now(), level, obj, message]
        self.results[self.active_test]['log'].append(logline)

    def log_success(self, obj, message=None):
        """
        Record a successful test against an object. Logging a message is optional.
        """
        if message:
            self._log(obj, message, level=LOG_SUCCESS)
        self.results[self.active_test]['success'] += 1

    def log_info(self, obj, message):
        """
        Log an informational message.
        """
        self._log(obj, message, level=LOG_INFO)
        self.results[self.active_test]['info'] += 1

    def log_warning(self, obj, message):
        """
        Log a warning.
        """
        self._log(obj, message, level=LOG_WARNING)
        self.results[self.active_test]['warning'] += 1

    def log_failure(self, obj, message):
        """
        Log a failure. Calling this method will automatically mark the report as failed.
        """
        self._log(obj, message, level=LOG_FAILURE)
        self.results[self.active_test]['failed'] += 1
        self.failed = True

    def run(self):
        """
        Run the report and return its results. Each test method will be executed in order.
        """
        for method_name in self.test_methods:
            self.active_test = method_name
            test_method = getattr(self, method_name)
            test_method()

        return self.results
