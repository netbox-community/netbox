from __future__ import unicode_literals

from django.core.management.base import BaseCommand
from django.utils import timezone

from extras.reports import get_reports


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

                    # Run the report and create a new ReportResult
                    self.stdout.write(
                        "[{:%H:%M:%S}] Running {}...".format(timezone.now(), report.full_name)
                    )
                    report.run()

                    # Report on success/failure
                    status = self.style.ERROR('FAILED') if report.failed else self.style.SUCCESS('SUCCESS')
                    for test_name, attrs in report.result.data.items():
                        self.stdout.write(
                            "\t{}: {} success, {} info, {} warning, {} failure".format(
                                test_name, attrs['success'], attrs['info'], attrs['warning'], attrs['failure']
                            )
                        )
                    self.stdout.write(
                        "[{:%H:%M:%S}] {}: {}".format(timezone.now(), report.full_name, status)
                    )

        # Wrap things up
        self.stdout.write(
            "[{:%H:%M:%S}] Finished".format(timezone.now())
        )
