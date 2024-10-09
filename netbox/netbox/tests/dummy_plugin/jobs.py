from core.choices import JobIntervalChoices
from netbox.jobs import JobRunner


class DummySystemJob(JobRunner):
    class Meta:
        system_interval = JobIntervalChoices.INTERVAL_HOURLY

    def run(self, *args, **kwargs):
        pass


system_jobs = (
    DummySystemJob,
)
