import logging
import os
import subprocess
import tempfile
from fnmatch import fnmatchcase
from urllib.parse import quote, urlunparse, urlparse

from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.module_loading import import_string
from django.utils.translation import gettext as _

from extras.models import JobResult
from netbox.models import ChangeLoggedModel
from utilities.files import sha256_hash
from utilities.querysets import RestrictedQuerySet
from ..choices import *
from ..exceptions import SyncError
from ..utils import FakeTempDirectory

__all__ = (
    'DataSource',
    'DataFile',
)

logger = logging.getLogger('netbox.core.data')


class DataSource(ChangeLoggedModel):
    """
    A remote source, such as a git repository, from which DataFiles are synchronized.
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
    url = models.CharField(
        max_length=200,
        verbose_name=_('URL')
    )
    status = models.CharField(
        max_length=50,
        choices=DataSourceStatusChoices,
        default=DataSourceStatusChoices.NEW,
        editable=False
    )
    enabled = models.BooleanField(
        default=True
    )
    description = models.CharField(
        max_length=200,
        blank=True
    )
    git_branch = models.CharField(
        max_length=100,
        blank=True,
        help_text=_("Branch to check out for git sources (if not using the default)")
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
    last_synced = models.DateTimeField(
        blank=True,
        null=True,
        editable=False
    )

    class Meta:
        ordering = ('name',)

    def __str__(self):
        return f'{self.name}'

    def get_absolute_url(self):
        return reverse('core:datasource', args=[self.pk])

    def get_type_color(self):
        return DataSourceTypeChoices.colors.get(self.type)

    def get_status_color(self):
        return DataSourceStatusChoices.colors.get(self.status)

    @property
    def ready_for_sync(self):
        return self.enabled and self.status not in (
            DataSourceStatusChoices.QUEUED,
            DataSourceStatusChoices.SYNCING
        )

    def clean(self):

        # Ensure URL scheme matches selected type
        url_scheme = urlparse(self.url)
        if self.type == DataSourceTypeChoices.LOCAL and url_scheme not in ('file', ''):
            raise ValidationError({
                'url': f"URLs for local sources must start with file:// (or omit the scheme)"
            })

    def enqueue_sync_job(self, request):
        """
        Enqueue a background job to synchronize the DataSource by calling sync().
        """
        # Set the status to "syncing"
        self.status = DataSourceStatusChoices.QUEUED

        # Enqueue a sync job
        job_result = JobResult.enqueue_job(
            import_string('core.jobs.sync_datasource'),
            name=self.name,
            obj_type=ContentType.objects.get_for_model(DataSource),
            user=request.user,
        )

        return job_result

    def sync(self):
        """
        Create/update/delete child DataFiles as necessary to synchronize with the remote source.
        """
        if not self.ready_for_sync:
            raise SyncError(f"Cannot initiate sync; data source not ready/enabled")

        self.status = DataSourceStatusChoices.SYNCING
        DataSource.objects.filter(pk=self.pk).update(status=self.status)

        # Replicate source data locally (if needed)
        local_path = self.fetch()

        logger.debug(f'Syncing files from source root {local_path.name}')
        data_files = self.datafiles.all()
        known_paths = {df.path for df in data_files}
        logger.debug(f'Starting with {len(known_paths)} known files')

        # Check for any updated/deleted files
        updated_files = []
        deleted_file_ids = []
        for datafile in data_files:

            try:
                if datafile.refresh_from_disk(source_root=local_path.name):
                    updated_files.append(datafile)
            except FileNotFoundError:
                # File no longer exists
                deleted_file_ids.append(datafile.pk)
                continue

        # Bulk update modified files
        updated_count = DataFile.objects.bulk_update(updated_files, ['hash'])
        logger.debug(f"Updated {updated_count} files")

        # Bulk delete deleted files
        deleted_count, _ = DataFile.objects.filter(pk__in=deleted_file_ids).delete()
        logger.debug(f"Deleted {updated_count} files")

        # Walk the local replication to find new files
        new_paths = self._walk(local_path.name) - known_paths

        # Bulk create new files
        new_datafiles = []
        for path in new_paths:
            datafile = DataFile(source=self, path=path)
            datafile.refresh_from_disk(source_root=local_path.name)
            datafile.full_clean()
            new_datafiles.append(datafile)
        created_count = len(DataFile.objects.bulk_create(new_datafiles, batch_size=100))
        logger.debug(f"Created {created_count} data files")

        # Update status & last_synced time
        self.status = DataSourceStatusChoices.COMPLETED
        self.last_updated = timezone.now()
        DataSource.objects.filter(pk=self.pk).update(status=self.status, last_updated=self.last_updated)

        local_path.cleanup()

    def fetch(self):
        """
        Replicate the file structure from the remote data source and return the local path.
        """
        logger.debug(f"Fetching source data for {self} ({self.get_type_display()})")
        try:
            fetch_method = getattr(self, f'fetch_{self.type}')
        except AttributeError:
            raise NotImplemented(f"fetch() not yet supported for {self.get_type_display()} data sources")

        return fetch_method()

    def fetch_local(self, path):
        """
        Skip fetching for local paths; return the source path directly.
        """
        logger.debug(f"Data source type is local; skipping fetch")
        local_path = urlparse(self.url).path

        return FakeTempDirectory(local_path)

    def fetch_git(self):
        """
        Perform a shallow clone of the remote repository using the `git` executable.
        """
        local_path = tempfile.TemporaryDirectory()

        # Add authentication credentials to URL (if specified)
        if self.username and self.password:
            url_components = list(urlparse(self.url))
            # Prepend username & password to netloc
            url_components[1] = quote(f'{self.username}@{self.password}:') + url_components[1]
            url = urlunparse(url_components)
        else:
            url = self.url

        # Compile git arguments
        args = ['git', 'clone', '--depth', '1']
        if self.git_branch:
            args.extend(['--branch', self.git_branch])
        args.extend([url, local_path.name])

        logger.debug(f"Cloning git repo: {' '.join(args)}")
        try:
            subprocess.run(args, check=True, capture_output=True)
        except subprocess.CalledProcessError as e:
            raise SyncError(
                f"Fetching remote data failed: {e.stderr}"
            )

        return local_path

    def _walk(self, root):
        """
        Return a set of all non-excluded files within the root path.
        """
        logger.debug(f"Walking {root}...")
        paths = set()

        for path, dir_names, file_names in os.walk(root):
            path = path.split(root)[1].lstrip('/')  # Strip root path
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
    The database representation of a remote file fetched from a remote DataSource. DataFile instances should be created,
    updated, or deleted only by calling DataSource.sync().
    """
    source = models.ForeignKey(
        to='core.DataSource',
        on_delete=models.CASCADE,
        related_name='datafiles',
        editable=False
    )
    path = models.CharField(
        max_length=1000,
        editable=False,
        help_text=_("File path relative to the data source's root")
    )
    last_updated = models.DateTimeField(
        editable=False
    )
    size = models.PositiveIntegerField(
        editable=False
    )
    hash = models.CharField(
        max_length=64,
        editable=False,
        validators=[
            RegexValidator(regex='^[0-9a-f]{64}$', message=_("Length must be 64 hexadecimal characters."))
        ],
        help_text=_("SHA256 hash of the file data")
    )
    data = models.BinaryField()

    objects = RestrictedQuerySet.as_manager()

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

    def get_absolute_url(self):
        return reverse('core:datafile', args=[self.pk])

    @property
    def data_as_string(self):
        try:
            return self.data.tobytes().decode('utf-8')
        except UnicodeDecodeError:
            return None

    def refresh_from_disk(self, source_root):
        """
        Update instance attributes from the file on disk. Returns True if any attribute
        has changed.
        """
        file_path = os.path.join(source_root, self.path)
        file_hash = sha256_hash(file_path).hexdigest()

        # Update instance file attributes & data
        if is_modified := file_hash != self.hash:
            self.last_updated = timezone.now()
            self.size = os.path.getsize(file_path)
            self.hash = file_hash
            with open(file_path, 'rb') as f:
                self.data = f.read()

        return is_modified
