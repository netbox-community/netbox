from netbox.jobs import JobRunner


class DummySystemJob(JobRunner):
    class Meta:
        system_interval = 60

    def run(self, *args, **kwargs):
        pass


system_jobs = (
    DummySystemJob,
)
