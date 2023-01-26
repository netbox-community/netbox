import logging
import os
import subprocess
import tempfile
from functools import cached_property
from fnmatch import fnmatchcase
from urllib.parse import quote, urlunparse, urlparse

from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext as _

from utilities.files import sha256_hash
from .choices import *

__all__ = (
    'DataSource',
    'DataFile',
)

logger = logging.getLogger('netbox.core.data')


class DataSource(models.Model):
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
    url = models.CharField(
        max_length=200,
        verbose_name=_('URL')
    )
    ignore_rules = models.TextField(
        blank=True,
        help_text=_("Patterns (one per line) matching files to ignore when syncing")
    )
    username = models.CharField(
        max_length=100,
        blank=True
    )
    password = models.CharField(
        max_length=100,
        blank=True
    )
    git_branch = models.CharField(
        max_length=100,
        blank=True
    )

    class Meta:
        ordering = ('name',)

    def __str__(self):
        return f'{self.name} ({self.get_type_display()})'

    # def get_absolute_url(self):
    #     return reverse('core:datasource', args=[self.pk])

    def sync(self):
        """
        Create/update/delete child DataFiles as necessary to synchronize with the remote source.
        """
        # Replicate source data locally (if needed)
        temp_dir = tempfile.TemporaryDirectory()
        self.fetch(path=temp_dir.name)

        print(f'Syncing files from source root {temp_dir.name}')
        data_files = self.datafiles.all()
        known_paths = {df.path for df in data_files}

        # Check for any updated/deleted files
        updated_files = []
        deleted_file_ids = []
        for datafile in data_files:

            try:
                if datafile.refresh_from_disk(source_root=temp_dir.name):
                    updated_files.append(datafile)
            except FileNotFoundError:
                # File no longer exists
                deleted_file_ids.append(datafile.pk)
                continue

        # Bulk update modified files
        updated_count = DataFile.objects.bulk_update(updated_files, ['hash'])
        logger.debug(f"Updated {updated_count} data files")

        # Bulk delete deleted files
        deleted_count, _ = DataFile.objects.filter(pk__in=deleted_file_ids).delete()
        logger.debug(f"Deleted {updated_count} data files")

        # Walk the local replication to find new files
        new_paths = self._walk(temp_dir.name) - known_paths

        # Bulk create new files
        new_datafiles = []
        for path in new_paths:
            datafile = DataFile(source=self, path=path)
            datafile.refresh_from_disk(source_root=temp_dir.name)
            new_datafiles.append(datafile)
            # TODO: Record last_updated?
        created_count = len(DataFile.objects.bulk_create(new_datafiles, batch_size=100))
        logger.debug(f"Created {created_count} data files")

        temp_dir.cleanup()

    def fetch(self, path):
        """
        Replicate the file structure from the remote data source and return the local path.
        """
        logger.debug(f"Fetching source data for {self} ({self.get_type_display()})")
        try:
            fetch_method = getattr(self, f'fetch_{self.type}')
        except AttributeError:
            raise NotImplemented(f"fetch() not yet supported for {self.get_type_display()} data sources")

        return fetch_method(path)

    def fetch_local(self, path):
        """
        Skip fetching for local paths; return the source path directly.
        """
        logger.debug(f"Data source type is local; skipping fetch")
        return urlparse(self.url).path

    def fetch_git(self, path):
        """
        Perform a shallow clone of the remote repository using the `git` executable.
        """
        # Add authentication credentials to URL (if specified)
        if self.username and self.password:
            url_components = list(urlparse(self.url))
            # Prepend username & password to netloc
            url_components[1] = quote(f'{self.username}@{self.password}:') + url_components[1]
            url = urlunparse(url_components)
        else:
            url = self.url

        result = subprocess.run(['git', 'clone', '--depth', '1', url, path])

    def _walk(self, root_path):
        """
        Return a set of all non-excluded files within the root path.
        """
        paths = set()

        for path, dir_names, file_names in os.walk(root_path):
            path = path.split(root_path)[1].lstrip('/')  # Strip root path
            if path.startswith('.'):
                continue
            for file_name in file_names:
                if not self._ignore(file_name):
                    paths.add(os.path.join(path, file_name))

        logger.debug(f"Found {len(paths)} files")
        return paths

    def _ignore(self, filename):
        """
        Returns a boolean indicating whether the file should be ignored per the DataSource's configured
        ignore rules.
        """
        if filename.startswith('.'):
            return True
        for rule in self.ignore_rules.splitlines():
            if fnmatchcase(filename, rule):
                return True
        return False


class DataFile(models.Model):
    """
    A database object which represents a remote file fetched from a DataSource.
    """
    source = models.ForeignKey(
        to='core.DataSource',
        on_delete=models.CASCADE,
        related_name='datafiles',
        editable=False
    )
    path = models.CharField(
        max_length=1000,
        unique=True,
        editable=False
    )
    last_updated = models.DateTimeField(
        editable=False
    )
    size = models.PositiveIntegerField(
        editable=False
    )
    # TODO: Create a proper SHA256 field
    hash = models.CharField(
        max_length=64,
        editable=False
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

    def __str__(self):
        return self.path

    # def get_absolute_url(self):
    #     return reverse('core:datafile', args=[self.pk])

    def refresh_from_disk(self, source_root):
        """
        Update instance attributes from the file on disk. Returns True if any attribute
        has changed.
        """
        file_path = os.path.join(source_root, self.path)

        # Get attributes from file on disk
        file_size = os.path.getsize(file_path)
        file_hash = sha256_hash(file_path).hexdigest()

        # Update instance file attributes & data
        has_changed = file_size != self.size or file_hash != self.hash
        if has_changed:
            self.last_updated = timezone.now()
            self.size = file_size
            self.hash = file_hash
            with open(file_path, 'rb') as f:
                self.data = f.read()

        return has_changed
