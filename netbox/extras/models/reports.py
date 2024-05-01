import inspect
import logging
from functools import cached_property

from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from core.choices import ManagedFileRootPathChoices
from core.models import ManagedFile
from extras.utils import is_report
from netbox.models.features import JobsMixin, EventRulesMixin
from utilities.querysets import RestrictedQuerySet
from .mixins import PythonModuleMixin

logger = logging.getLogger('netbox.reports')

__all__ = (
    'Report',
    'ReportModule',
)


class Report(EventRulesMixin, models.Model):
    """
    Dummy model used to generate permissions for reports. Does not exist in the database.
    """
    class Meta:
        managed = False


class ReportModuleManager(models.Manager.from_queryset(RestrictedQuerySet)):

    def get_queryset(self):
        return super().get_queryset().filter(file_root=ManagedFileRootPathChoices.REPORTS)


class ReportModule(PythonModuleMixin, JobsMixin, ManagedFile):
    """
    Proxy model for report module files.
    """
    objects = ReportModuleManager()

    class Meta:
        proxy = True
        ordering = ('file_root', 'file_path')
        verbose_name = _('report module')
        verbose_name_plural = _('report modules')

    def get_absolute_url(self):
        return reverse('extras:report_list')

    def __str__(self):
        return self.python_name

    @property
    def reports(self):

        def _get_name(cls):
            # For child objects in submodules use the full import path w/o the root module as the name
            return cls.full_name.split(".", maxsplit=1)[1]

        try:
            module = self.get_module()
        except (ImportError, SyntaxError) as e:
            logger.error(f"Unable to load report module {self.name}, exception: {e}")
            return {}
        reports = {}
        ordered = getattr(module, 'report_order', [])

        for cls in ordered:
            reports[_get_name(cls)] = cls
        for name, cls in inspect.getmembers(module, is_report):
            if cls not in ordered:
                reports[_get_name(cls)] = cls

        return reports

    def save(self, *args, **kwargs):
        self.file_root = ManagedFileRootPathChoices.REPORTS
        return super().save(*args, **kwargs)
