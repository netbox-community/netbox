from django.core.management.base import BaseCommand, CommandError

from core.choices import DataSourceStatusChoices
from core.models import DataSource


class Command(BaseCommand):
    help = "Synchronize a data source from its remote upstream"

    def add_arguments(self, parser):
        parser.add_argument('name', nargs='*', help="Data source(s) to synchronize")
        parser.add_argument(
            "--all", action='store_true', dest='sync_all',
            help="Synchronize all data sources"
        )

    def handle(self, *args, **options):

        # Find DataSources to sync
        if options['sync_all']:
            datasources = DataSource.objects.all()
        elif options['name']:
            datasources = DataSource.objects.filter(name__in=options['name'])
            # Check for invalid names
            found_names = {ds['name'] for ds in datasources.values('name')}
            if invalid_names := set(options['name']) - found_names:
                raise CommandError(f"Invalid data source names: {', '.join(invalid_names)}")
        else:
            raise CommandError("Must specify at least one data source, or set --all.")

        if len(options['name']) > 1:
            self.stdout.write(f"Syncing {len(datasources)} data sources.")

        for i, datasource in enumerate(datasources, start=1):
            self.stdout.write(f"[{i}] Syncing {datasource}... ", ending='')
            self.stdout.flush()
            try:
                datasource.sync()
                self.stdout.write(datasource.get_status_display())
                self.stdout.flush()
            except Exception as e:
                DataSource.objects.filter(pk=datasource.pk).update(status=DataSourceStatusChoices.FAILED)
                raise e

        if len(options['name']) > 1:
            self.stdout.write("Finished.")
