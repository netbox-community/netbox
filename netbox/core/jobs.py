import logging

from netbox.search.backends import search_backend
from utilities.jobs import JobRunner
from .choices import DataSourceStatusChoices
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
