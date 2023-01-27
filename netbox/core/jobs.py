import logging

from django_rq import job

from extras.choices import JobResultStatusChoices
from .choices import *
from .models import DataSource

logger = logging.getLogger(__name__)


@job('low')
def sync_datasource(job_result, *args, **kwargs):
    """
    Call sync() on a DataSource.
    """
    datasource = DataSource.objects.get(name=job_result.name)

    try:
        job_result.start()
        datasource.sync()
    except Exception:
        job_result.set_status(JobResultStatusChoices.STATUS_ERRORED)
        job_result.save()
        datasource.status = DataSourceStatusChoices.FAILED
        datasource.save()
        logging.error(f"Error during syncing of data source {datasource}")
