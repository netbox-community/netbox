from datetime import timedelta
from importlib import import_module

from django.conf import settings
from django.core.management.base import BaseCommand
from django.db import DEFAULT_DB_ALIAS
from django.utils import timezone

from extras.models import ObjectChange


class Command(BaseCommand):
    help = "Perform nightly housekeeping tasks. (This command can be run at any time.)"

    def handle(self, *args, **options):

        # Clear expired authentication sessions (essentially replicating the `clearsessions` command)
        self.stdout.write("[*] Clearing expired authentication sessions")
        if options['verbosity'] >= 2:
            self.stdout.write(f"\tConfigured session engine: {settings.SESSION_ENGINE}")
        engine = import_module(settings.SESSION_ENGINE)
        try:
            engine.SessionStore.clear_expired()
            self.stdout.write("\tSessions cleared.", self.style.SUCCESS)
        except NotImplementedError:
            self.stdout.write(
                f"\tThe configured session engine ({settings.SESSION_ENGINE}) does not support "
                f"clearing sessions; skipping."
            )

        # Delete expired ObjectRecords
        self.stdout.write("[*] Checking for expired changelog records")
        if settings.CHANGELOG_RETENTION:
            cutoff = timezone.now() - timedelta(days=settings.CHANGELOG_RETENTION)
            if options['verbosity'] >= 2:
                self.stdout.write(f"Retention period: {settings.CHANGELOG_RETENTION} days")
                self.stdout.write(f"\tCut-off time: {cutoff}")
            expired_records = ObjectChange.objects.filter(time__lt=cutoff).count()
            if expired_records:
                self.stdout.write(f"\tDeleting {expired_records} expired records... ", self.style.WARNING, ending="")
                self.stdout.flush()
                ObjectChange.objects.filter(time__lt=cutoff)._raw_delete(using=DEFAULT_DB_ALIAS)
                self.stdout.write("Done.", self.style.WARNING)
            else:
                self.stdout.write("\tNo expired records found.")
        else:
            self.stdout.write(
                f"\tSkipping: No retention period specified (CHANGELOG_RETENTION = {settings.CHANGELOG_RETENTION})"
            )

        self.stdout.write("Finished.", self.style.SUCCESS)
