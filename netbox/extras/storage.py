from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.utils.functional import cached_property


class ScriptFileSystemStorage(FileSystemStorage):

    @cached_property
    def base_location(self):
        return settings.SCRIPTS_ROOT
