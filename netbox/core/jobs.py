import logging

from netbox.search.backends import search_backend
from .choices import *
from .exceptions import SyncError
from .models import DataSource
from rq.timeouts import JobTimeoutException

logger = logging.getLogger(__name__)


def sync_datasource(job, *args, **kwargs):
    """
    Call sync() on a DataSource.
    """
    datasource = DataSource.objects.get(pk=job.object_id)

    try:
        job.start()
        datasource.sync()

        # Update the search cache for DataFiles belonging to this source
        search_backend.cache(datasource.datafiles.iterator())

        job.terminate()

    except Exception as e:
        job.terminate(status=JobStatusChoices.STATUS_ERRORED)
        DataSource.objects.filter(pk=datasource.pk).update(status=DataSourceStatusChoices.FAILED)
        if type(e) in (SyncError, JobTimeoutException):
            logging.error(e)
        else:
            raise e
