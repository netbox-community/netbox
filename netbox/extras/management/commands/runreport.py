from __future__ import unicode_literals
import importlib
import inspect

from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone

from extras.reports import Report


class Command(BaseCommand):
    help = "Run a report to validate data in NetBox"

    def add_arguments(self, parser):
        parser.add_argument('reports', nargs='+', help="Report(s) to run")
        # parser.add_argument('--verbose', action='store_true', default=False, help="Print all logs")

    def handle(self, *args, **options):

        # Gather all reports to be run
        reports = []
        for module_name in options['reports']:
            try:
                report_module = importlib.import_module('reports.report_{}'.format(module_name))
            except ImportError:
                self.stdout.write(
                    "Report '{}' not found. Ensure that the report has been saved as 'report_{}.py' in the reports "
                    "directory.".format(module_name, module_name)
                )
                return
            for name, cls in inspect.getmembers(report_module, inspect.isclass):
                if cls in Report.__subclasses__():
                    reports.append((name, cls))

        # Run reports
        for name, report in reports:
            self.stdout.write("[{:%H:%M:%S}] Running report {}...".format(timezone.now(), name))
            report = report()
            report.run()
            status = self.style.ERROR('FAILED') if report.failed else self.style.SUCCESS('SUCCESS')
            self.stdout.write("[{:%H:%M:%S}] {}: {}".format(timezone.now(), name, status))
            for test_name, attrs in report.results.items():
                self.stdout.write("    {}: {} success, {} info, {} warning, {} failed".format(
                    test_name, attrs['success'], attrs['info'], attrs['warning'], attrs['failed']
                ))

        self.stdout.write("[{:%H:%M:%S}] Finished".format(timezone.now()))
