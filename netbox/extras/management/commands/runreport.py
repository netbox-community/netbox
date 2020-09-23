import time

from django.contrib.contenttypes.models import ContentType
from django.core.management.base import BaseCommand
from django.utils import timezone

from extras.choices import JobResultStatusChoices
from extras.models import JobResult
from extras.reports import get_reports, run_report


class Command(BaseCommand):
    help = "Run a report to validate data in NetBox"

    def add_arguments(self, parser):
        parser.add_argument('reports', nargs='+', help="Report(s) to run")

    def handle(self, *args, **options):

        # Gather all available reports
        reports = get_reports()

        # Run reports
        for module_name, report_list in reports:
            for report in report_list:
                if module_name in options['reports'] or report.full_name in options['reports']:

                    # Run the report and create a new JobResult
                    self.stdout.write(
                        "[{:%H:%M:%S}] Running {}...".format(timezone.now(), report.full_name)
                    )

                    report_content_type = ContentType.objects.get(app_label='extras', model='report')
                    job_result = JobResult.enqueue_job(
                        run_report,
                        report.full_name,
                        report_content_type,
                        None
                    )

                    # Wait on the job to finish
                    while job_result.status not in JobResultStatusChoices.TERMINAL_STATE_CHOICES:
                        time.sleep(1)
                        job_result = JobResult.objects.get(pk=job_result.pk)

                    # Report on success/failure
                    if job_result.status == JobResultStatusChoices.STATUS_FAILED:
                        status = self.style.ERROR('FAILED')
                    elif job_result == JobResultStatusChoices.STATUS_ERRORED:
                        status = self.style.ERROR('ERRORED')
                    else:
                        status = self.style.SUCCESS('SUCCESS')

                    for test_name, attrs in job_result.data.items():
                        self.stdout.write(
                            "\t{}: {} success, {} info, {} warning, {} failure".format(
                                test_name, attrs['success'], attrs['info'], attrs['warning'], attrs['failure']
                            )
                        )
                    self.stdout.write(
                        "[{:%H:%M:%S}] {}: {}".format(timezone.now(), report.full_name, status)
                    )
                    self.stdout.write(
                        "[{:%H:%M:%S}] {}: Duration {}".format(timezone.now(), report.full_name, job_result.duration)
                    )

        # Wrap things up
        self.stdout.write(
            "[{:%H:%M:%S}] Finished".format(timezone.now())
        )
