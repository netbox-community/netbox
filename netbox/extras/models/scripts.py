import inspect
from functools import cached_property

from django.db import models
from django.urls import reverse

from core.choices import ManagedFileRootPathChoices
from core.models import ManagedFile
from extras.utils import is_script
from netbox.models.features import JobsMixin, WebhooksMixin
from utilities.querysets import RestrictedQuerySet
from .mixins import PythonModuleMixin

__all__ = (
    'Script',
    'ScriptModule',
)


class Script(WebhooksMixin, models.Model):
    """
    Dummy model used to generate permissions for custom scripts. Does not exist in the database.
    """
    class Meta:
        managed = False


class ScriptModuleManager(models.Manager.from_queryset(RestrictedQuerySet)):

    def get_queryset(self):
        return super().get_queryset().filter(file_root=ManagedFileRootPathChoices.SCRIPTS)


class ScriptModule(PythonModuleMixin, JobsMixin, ManagedFile):
    """
    Proxy model for script module files.
    """
    objects = ScriptModuleManager()

    class Meta:
        proxy = True

    def get_absolute_url(self):
        return reverse('extras:script_list')

    def __str__(self):
        return self.python_name

    @cached_property
    def scripts(self):

        def _get_name(cls):
            # For child objects in submodules use the full import path w/o the root module as the name
            return cls.full_name.split(".", maxsplit=1)[1]

        module = self.get_module()
        scripts = {}
        ordered = getattr(module, 'script_order', [])

        for cls in ordered:
            scripts[_get_name(cls)] = cls
        for name, cls in inspect.getmembers(module, is_script):
            if cls not in ordered:
                scripts[_get_name(cls)] = cls

        return scripts

    def save(self, *args, **kwargs):
        self.file_root = ManagedFileRootPathChoices.SCRIPTS
        return super().save(*args, **kwargs)
