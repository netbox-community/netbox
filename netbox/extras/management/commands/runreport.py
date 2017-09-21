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

            # Split the report name off if one has been provided.
            report_name = None
            if '.' in module_name:
                module_name, report_name = module_name.split('.', 1)

            # Import the report module
            try:
                report_module = importlib.import_module('reports.report_{}'.format(module_name))
            except ImportError:
                self.stdout.write(
                    "Report module '{}' not found. Ensure that the report has been saved as 'report_{}.py' in the "
                    "reports directory.".format(module_name, module_name)
                )
                return

            # If the name of a particular report has been given, run that. Otherwise, run all reports in the module.
            if report_name is not None:
                report_cls = getattr(report_module, report_name)
                reports = [(report_name, report_cls)]
            else:
                for name, report_cls in inspect.getmembers(report_module, inspect.isclass):
                    if report_cls in Report.__subclasses__():
                        reports.append((name, report_cls))

        # Run reports
        for name, report_cls in reports:
            self.stdout.write("[{:%H:%M:%S}] Running {}...".format(timezone.now(), name))
            report = report_cls()
            results = report.run()
            status = self.style.ERROR('FAILED') if report.failed else self.style.SUCCESS('SUCCESS')
            self.stdout.write("[{:%H:%M:%S}] {}: {}".format(timezone.now(), name, status))
            for test_name, attrs in results.items():
                self.stdout.write("    {}: {} success, {} info, {} warning, {} failed".format(
                    test_name, attrs['success'], attrs['info'], attrs['warning'], attrs['failed']
                ))

        self.stdout.write("[{:%H:%M:%S}] Finished".format(timezone.now()))
