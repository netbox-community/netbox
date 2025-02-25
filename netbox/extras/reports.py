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
        self._log(message, None, level=LogLevelChoices.LOG_INFO)

    def log_success(self, obj=None, message=None):
        super().log_success(message, obj)

    def log_info(self, obj=None, message=None):
        super().log_info(message, obj)

    def log_warning(self, obj=None, message=None):
        super().log_warning(message, obj)

    def log_failure(self, obj=None, message=None):
        super().log_failure(message, obj)

    # Added in v4.0 to avoid confusion with the log_debug() method provided by BaseScript
    def log_debug(self, obj=None, message=None):
        super().log_debug(message, obj)
