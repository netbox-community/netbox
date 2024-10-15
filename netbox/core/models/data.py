import hashlib
import logging
import os
from fnmatch import fnmatchcase
from urllib.parse import urlparse

import yaml
from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext as _

from netbox.constants import CENSOR_TOKEN, CENSOR_TOKEN_CHANGED
from netbox.models import PrimaryModel
from netbox.models.features import JobsMixin
from netbox.registry import registry
from utilities.querysets import RestrictedQuerySet
from ..choices import *
from ..exceptions import SyncError

__all__ = (
    'AutoSyncRecord',
    'DataFile',
    'DataSource',
)

logger = logging.getLogger('netbox.core.data')


class DataSource(JobsMixin, PrimaryModel):
    """
    A remote source, such as a git repository, from which DataFiles are synchronized.
    """
    name = models.CharField(
        verbose_name=_('name'),
        max_length=100,
        unique=True
    )
    type = models.CharField(
        verbose_name=_('type'),
        max_length=50
    )
    source_url = models.CharField(
        max_length=200,
        verbose_name=_('URL')
    )
    status = models.CharField(
        verbose_name=_('status'),
        max_length=50,
        choices=DataSourceStatusChoices,
        default=DataSourceStatusChoices.NEW,
        editable=False
    )
    enabled = models.BooleanField(
        verbose_name=_('enabled'),
        default=True
    )
    ignore_rules = models.TextField(
        verbose_name=_('ignore rules'),
        blank=True,
        help_text=_("Patterns (one per line) matching files to ignore when syncing")
    )
    parameters = models.JSONField(
        verbose_name=_('parameters'),
        blank=True,
        null=True
    )
    last_synced = models.DateTimeField(
        verbose_name=_('last synced'),
        blank=True,
        null=True,
        editable=False
    )

    class Meta:
        ordering = ('name',)
        verbose_name = _('data source')
        verbose_name_plural = _('data sources')

    def __str__(self):
        return f'{self.name}'

    def get_absolute_url(self):
        return reverse('core:datasource', args=[self.pk])

    @property
    def docs_url(self):
        return f'{settings.STATIC_URL}docs/models/{self._meta.app_label}/{self._meta.model_name}/'

    def get_type_display(self):
        if backend := registry['data_backends'].get(self.type):
            return backend.label

    def get_status_color(self):
        return DataSourceStatusChoices.colors.get(self.status)

    @property
    def url_scheme(self):
        return urlparse(self.source_url).scheme.lower()

    @property
    def backend_class(self):
        return registry['data_backends'].get(self.type)

    @property
    def ready_for_sync(self):
        return self.enabled and self.status not in (
            DataSourceStatusChoices.QUEUED,
            DataSourceStatusChoices.SYNCING
        )

    def clean(self):
        super().clean()

        # Validate data backend type
        if self.type and self.type not in registry['data_backends']:
            raise ValidationError({
                'type': _("Unknown backend type: {type}".format(type=self.type))
            })

        # Ensure URL scheme matches selected type
        if self.backend_class.is_local and self.url_scheme not in ('file', ''):
            raise ValidationError({
                'source_url': "URLs for local sources must start with file:// (or specify no scheme)"
            })

    def to_objectchange(self, action):
        objectchange = super().to_objectchange(action)

        # Censor any backend parameters marked as sensitive in the serialized data
        pre_change_params = {}
        post_change_params = {}
        if objectchange.prechange_data:
            pre_change_params = objectchange.prechange_data.get('parameters') or {}  # parameters may be None
        if objectchange.postchange_data:
            post_change_params = objectchange.postchange_data.get('parameters') or {}
        for param in self.backend_class.sensitive_parameters:
            if post_change_params.get(param):
                if post_change_params[param] != pre_change_params.get(param):
                    # Set the "changed" token if the parameter's value has been modified
                    post_change_params[param] = CENSOR_TOKEN_CHANGED
                else:
                    post_change_params[param] = CENSOR_TOKEN
            if pre_change_params.get(param):
                pre_change_params[param] = CENSOR_TOKEN

        return objectchange

    def get_backend(self):
        backend_params = self.parameters or {}
        return self.backend_class(self.source_url, **backend_params)

    def sync(self):
        """
        Create/update/delete child DataFiles as necessary to synchronize with the remote source.
        """
        from core.signals import post_sync, pre_sync

        if self.status == DataSourceStatusChoices.SYNCING:
            raise SyncError(_("Cannot initiate sync; syncing already in progress."))

        # Emit the pre_sync signal
        pre_sync.send(sender=self.__class__, instance=self)

        self.status = DataSourceStatusChoices.SYNCING
        DataSource.objects.filter(pk=self.pk).update(status=self.status)

        # Replicate source data locally
        try:
            backend = self.get_backend()
        except ModuleNotFoundError as e:
            raise SyncError(
                _("There was an error initializing the backend. A dependency needs to be installed: ") + str(e)
            )
        with backend.fetch() as local_path:

            logger.debug(f'Syncing files from source root {local_path}')
            data_files = self.datafiles.all()
            known_paths = {df.path for df in data_files}
            logger.debug(f'Starting with {len(known_paths)} known files')

            # Check for any updated/deleted files
            updated_files = []
            deleted_file_ids = []
            for datafile in data_files:

                try:
                    if datafile.refresh_from_disk(source_root=local_path):
                        updated_files.append(datafile)
                except FileNotFoundError:
                    # File no longer exists
                    deleted_file_ids.append(datafile.pk)
                    continue

            # Bulk update modified files
            updated_count = DataFile.objects.bulk_update(updated_files, ('last_updated', 'size', 'hash', 'data'))
            logger.debug(f"Updated {updated_count} files")

            # Bulk delete deleted files
            deleted_count, __ = DataFile.objects.filter(pk__in=deleted_file_ids).delete()
            logger.debug(f"Deleted {deleted_count} files")

            # Walk the local replication to find new files
            new_paths = self._walk(local_path) - known_paths

            # Bulk create new files
            new_datafiles = []
            for path in new_paths:
                datafile = DataFile(source=self, path=path)
                datafile.refresh_from_disk(source_root=local_path)
                datafile.full_clean()
                new_datafiles.append(datafile)
            created_count = len(DataFile.objects.bulk_create(new_datafiles, batch_size=100))
            logger.debug(f"Created {created_count} data files")

        # Update status & last_synced time
        self.status = DataSourceStatusChoices.COMPLETED
        self.last_synced = timezone.now()
        DataSource.objects.filter(pk=self.pk).update(status=self.status, last_synced=self.last_synced)

        # Emit the post_sync signal
        post_sync.send(sender=self.__class__, instance=self)
    sync.alters_data = True

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
    created = models.DateTimeField(
        verbose_name=_('created'),
        auto_now_add=True
    )
    last_updated = models.DateTimeField(
        verbose_name=_('last updated'),
        editable=False
    )
    source = models.ForeignKey(
        to='core.DataSource',
        on_delete=models.CASCADE,
        related_name='datafiles',
        editable=False
    )
    path = models.CharField(
        verbose_name=_('path'),
        max_length=1000,
        editable=False,
        help_text=_("File path relative to the data source's root")
    )
    size = models.PositiveIntegerField(
        editable=False,
        verbose_name=_('size')
    )
    hash = models.CharField(
        verbose_name=_('hash'),
        max_length=64,
        editable=False,
        validators=[
            RegexValidator(regex='^[0-9a-f]{64}$', message=_("Length must be 64 hexadecimal characters."))
        ],
        help_text=_('SHA256 hash of the file data')
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
        indexes = [
            models.Index(fields=('source', 'path'), name='core_datafile_source_path'),
        ]
        verbose_name = _('data file')
        verbose_name_plural = _('data files')

    def __str__(self):
        return self.path

    def get_absolute_url(self):
        return reverse('core:datafile', args=[self.pk])

    @property
    def data_as_string(self):
        if not self.data:
            return None
        try:
            return self.data.decode('utf-8')
        except UnicodeDecodeError:
            return None

    def get_data(self):
        """
        Attempt to read the file data as JSON/YAML and return a native Python object.
        """
        # TODO: Something more robust
        return yaml.safe_load(self.data_as_string)

    def refresh_from_disk(self, source_root):
        """
        Update instance attributes from the file on disk. Returns True if any attribute
        has changed.
        """
        file_path = os.path.join(source_root, self.path)
        with open(file_path, 'rb') as f:
            file_hash = hashlib.sha256(f.read()).hexdigest()

        # Update instance file attributes & data
        if is_modified := file_hash != self.hash:
            self.last_updated = timezone.now()
            self.size = os.path.getsize(file_path)
            self.hash = file_hash
            with open(file_path, 'rb') as f:
                self.data = f.read()

        return is_modified

    def write_to_disk(self, path, overwrite=False):
        """
        Write the object's data to disk at the specified path
        """
        # Check whether file already exists
        if os.path.isfile(path) and not overwrite:
            raise FileExistsError()

        with open(path, 'wb+') as new_file:
            new_file.write(self.data)


class AutoSyncRecord(models.Model):
    """
    Maps a DataFile to a synced object for efficient automatic updating.
    """
    datafile = models.ForeignKey(
        to=DataFile,
        on_delete=models.CASCADE,
        related_name='+'
    )
    object_type = models.ForeignKey(
        to='contenttypes.ContentType',
        on_delete=models.CASCADE,
        related_name='+'
    )
    object_id = models.PositiveBigIntegerField()
    object = GenericForeignKey(
        ct_field='object_type',
        fk_field='object_id'
    )

    _netbox_private = True

    class Meta:
        constraints = (
            models.UniqueConstraint(
                fields=('object_type', 'object_id'),
                name='%(app_label)s_%(class)s_object'
            ),
        )
        indexes = (
            models.Index(fields=('object_type', 'object_id')),
        )
        verbose_name = _('auto sync record')
        verbose_name_plural = _('auto sync records')
