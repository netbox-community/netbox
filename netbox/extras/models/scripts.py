import inspect
import logging
from functools import cached_property

from django.contrib.contenttypes.fields import GenericRelation
from django.db import models
from django.db.models import Q
from django.db.models.signals import post_save
from django.dispatch import receiver
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


class Script(EventRulesMixin, JobsMixin):
    name = models.CharField(
        verbose_name=_('name'),
        max_length=79,  # Maximum length for a Python class name
        editable=False,
    )
    module = models.ForeignKey(
        to='extras.ScriptModule',
        on_delete=models.CASCADE,
        related_name='scripts',
        editable=False
    )
    is_executable = models.BooleanField(
        default=True,
        verbose_name=_('is executable'),
        editable=False
    )
    events = GenericRelation(
        'extras.EventRule',
        content_type_field='action_object_type',
        object_id_field='action_object_id'
    )

    def __str__(self):
        return self.name

    objects = RestrictedQuerySet.as_manager()

    class Meta:
        ordering = ('module', 'name')
        constraints = (
            models.UniqueConstraint(
                fields=('name', 'module'),
                name='extras_script_unique_name_module'
            ),
        )
        verbose_name = _('script')
        verbose_name_plural = _('scripts')

    def get_absolute_url(self):
        return reverse('extras:script', args=[self.pk])

    @property
    def result(self):
        return self.jobs.all().order_by('-created').first()

    @cached_property
    def python_class(self):
        return self.module.module_scripts.get(self.name)

    def delete(self, soft_delete=False, **kwargs):
        if soft_delete and self.jobs.exists():
            self.is_executable = False
            self.save()
        else:
            super().delete(**kwargs)
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
    error = None

    event_rules = GenericRelation(
        to='extras.EventRule',
        content_type_field='action_object_type',
        object_id_field='action_object_id',
        for_concrete_model=False
    )

    class Meta:
        proxy = True
        ordering = ('file_root', 'file_path')
        verbose_name = _('script module')
        verbose_name_plural = _('script modules')

    def get_absolute_url(self):
        return reverse('extras:script_list')

    def __str__(self):
        return self.python_name

    @property
    def module_scripts(self):

        def _get_name(cls):
            # For child objects in submodules use the full import path w/o the root module as the name
            return cls.full_name.split(".", maxsplit=1)[1]

        try:
            module = self.get_module()
        except Exception as e:
            self.error = e
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
        """
        Syncs the file-based module to the database, adding and removing individual Script objects
        in the database as needed.
        """
        if self.id:
            db_classes = {
                script.name: script for script in self.scripts.all()
            }
        else:
            db_classes = {}

        db_classes_set = set(db_classes.keys())
        module_classes_set = set(self.module_scripts.keys())

        # remove any existing db classes if they are no longer in the file
        removed = db_classes_set - module_classes_set
        for name in removed:
            db_classes[name].delete(soft_delete=True)

        added = module_classes_set - db_classes_set
        for name in added:
            Script.objects.create(
                module=self,
                name=name,
                is_executable=True,
            )

    def sync_data(self):
        super().sync_data()

    def save(self, *args, **kwargs):
        self.file_root = ManagedFileRootPathChoices.SCRIPTS
        super().save(*args, **kwargs)
        self.sync_classes()


@receiver(post_save, sender=ScriptModule)
def script_module_post_save_handler(instance, created, **kwargs):
    instance.sync_classes()
