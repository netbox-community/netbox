from .choices import LogLevelChoices
from .scripts import BaseScript

__all__ = (
    'Report',
)


# Required by extras/migrations/0109_script_models.py
class Report(BaseScript):

    #
    # Legacy logging methods for Reports
    #

    # There is no generic log() equivalent on BaseScript
    def log(self, message):
        self._log(message, None, level=LogLevelChoices.LOG_DEFAULT)

    def log_success(self, message=None, obj=None):
        self._log(message, obj, level=LogLevelChoices.LOG_SUCCESS)

    def log_info(self, message=None, obj=None):
        self._log(message, obj, level=LogLevelChoices.LOG_INFO)

    def log_warning(self, message=None, obj=None):
        self._log(message, obj, level=LogLevelChoices.LOG_WARNING)

    def log_failure(self, message=None, obj=None):
        self._log(message, obj, level=LogLevelChoices.LOG_FAILURE)

    # Added in v4.0 to avoid confusion with the log_debug() method provided by BaseScript
    def log_debug(self, message=None, obj=None):
        self._log(message, obj, level=LogLevelChoices.LOG_DEBUG)
