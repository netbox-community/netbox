import logging
import os
from functools import cached_property
from urllib.parse import urlparse

from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext as _

from netbox.models import NetBoxModel, PrimaryModel
from utilities.files import sha256_checksum
from .choices import *

__all__ = (
    'DataSource',
    'DataFile',
)

logger = logging.getLogger('netbox.core.data')


class DataSource(PrimaryModel):
    """
    A remote source from which DataFiles are synchronized.
    """
    name = models.CharField(
        max_length=100,
        unique=True
    )
    type = models.CharField(
        max_length=50,
        choices=DataSourceTypeChoices,
        default=DataSourceTypeChoices.LOCAL
    )
    enabled = models.BooleanField(
        default=True
    )
    description = models.CharField(
        max_length=200,
        blank=True
    )
    url = models.URLField(
        verbose_name='URL'
    )

    class Meta:
        ordering = ('name',)

    # def get_absolute_url(self):
    #     return reverse('core:datasource', args=[self.pk])

    # @property
    # def root_path(self):
    #     if self.pk is None:
    #         return None
    #     if self.type == DataSourceTypeChoices.LOCAL:
    #         return self.url.lstrip('file://')
    #     return os.path.join(DATASOURCES_CACHE_PATH, str(self.pk))

    def sync(self):
        """
        Create/update/delete child DataFiles as necessary to synchronize with the remote source.
        """
        # Replicate source data locally (if needed)
        source_root = self.fetch()
        logger.debug(f'Syncing files from source root {source_root}')

        data_files = self.datafiles.all()
        known_paths = {df.path for df in data_files}

        # Check for any updated/deleted files
        updated_files = []
        deleted_file_ids = []
        for datafile in data_files:

            try:
                if datafile.refresh_from_disk(root_path=source_root):
                    updated_files.append(datafile)
            except FileNotFoundError:
                # File no longer exists
                deleted_file_ids.append(datafile.pk)
                continue

        # Bulk update modified files
        updated_count = DataFile.objects.bulk_update(updated_files, ['checksum'])
        logger.debug(f"Updated {updated_count} data files")

        # Bulk delete deleted files
        deleted_count, _ = DataFile.objects.filter(pk__in=deleted_file_ids).delete()
        logger.debug(f"Deleted {updated_count} data files")

        # Walk the local replication to find new files
        new_paths = self._walk(source_root) - known_paths

        # Bulk create new files
        new_datafiles = []
        for path in new_paths:
            datafile = DataFile(source=self, path=path)
            datafile.refresh_from_disk(root_path=source_root)
            new_datafiles.append(datafile)
            # TODO: Record last_updated?
        created_count = len(DataFile.objects.bulk_create(new_datafiles, batch_size=100))
        logger.debug(f"Created {created_count} data files")

    def fetch(self):
        """
        Replicate the file structure from the remote data source and return the local path.
        """
        logger.debug(f"Fetching source data for {self}")

        if self.type == DataSourceTypeChoices.LOCAL:
            logger.debug(f"Data source type is local; skipping fetch")
            # No replication is necessary for local sources
            return urlparse(self.url).path

        raise NotImplemented(f"fetch() not yet supported for {self.get_type_display()} data sources")

        # TODO: Sync remote files to tempfile.TemporaryDirectory

    def _walk(self, root_path):
        """
        Return a set of all non-excluded files within the root path.
        """
        paths = set()

        for path, dir_names, file_names in os.walk(root_path):
            path = path.split(root_path)[1]  # Strip root path
            path.lstrip('/')
            if path.startswith('.'):
                continue
            for file_name in file_names:
                # TODO: Apply include/exclude rules
                if file_name.startswith('.'):
                    continue
                paths.add(os.path.join(path, file_name))

        logger.debug(f"Found {len(paths)} files")
        return paths


class DataFile(NetBoxModel):
    """
    A database object which represents a remote file fetched from a DataSource.
    """
    source = models.ForeignKey(
        to='core.DataSource',
        on_delete=models.CASCADE,
        related_name='datafiles'
    )
    path = models.CharField(
        max_length=1000,
        unique=True
    )
    last_updated = models.DateTimeField()
    size = models.PositiveIntegerField()
    # TODO: Create a proper SHA256 field
    checksum = models.CharField(
        max_length=64
    )
    data = models.BinaryField()

    class Meta:
        ordering = ('source', 'path')
        constraints = (
            models.UniqueConstraint(
                fields=('source', 'path'),
                name='%(app_label)s_%(class)s_unique_source_path'
            ),
        )

    # def get_absolute_url(self):
    #     return reverse('core:datafile', args=[self.pk])

    def refresh_from_disk(self, root_path):
        """
        Update instance attributes from the file on disk. Returns True if any attribute
        has changed.
        """
        file_path = os.path.join(root_path, self.path)

        # Get attributes from file on disk
        file_size = os.path.getsize(file_path)
        file_checksum = sha256_checksum(file_path)

        # Update instance file attributes & data
        has_changed = file_size != self.size or file_checksum != self.checksum
        if has_changed:
            self.last_updated = timezone.now()
            self.size = file_size
            self.checksum = file_checksum
            with open(file_path, 'rb') as f:
                self.data = f.read()

        return has_changed
