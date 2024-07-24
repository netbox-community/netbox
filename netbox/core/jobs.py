import logging

from netbox.search.backends import search_backend
from utilities.jobs import BackgroundJob
from .choices import DataSourceStatusChoices
from .exceptions import SyncError
from .models import DataSource

logger = logging.getLogger(__name__)


class SyncDataSourceJob(BackgroundJob):
    """
    Call sync() on a DataSource.
    """

    class Meta:
        name = 'Synchronization'

    @classmethod
    def run(cls, job, *args, **kwargs):
        datasource = DataSource.objects.get(pk=job.object_id)

        try:
            datasource.sync()

            # Update the search cache for DataFiles belonging to this source
            search_backend.cache(datasource.datafiles.iterator())

        except Exception as e:
            DataSource.objects.filter(pk=datasource.pk).update(status=DataSourceStatusChoices.FAILED)
            if type(e) is SyncError:
                logging.error(e)
            raise e
