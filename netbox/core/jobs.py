import logging

from extras.choices import JobResultStatusChoices
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
    except SyncError as e:
        job_result.set_status(JobResultStatusChoices.STATUS_ERRORED)
        job_result.save()
        DataSource.objects.filter(pk=datasource.pk).update(status=DataSourceStatusChoices.FAILED)
        logging.error(e)
