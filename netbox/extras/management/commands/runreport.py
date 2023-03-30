import time

from django.core.management.base import BaseCommand
from django.utils import timezone

from core.choices import JobStatusChoices
from core.models import Job
from extras.models import ReportModule
from extras.reports import run_report


class Command(BaseCommand):
    help = "Run a report to validate data in NetBox"

    def add_arguments(self, parser):
        parser.add_argument('reports', nargs='+', help="Report(s) to run")

    def handle(self, *args, **options):

        for module in ReportModule.objects.all():
            for report in module.reports.values():
                if module.name in options['reports'] or report.full_name in options['reports']:

                    # Run the report and create a new Job
                    self.stdout.write(
                        "[{:%H:%M:%S}] Running {}...".format(timezone.now(), report.full_name)
                    )

                    job = Job.enqueue(
                        run_report,
                        instance=module,
                        name=report.class_name,
                        job_timeout=report.job_timeout
                    )

                    # Wait on the job to finish
                    while job.status not in JobStatusChoices.TERMINAL_STATE_CHOICES:
                        time.sleep(1)
                        job = Job.objects.get(pk=job.pk)

                    # Report on success/failure
                    if job.status == JobStatusChoices.STATUS_FAILED:
                        status = self.style.ERROR('FAILED')
                    elif job == JobStatusChoices.STATUS_ERRORED:
                        status = self.style.ERROR('ERRORED')
                    else:
                        status = self.style.SUCCESS('SUCCESS')

                    for test_name, attrs in job.data.items():
                        self.stdout.write(
                            "\t{}: {} success, {} info, {} warning, {} failure".format(
                                test_name, attrs['success'], attrs['info'], attrs['warning'], attrs['failure']
                            )
                        )
                    self.stdout.write(
                        "[{:%H:%M:%S}] {}: {}".format(timezone.now(), report.full_name, status)
                    )
                    self.stdout.write(
                        "[{:%H:%M:%S}] {}: Duration {}".format(timezone.now(), report.full_name, job.duration)
                    )

        # Wrap things up
        self.stdout.write(
            "[{:%H:%M:%S}] Finished".format(timezone.now())
        )
