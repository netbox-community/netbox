import uuid

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError

from core.choices import JobStatusChoices
from ndx.importers import ImportAborted, import_entries
from ndx.jobs import SyncJob
from ndx.models import ImportRecord
from ndx.utils import is_enabled
from utilities.request import NetBoxFakeRequest, apply_request_processors


class Command(BaseCommand):
    help = "Check the NDX catalog for updates to imported entries, and optionally apply them"

    def add_arguments(self, parser):
        parser.add_argument(
            '--vendor',
            help="Limit the sync to entries from the specified vendor (slug)"
        )
        parser.add_argument(
            '--apply',
            action='store_true',
            help="Re-import entries for which an update is available"
        )
        parser.add_argument(
            '--user',
            help="The user to which the sync and any imported changes are attributed (required with --apply)"
        )

    def handle(self, *args, **options):
        if not is_enabled():
            raise CommandError("The NDX integration is not enabled. Set NDX_API_TOKEN to enable it.")

        if options['apply'] and not options['user']:
            raise CommandError("--user is required with --apply.")
        user = None
        if options['user']:
            try:
                user = get_user_model().objects.get(username=options['user'], is_active=True)
            except get_user_model().DoesNotExist:
                raise CommandError(f"Active user not found: {options['user']}")

        # Run the sync as a job, so that its outcome is reflected in the UI
        job = SyncJob.enqueue(immediate=True, user=user, vendor=options['vendor'])
        if job.status != JobStatusChoices.STATUS_COMPLETED:
            raise CommandError((job.data or {}).get('error') or job.error or f"Sync job {job.pk} {job.status}")
        result = job.data
        self.stdout.write(f"Authenticated to the NDX API (tier: {result['tier'] or 'unknown'})")
        self.stdout.write(
            f"{result['flagged']} record(s) flagged for update, {result['cleared']} flag(s) cleared, "
            f"{result['updates_available']} update(s) available"
        )

        if not options['apply'] or not result['updates_available']:
            return

        records = ImportRecord.objects.filter(update_available=True)
        if options['vendor']:
            records = records.filter(vendor_slug=options['vendor'])
        ndx_ids = list(records.values_list('ndx_id', flat=True))
        self.stdout.write(f"Applying {len(ndx_ids)} update(s)...")

        # Apply request processors so that changes are logged and attributed to the user
        request = NetBoxFakeRequest({
            'META': {},
            'COOKIES': {},
            'POST': {},
            'GET': {},
            'FILES': {},
            'user': user,
            'method': 'POST',
            'path': '',
            'id': uuid.uuid4(),
        })
        with apply_request_processors(request):
            try:
                results = import_entries(ndx_ids, user, callback=self.write_result)
            except ImportAborted as e:
                raise CommandError(str(e))

        statuses = [result.status for result in results]
        self.stdout.write(self.style.SUCCESS(
            f"Update complete: {statuses.count('updated') + statuses.count('created')} updated, "
            f"{statuses.count('skipped')} skipped, {statuses.count('failed')} failed"
        ))

    def write_result(self, result):
        if result.success:
            self.stdout.write(f"  {result.ndx_id}: {result.message}")
        else:
            message = result.message or '; '.join(map(str, result.errors))
            style = self.style.WARNING if result.skipped else self.style.ERROR
            self.stdout.write(style(f"  {result.ndx_id}: {message}"))
        for msg in [*result.warnings, *result.component_errors, *result.image_errors]:
            self.stdout.write(self.style.WARNING(f"  {result.ndx_id}: {msg}"))
