import logging
import requests
import sys

from django.conf import settings
from netbox.jobs import JobRunner, system_job
from netbox.search.backends import search_backend
from .choices import DataSourceStatusChoices, JobIntervalChoices
from .exceptions import SyncError
from .models import DataSource

logger = logging.getLogger(__name__)


class SyncDataSourceJob(JobRunner):
    """
    Call sync() on a DataSource.
    """

    class Meta:
        name = 'Synchronization'

    def run(self, *args, **kwargs):
        datasource = DataSource.objects.get(pk=self.job.object_id)

        try:
            datasource.sync()

            # Update the search cache for DataFiles belonging to this source
            search_backend.cache(datasource.datafiles.iterator())

        except Exception as e:
            DataSource.objects.filter(pk=datasource.pk).update(status=DataSourceStatusChoices.FAILED)
            if type(e) is SyncError:
                logging.error(e)
            raise e


@system_job(interval=JobIntervalChoices.INTERVAL_DAILY)
class SystemHousekeepingJob(JobRunner):
    """
    Perform daily system housekeeping functions.
    """
    class Meta:
        name = "System Housekeeping"

    def run(self, *args, **kwargs):
        # Skip if running in development or test mode
        if settings.DEBUG or 'test' in sys.argv:
            return

        # TODO: Migrate other housekeeping functions from the `housekeeping` management command.
        self.send_census_report()

    @staticmethod
    def send_census_report():
        """
        Send a census report (if enabled).
        """
        # Skip if census reporting is disabled
        if settings.ISOLATED_DEPLOYMENT or not settings.CENSUS_REPORTING_ENABLED:
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
                proxies=settings.HTTP_PROXIES
            )
        except requests.exceptions.RequestException:
            pass
