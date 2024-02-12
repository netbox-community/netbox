from .choices import LogLevelChoices
from .scripts import BaseScript

__all__ = (
    'Report',
)


class Report(BaseScript):

    #
    # Legacy logging methods for Reports
    #

    # There is no generic log() equivalent on BaseScript
    def log(self, message):
        self._log(message, None, level=LogLevelChoices.LOG_DEFAULT)

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
