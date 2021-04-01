from django.core.management.base import BaseCommand
from django.core.management.color import no_style
from django.db import connection

from dcim.models import CablePath, ConsolePort, ConsoleServerPort, Interface, PowerFeed, PowerOutlet, PowerPort
from dcim.signals import create_cablepath

ENDPOINT_MODELS = (
    ConsolePort,
    ConsoleServerPort,
    Interface,
    PowerFeed,
    PowerOutlet,
    PowerPort
)


class Command(BaseCommand):
    help = "Generate any missing cable paths among all cable termination objects in NetBox"

    def add_arguments(self, parser):
        parser.add_argument(
            "--force", action='store_true', dest='force',
            help="Force recalculation of all existing cable paths"
        )
        parser.add_argument(
            "--no-input", action='store_true', dest='no_input',
            help="Do not prompt user for any input/confirmation"
        )

    def draw_progress_bar(self, percentage):
        """
        Draw a simple progress bar 20 increments wide illustrating the specified percentage.
        """
        bar_size = int(percentage / 5)
        self.stdout.write(f"\r  [{'#' * bar_size}{' ' * (20-bar_size)}] {int(percentage)}%", ending='')

    def handle(self, *model_names, **options):

        # If --force was passed, first delete all existing CablePaths
        if options['force']:
            cable_paths = CablePath.objects.all()
            paths_count = cable_paths.count()

            # Prompt the user to confirm recalculation of all paths
            if paths_count and not options['no_input']:
                self.stdout.write(self.style.ERROR("WARNING: Forcing recalculation of all cable paths."))
                self.stdout.write(
                    f"This will delete and recalculate all {paths_count} existing cable paths. Are you sure?"
                )
                confirmation = input("Type yes to confirm: ")
                if confirmation != 'yes':
                    self.stdout.write(self.style.SUCCESS("Aborting"))
                    return

            # Delete all existing CablePath instances
            self.stdout.write(f"Deleting {paths_count} existing cable paths...")
            deleted_count, _ = CablePath.objects.all().delete()
            self.stdout.write((self.style.SUCCESS(f'  Deleted {deleted_count} paths')))

            # Reinitialize the model's PK sequence
            self.stdout.write(f'Resetting database sequence for CablePath model')
            sequence_sql = connection.ops.sequence_reset_sql(no_style(), [CablePath])
            with connection.cursor() as cursor:
                for sql in sequence_sql:
                    cursor.execute(sql)

        # Retrace paths
        for model in ENDPOINT_MODELS:
            origins = model.objects.filter(cable__isnull=False)
            if not options['force']:
                origins = origins.filter(_path__isnull=True)
            origins_count = origins.count()
            if not origins_count:
                self.stdout.write(f'Found no missing {model._meta.verbose_name} paths; skipping')
                continue
            self.stdout.write(f'Retracing {origins_count} cabled {model._meta.verbose_name_plural}...')
            i = 0
            for i, obj in enumerate(origins, start=1):
                create_cablepath(obj)
                if not i % 100:
                    self.draw_progress_bar(i * 100 / origins_count)
            self.draw_progress_bar(100)
            self.stdout.write(self.style.SUCCESS(f'\n  Retraced {i} {model._meta.verbose_name_plural}'))

        self.stdout.write(self.style.SUCCESS('Finished.'))
