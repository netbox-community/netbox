from .scripts import BaseScript

__all__ = (
    'Report',
)


class Report(BaseScript):
    def log_success(self, obj=None, message=None):
        super().log_success(message, obj)

    def log_info(self, obj=None, message=None):
        super().log_info(message, obj)

    def log_warning(self, obj=None, message=None):
        super().log_warning(message, obj)

    def log_failure(self, obj=None, message=None):
        super().log_failure(message, obj)
