import logging

from extras.choices import JobResultStatusChoices
from netbox.search.backends import search_backend
from .choices import *
from .exceptions import SyncError
from .models import DataSource

logger = logging.getLogger(__name__)


def sync_datasource(job_result, *args, **kwargs):
    """
    Call sync() on a DataSource.
    """
    datasource = DataSource.objects.get(name=job_result.name)

    try:
        job_result.start()
        datasource.sync()

        # Update the search cache for DataFiles belonging to this source
        search_backend.cache(datasource.datafiles.iterator())

        job_result.terminate()

    except SyncError as e:
        job_result.terminate(status=JobResultStatusChoices.STATUS_ERRORED)
        DataSource.objects.filter(pk=datasource.pk).update(status=DataSourceStatusChoices.FAILED)
        logging.error(e)
