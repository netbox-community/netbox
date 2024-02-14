import inspect
import logging
from functools import cached_property

from django.contrib.contenttypes.fields import GenericRelation
from django.db import models
from django.db.models import Q
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from core.choices import ManagedFileRootPathChoices
from core.models import ManagedFile
from extras.utils import is_script
from netbox.models.features import JobsMixin, EventRulesMixin
from utilities.querysets import RestrictedQuerySet
from .mixins import PythonModuleMixin

__all__ = (
    'Script',
    'ScriptModule',
)

logger = logging.getLogger('netbox.data_backends')


class Script(EventRulesMixin, JobsMixin, models.Model):
    name = models.CharField(
        verbose_name=_('name'),
        max_length=79,  # Maximum length for a Python class name
    )
    module = models.ForeignKey(
        to='extras.ScriptModule',
        on_delete=models.CASCADE,
        related_name='scripts'
    )
    is_executable = models.BooleanField(
        default=True,
        verbose_name=_('is executable')
    )
    events = GenericRelation(
        'extras.EventRule',
        content_type_field='action_object_type',
        object_id_field='action_object_id'
    )

    def __str__(self):
        return self.name

    class Meta:
        ordering = ('module', 'name')
        constraints = (
            models.UniqueConstraint(
                fields=('name', 'module'),
                name='%(app_label)s_%(class)s_unique_name_module'
            ),
        )
        verbose_name = _('script')
        verbose_name_plural = _('scripts')

    def get_absolute_url(self):
        return reverse('extras:script', args=[self.pk])

    @cached_property
    def python_class(self):
        return self.module.get_module_scripts.get(self.name)

    def delete_if_no_jobs(self):
        if self.jobs.all():
            self.is_executable = False
            self.save()
        else:
            self.delete()
            self.id = None


class ScriptModuleManager(models.Manager.from_queryset(RestrictedQuerySet)):

    def get_queryset(self):
        return super().get_queryset().filter(
            Q(file_root=ManagedFileRootPathChoices.SCRIPTS) | Q(file_root=ManagedFileRootPathChoices.REPORTS))


class ScriptModule(PythonModuleMixin, JobsMixin, ManagedFile):
    """
    Proxy model for script module files.
    """
    objects = ScriptModuleManager()

    class Meta:
        proxy = True
        verbose_name = _('script module')
        verbose_name_plural = _('script modules')

    def get_absolute_url(self):
        return reverse('extras:script_list')

    def __str__(self):
        return self.python_name

    @cached_property
    def get_module_scripts(self):

        def _get_name(cls):
            # For child objects in submodules use the full import path w/o the root module as the name
            return cls.full_name.split(".", maxsplit=1)[1]

        try:
            module = self.get_module()
        except Exception as e:
            logger.debug(f"Failed to load script: {self.python_name} error: {e}")
            module = None

        scripts = {}
        ordered = getattr(module, 'script_order', [])

        for cls in ordered:
            scripts[_get_name(cls)] = cls
        for name, cls in inspect.getmembers(module, is_script):
            if cls not in ordered:
                scripts[_get_name(cls)] = cls

        return scripts

    def sync_classes(self):
        db_classes = {}
        for obj in self.scripts.filter(module=self):
            db_classes[obj.name] = obj

        db_classes_set = {k for k in db_classes.keys()}

        module_scripts = self.get_module_scripts

        module_classes_set = {k for k in module_scripts.keys()}

        # remove any existing db classes if they are no longer in the file
        removed = db_classes_set - module_classes_set
        for name in removed:
            db_classes[name].delete_if_no_jobs()

        added = module_classes_set - db_classes_set
        for name in added:
            Script.objects.create(
                module=self,
                name=name,
                is_executable=True,
            )

    def sync_data(self):
        super().sync_data()
        self.sync_classes()

    def save(self, *args, **kwargs):
        self.file_root = ManagedFileRootPathChoices.SCRIPTS
        super().save(*args, **kwargs)
        self.sync_classes()
