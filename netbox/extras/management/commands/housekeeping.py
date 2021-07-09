from datetime import timedelta
from importlib import import_module

import requests
from django.conf import settings
from django.core.cache import cache
from django.core.management.base import BaseCommand
from django.db import DEFAULT_DB_ALIAS
from django.utils import timezone
from packaging import version

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

        # Check for new releases (if enabled)
        self.stdout.write("[*] Checking for latest release")
        if settings.RELEASE_CHECK_URL:
            headers = {
                'Accept': 'application/vnd.github.v3+json',
            }

            try:
                self.stdout.write(f"\tFetching {settings.RELEASE_CHECK_URL}")
                response = requests.get(
                    url=settings.RELEASE_CHECK_URL,
                    headers=headers,
                    proxies=settings.HTTP_PROXIES
                )
                response.raise_for_status()

                releases = []
                for release in response.json():
                    if 'tag_name' not in release or release.get('devrelease') or release.get('prerelease'):
                        continue
                    releases.append((version.parse(release['tag_name']), release.get('html_url')))
                latest_release = max(releases)
                self.stdout.write(f"\tFound {len(response.json())} releases; {len(releases)} usable")
                self.stdout.write(f"\tLatest release: {latest_release[0]}")

                # Cache the most recent release
                cache.set('latest_release', latest_release, None)

            except requests.exceptions.RequestException as exc:
                self.stdout.write(f"\tRequest error: {exc}")
        else:
            self.stdout.write(f"\tSkipping: RELEASE_CHECK_URL not set")

        self.stdout.write("Finished.", self.style.SUCCESS)
