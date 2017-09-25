from __future__ import unicode_literals

from django.core.management.base import BaseCommand
from django.utils import timezone

from extras.models import ReportResult
from extras.reports import get_reports


class Command(BaseCommand):
    help = "Run a report to validate data in NetBox"

    def add_arguments(self, parser):
        parser.add_argument('reports', nargs='+', help="Report(s) to run")
        # parser.add_argument('--verbose', action='store_true', default=False, help="Print all logs")

    def handle(self, *args, **options):

        # Gather all reports to be run
        reports = get_reports()

        # Run reports
        for module_name, report in reports:
            for report_name, report_cls in report:
                report_name_full = '{}.{}'.format(module_name, report_name)
                if module_name in options['reports'] or report_name_full in options['reports']:

                    # Run the report
                    self.stdout.write(
                        "[{:%H:%M:%S}] Running {}.{}...".format(timezone.now(), module_name, report_name)
                    )
                    report = report_cls()
                    result = report.run()

                    # Record the results
                    ReportResult.objects.filter(report=report_name_full).delete()
                    ReportResult(report=report_name_full, failed=report.failed, data=result).save()

                    # Report on success/failure
                    status = self.style.ERROR('FAILED') if report.failed else self.style.SUCCESS('SUCCESS')
                    for test_name, attrs in result.items():
                        self.stdout.write(
                            "\t{}: {} success, {} info, {} warning, {} failed".format(
                                test_name, attrs['success'], attrs['info'], attrs['warning'], attrs['failed']
                            )
                        )
                    self.stdout.write(
                        "[{:%H:%M:%S}] {}.{}: {}".format(timezone.now(), module_name, report_name, status)
                    )

        # Wrap things up
        self.stdout.write(
            "[{:%H:%M:%S}] Finished".format(timezone.now())
        )
