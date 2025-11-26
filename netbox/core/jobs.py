import sys
from datetime import timedelta
from importlib import import_module

import requests
from django.conf import settings
from django.core.cache import cache
from django.utils import timezone
from packaging import version

from core.models import Job, ObjectChange
from netbox.config import Config
from netbox.jobs import JobRunner, system_job
from netbox.search.backends import search_backend
from utilities.proxy import resolve_proxies
from .choices import DataSourceStatusChoices, JobIntervalChoices
from .models import DataSource


class SyncDataSourceJob(JobRunner):
    """
    Call sync() on a DataSource.
    """

    class Meta:
        name = 'Synchronization'

    @classmethod
    def enqueue(cls, *args, **kwargs):
        job = super().enqueue(*args, **kwargs)

        # Update the DataSource's synchronization status to queued
        if datasource := job.object:
            datasource.status = DataSourceStatusChoices.QUEUED
            DataSource.objects.filter(pk=datasource.pk).update(status=datasource.status)

        return job

    def run(self, *args, **kwargs):
        datasource = DataSource.objects.get(pk=self.job.object_id)
        self.logger.debug(f"Found DataSource ID {datasource.pk}")

        try:
            self.logger.info(f"Syncing data source {datasource}")
            datasource.sync()

            # Update the search cache for DataFiles belonging to this source
            self.logger.debug("Updating search cache for data files")
            search_backend.cache(datasource.datafiles.iterator())

        except Exception as e:
            self.logger.error(f"Error syncing data source: {e}")
            DataSource.objects.filter(pk=datasource.pk).update(status=DataSourceStatusChoices.FAILED)
            raise e

        self.logger.info("Syncing completed successfully")


@system_job(interval=JobIntervalChoices.INTERVAL_DAILY)
class SystemHousekeepingJob(JobRunner):
    """
    Perform daily system housekeeping functions.
    """
    class Meta:
        name = "System Housekeeping"

    def run(self, *args, **kwargs):
        # Skip if running in development or test mode
        if settings.DEBUG:
            self.logger.warning("Aborting execution: Debug is enabled")
            return
        if 'test' in sys.argv:
            self.logger.warning("Aborting execution: Tests are running")
            return

        self.send_census_report()
        self.clear_expired_sessions()
        self.prune_changelog()
        self.delete_expired_jobs()
        self.check_for_new_releases()

    def send_census_report(self):
        """
        Send a census report (if enabled).
        """
        self.logger.info("Reporting census data...")
        if settings.ISOLATED_DEPLOYMENT:
            self.logger.info("ISOLATED_DEPLOYMENT is enabled; skipping")
            return
        if not settings.CENSUS_REPORTING_ENABLED:
            self.logger.info("CENSUS_REPORTING_ENABLED is disabled; skipping")
            return

        census_data = {
            'version': settings.RELEASE.full_version,
            'python_version': sys.version.split()[0],
            'deployment_id': settings.DEPLOYMENT_ID,
        }
        try:
            requests.get(
                url=settings.CENSUS_URL,
                params=census_data,
                timeout=3,
                proxies=resolve_proxies(url=settings.CENSUS_URL)
            )
        except requests.exceptions.RequestException:
            pass

    def clear_expired_sessions(self):
        """
        Clear any expired sessions from the database.
        """
        self.logger.info("Clearing expired sessions...")
        engine = import_module(settings.SESSION_ENGINE)
        try:
            engine.SessionStore.clear_expired()
            self.logger.info("Sessions cleared.")
        except NotImplementedError:
            self.logger.warning(
                f"The configured session engine ({settings.SESSION_ENGINE}) does not support "
                f"clearing sessions; skipping."
            )

    def prune_changelog(self):
        """
        Delete any ObjectChange records older than the configured changelog retention time (if any).
        """
        self.logger.info("Pruning old changelog entries...")
        config = Config()
        if not config.CHANGELOG_RETENTION:
            self.logger.info("No retention period specified; skipping.")
            return

        cutoff = timezone.now() - timedelta(days=config.CHANGELOG_RETENTION)
        self.logger.debug(
            f"Changelog retention period: {config.CHANGELOG_RETENTION} days ({cutoff:%Y-%m-%d %H:%M:%S})"
        )

        count = ObjectChange.objects.filter(time__lt=cutoff).delete()[0]
        self.logger.info(f"Deleted {count} expired changelog records")

    def delete_expired_jobs(self):
        """
        Delete any jobs older than the configured retention period (if any).
        """
        self.logger.info("Deleting expired jobs...")
        config = Config()
        if not config.JOB_RETENTION:
            self.logger.info("No retention period specified; skipping.")
            return

        cutoff = timezone.now() - timedelta(days=config.JOB_RETENTION)
        self.logger.debug(
            f"Job retention period: {config.JOB_RETENTION} days ({cutoff:%Y-%m-%d %H:%M:%S})"
        )

        count = Job.objects.filter(created__lt=cutoff).delete()[0]
        self.logger.info(f"Deleted {count} expired jobs")

    def check_for_new_releases(self):
        """
        Check for new releases and cache the latest release.
        """
        self.logger.info("Checking for new releases...")
        if settings.ISOLATED_DEPLOYMENT:
            self.logger.info("ISOLATED_DEPLOYMENT is enabled; skipping")
            return
        if not settings.RELEASE_CHECK_URL:
            self.logger.info("RELEASE_CHECK_URL is not set; skipping")
            return

        # Fetch the latest releases
        self.logger.debug(f"Release check URL: {settings.RELEASE_CHECK_URL}")
        try:
            response = requests.get(
                url=settings.RELEASE_CHECK_URL,
                headers={'Accept': 'application/vnd.github.v3+json'},
                proxies=resolve_proxies(url=settings.RELEASE_CHECK_URL)
            )
            response.raise_for_status()
        except requests.exceptions.RequestException as exc:
            self.logger.error(f"Error fetching release: {exc}")
            return

        # Determine the most recent stable release
        releases = []
        for release in response.json():
            if 'tag_name' not in release or release.get('devrelease') or release.get('prerelease'):
                continue
            releases.append((version.parse(release['tag_name']), release.get('html_url')))
        latest_release = max(releases)
        self.logger.debug(f"Found {len(response.json())} releases; {len(releases)} usable")
        self.logger.info(f"Latest release: {latest_release[0]}")

        # Cache the most recent release
        cache.set('latest_release', latest_release, None)
