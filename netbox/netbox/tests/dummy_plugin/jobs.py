from core.choices import JobIntervalChoices
from netbox.jobs import JobRunner, system_job


@system_job(interval=JobIntervalChoices.INTERVAL_HOURLY)
class DummySystemJob(JobRunner):

    def run(self, *args, **kwargs):
        pass
