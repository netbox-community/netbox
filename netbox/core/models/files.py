import logging
import os
from functools import cached_property

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.core.files.storage import storages
from django.urls import reverse
from django.utils.translation import gettext as _

from ..choices import ManagedFileRootPathChoices
from extras.storage import ScriptFileSystemStorage
from netbox.models.features import SyncedDataMixin
from utilities.querysets import RestrictedQuerySet

__all__ = (
    'ManagedFile',
)

logger = logging.getLogger('netbox.core.files')


class ManagedFile(SyncedDataMixin, models.Model):
    """
    Database representation for a file on disk. This class is typically wrapped by a proxy class (e.g. ScriptModule)
    to provide additional functionality.
    """
    created = models.DateTimeField(
        verbose_name=_('created'),
        auto_now_add=True
    )
    last_updated = models.DateTimeField(
        verbose_name=_('last updated'),
        editable=False,
        blank=True,
        null=True
    )
    file_root = models.CharField(
        verbose_name=_('file root'),
        max_length=1000,
        choices=ManagedFileRootPathChoices
    )
    file_path = models.FilePathField(
        verbose_name=_('file path'),
        editable=False,
        help_text=_('File path relative to the designated root path')
    )

    objects = RestrictedQuerySet.as_manager()
    _netbox_private = True

    class Meta:
        ordering = ('file_root', 'file_path')
        constraints = (
            models.UniqueConstraint(
                fields=('file_root', 'file_path'),
                name='%(app_label)s_%(class)s_unique_root_path'
            ),
        )
        verbose_name = _('managed file')
        verbose_name_plural = _('managed files')

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('core:managedfile', args=[self.pk])

    @property
    def name(self):
        return self.file_path

    @property
    def full_path(self):
        return os.path.join(self._resolve_root_path(), self.file_path)

    def _resolve_root_path(self):
        storage = self.storage
        if isinstance(storage, ScriptFileSystemStorage):
            return {
                'scripts': settings.SCRIPTS_ROOT,
                'reports': settings.REPORTS_ROOT,
            }[self.file_root]
        else:
            return ""

    def sync_data(self):
        if self.data_file:
            self.file_path = os.path.basename(self.data_path)

            storage = self.storage

            with storage.open(self.full_path, 'wb+') as new_file:
                new_file.write(self.data_file.data)

    @cached_property
    def storage(self):
        return storages.create_storage(storages.backends["scripts"])

    def clean(self):
        super().clean()

        if self.data_file and not self.file_path:
            self.file_path = os.path.basename(self.data_path)

        # Ensure that the file root and path make a unique pair
        if self._meta.model.objects.filter(
                file_root=self.file_root, file_path=self.file_path
        ).exclude(pk=self.pk).exists():
            raise ValidationError(
                _("A {model} with this file path already exists ({path}).").format(
                    model=self._meta.verbose_name.lower(),
                    path=f"{self.file_root}/{self.file_path}"
                ))

    def delete(self, *args, **kwargs):
        # Delete file from disk
        storage = self.storage
        try:
            storage.delete(self.full_path)
        except FileNotFoundError:
            pass

        return super().delete(*args, **kwargs)
