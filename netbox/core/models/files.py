import logging
import os

from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext as _

from netbox.models.features import SyncedDataMixin
from utilities.querysets import RestrictedQuerySet

__all__ = (
    'ManagedFile',
)

logger = logging.getLogger('netbox.core.files')

ROOT_PATH_CHOICES = (
    ('scripts', 'Scripts Root'),
    ('reports', 'Reports Root'),
)


class ManagedFile(SyncedDataMixin, models.Model):
    """
    Database representation for a file on disk.
    """
    created = models.DateTimeField(
        auto_now_add=True
    )
    last_updated = models.DateTimeField(
        editable=False,
        blank=True,
        null=True
    )
    file_root = models.CharField(
        max_length=1000,
        choices=ROOT_PATH_CHOICES
    )
    file_path = models.FilePathField(
        editable=False,
        help_text=_("File path relative to the designated root path")
    )

    objects = RestrictedQuerySet.as_manager()

    class Meta:
        ordering = ('file_root', 'file_path')
        constraints = (
            models.UniqueConstraint(
                fields=('file_root', 'file_path'),
                name='%(app_label)s_%(class)s_unique_root_path'
            ),
        )
        indexes = [
            models.Index(fields=('file_root', 'file_path'), name='core_managedfile_root_path'),
        ]

    def __str__(self):
        return f'{self.get_file_root_display()}: {self.file_path}'

    def get_absolute_url(self):
        return reverse('core:managedfile', args=[self.pk])

    @property
    def full_path(self):
        return os.path.join(self._resolve_root_path(), self.file_path)

    def _resolve_root_path(self):
        return {
            'scripts': settings.SCRIPTS_ROOT,
            'reports': settings.REPORTS_ROOT,
        }[self.file_root]

    def sync_data(self):
        if self.data_file:
            self.file_path = self.data_path
            self.data_file.write_to_disk(self.full_path, overwrite=True)

    def delete(self, *args, **kwargs):
        # Delete file from disk
        os.remove(self.full_path)

        return super().delete(*args, **kwargs)
