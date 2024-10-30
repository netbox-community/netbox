from core.choices import JobIntervalChoices
from netbox.jobs import JobRunner, system_job


@system_job()
class DummySystemJob(JobRunner):
    class Meta:
        system_interval = JobIntervalChoices.INTERVAL_HOURLY

    def run(self, *args, **kwargs):
        pass


system_jobs = (
    DummySystemJob,
)
