from django.core.exceptions import ImproperlyConfigured


class SyncError(Exception):
    pass


class IncompatiblePluginError(ImproperlyConfigured):
    pass
