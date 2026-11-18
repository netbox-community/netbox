from django.conf import settings
from django.contrib.auth import get_user_model
from django.db.models import Q
from django.utils.translation import gettext_lazy as _

from core.choices import JobStatusChoices
from core.exceptions import JobFailed
from netbox.jobs import JobRunner, system_job
from netbox.settings_utils import parse_job_timeout
from utilities.request import apply_request_processors, copy_safe_request

from .client import error_of, get_client
from .constants import IMPORT_JOB_TIMEOUT_PER_ENTRY
from .utils import is_enabled

__all__ = (
    'ImportJob',
    'SyncFailed',
    'SyncJob',
    'get_active_sync_job',
    'get_last_sync_job',
    'register_sync_job',
    'sync_catalog',
)


class SyncFailed(Exception):
    """
    Raised when the NDX catalog cannot be checked for changes.
    """


def sync_catalog(client, vendor=None, logger=None):
    """
    Check the NDX catalog for changes to imported entries (optionally limited to a single vendor), flagging records
    for which an update is available and clearing the flag on any which are current. Returns a summary of the sync.
    Raises SyncFailed if the catalog cannot be checked.
    """
    from .models import ImportRecord

    # Verify the configured token
    auth = client.verify_auth()
    if error := error_of(auth):
        raise SyncFailed(error.message)
    tier = auth.get('tier', '')
    if logger:
        logger.info(f"Authenticated to the NDX API (tier: {tier or 'unknown'})")

    # Retrieve per-vendor checksums from the catalog manifest
    manifest = client.get_manifest()
    if error := error_of(manifest):
        raise SyncFailed(error.message)
    checksums = {
        slug: checksum for slug, checksum in (manifest.get('vendor_checksums') or {}).items() if checksum
    }
    if not checksums:
        # Without checksums, every record would compare as current
        raise SyncFailed(_("The NDX API returned no vendor checksums; update flags were left unchanged."))

    catalog_count = client.check_sync().get('total_count')

    # Flag records whose vendor's checksum has changed since they were imported, and clear the flag on any which
    # now match (or whose vendor no longer appears in the manifest). A record without a checksum (e.g. imported while
    # the manifest was rate-limited) can't be compared, and is not flagged. Queryset updates are used intentionally:
    # flags are catalog metadata and are not change-logged.
    stale = Q()
    for vendor_slug, checksum in checksums.items():
        stale |= Q(vendor_slug=vendor_slug) & ~Q(checksum=checksum)
    stale &= ~Q(checksum='')
    records = ImportRecord.objects.all()
    if vendor:
        records = records.filter(vendor_slug=vendor)
    flagged = records.filter(stale, update_available=False).update(update_available=True)
    cleared = records.filter(update_available=True).exclude(stale).update(update_available=False)

    return {
        'tier': tier,
        'catalog_count': catalog_count,
        'imported_count': records.count(),
        'updates_available': records.filter(update_available=True).count(),
        'flagged': flagged,
        'cleared': cleared,
    }


class SyncJob(JobRunner):
    """
    Check the NDX catalog for changes to imported entries. Updates are flagged but never applied automatically.
    """
    class Meta:
        name = 'NDX Catalog Sync'

    def run(self, *args, vendor=None, **kwargs):
        if not is_enabled():
            self.logger.info("The NDX integration is disabled; skipping catalog sync.")
            return

        try:
            self.job.data = sync_catalog(get_client(), vendor=vendor, logger=self.logger)
            if vendor:
                self.job.data['vendor'] = vendor
        except SyncFailed as e:
            # Record the reason for display on the sync status page
            self.job.data = {'error': str(e)}
            self.logger.error(str(e))
            raise JobFailed(str(e))

        self.logger.info(
            f"Catalog sync complete: {self.job.data['flagged']} record(s) flagged for update, "
            f"{self.job.data['cleared']} flag(s) cleared, {self.job.data['updates_available']} update(s) available"
        )


class ImportJob(JobRunner):
    """
    Import entries from the NDX catalog in the background.
    """
    class Meta:
        name = 'NDX Import'

    @classmethod
    def enqueue_for(cls, request, ndx_ids):
        """
        Queue a job to import the given catalog entries on behalf of the request's user. The job's timeout is raised
        from the default in proportion to the number of entries.
        """
        kwargs = {}
        default_timeout = parse_job_timeout(settings.RQ_DEFAULT_TIMEOUT)
        if default_timeout is not None:
            kwargs['job_timeout'] = max(default_timeout, IMPORT_JOB_TIMEOUT_PER_ENTRY * len(ndx_ids))
        return cls.enqueue(
            name=_('NDX import ({count} entries)').format(count=len(ndx_ids)),
            user=request.user,
            ndx_ids=ndx_ids,
            request=copy_safe_request(request, include_files=False),
            **kwargs,
        )

    def run(self, ndx_ids, request, *args, **kwargs):
        from .importers import ImportAborted, import_entries

        # Attribute changes to the current user record rather than the copy which was pickled at enqueue time
        user = get_user_model().objects.filter(pk=self.job.user_id, is_active=True).first()
        if user is None:
            raise JobFailed(_("The requesting user no longer exists or is inactive."))
        request.user = user
        request.job = self

        # Record each result as it completes, so that the outcome of each entry survives an interrupted job
        self.job.data = {'results': []}

        def record_result(result):
            log = self.logger.info if result.success or result.skipped else self.logger.error
            log(f"{result.ndx_id}: {result.message or '; '.join(map(str, result.errors))}")
            for msg in [*result.warnings, *result.component_errors, *result.image_errors]:
                self.logger.warning(f"{result.ndx_id}: {msg}")
            self.job.data['results'].append(result.serialize())
            self.job.save(update_fields=['data', 'log_entries'])

        # Apply request processors (e.g. change logging) as for the original request
        with apply_request_processors(request):
            try:
                results = import_entries(ndx_ids, user, callback=record_result)
            except ImportAborted as e:
                self.logger.error(str(e))
                raise JobFailed(str(e))

        statuses = [result.status for result in results]
        self.logger.info(
            f"Import complete: {statuses.count('created')} created, {statuses.count('updated')} updated, "
            f"{statuses.count('skipped')} skipped, {statuses.count('failed')} failed"
        )


def register_sync_job():
    """
    Register the periodic catalog sync as a system job, if the integration is enabled.
    """
    if is_enabled() and settings.NDX_SYNC_INTERVAL:
        system_job(interval=settings.NDX_SYNC_INTERVAL)(SyncJob)


def get_active_sync_job():
    """
    Return the catalog sync job which is pending or running, if any.
    """
    return SyncJob.get_jobs().filter(
        status__in=(JobStatusChoices.STATUS_PENDING, JobStatusChoices.STATUS_RUNNING)
    ).first()


def get_last_sync_job():
    """
    Return the most recent completed (or failed) catalog sync job of the entire catalog, if any.
    """
    from core.models import Job

    return Job.objects.filter(
        name=SyncJob.name,
        status__in=JobStatusChoices.TERMINAL_STATE_CHOICES,
    ).exclude(
        # Ignore syncs limited to a single vendor
        data__has_key='vendor'
    ).order_by('-completed').first()
