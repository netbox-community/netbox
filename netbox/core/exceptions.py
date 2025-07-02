from django.core.exceptions import ImproperlyConfigured

__all__ = (
    'IncompatiblePluginError',
    'JobFailed',
    'SyncError',
)


class IncompatiblePluginError(ImproperlyConfigured):
    pass


class JobFailed(Exception):
    pass


class SyncError(Exception):
    pass
