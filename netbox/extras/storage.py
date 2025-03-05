from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.utils.functional import cached_property


class ScriptFileSystemStorage(FileSystemStorage):
    """
    Custom storage for scripts - for django-storages as the default one will
    go off media-root and raise security errors as the scripts can be outside
    the media-root directory.
    """
    @cached_property
    def base_location(self):
        return settings.SCRIPTS_ROOT
