from django.contrib.contenttypes.models import ContentType
from django.core.management.base import BaseCommand
from django.core.management.color import no_style
from django.db import connection
from django.db.models import Q

from dcim.models import CablePath
from dcim.signals import create_cablepath

ENDPOINT_MODELS = (
    'circuits.CircuitTermination',
    'dcim.ConsolePort',
    'dcim.ConsoleServerPort',
    'dcim.Interface',
    'dcim.PowerFeed',
    'dcim.PowerOutlet',
    'dcim.PowerPort',
)


class Command(BaseCommand):
    help = "Recalculate natural ordering values for the specified models"

    def add_arguments(self, parser):
        parser.add_argument(
            'args', metavar='app_label.ModelName', nargs='*',
            help='One or more specific models (each prefixed with its app_label) to retrace',
        )

    def _get_content_types(self, model_names):
        q = Q()
        for model_name in model_names:
            app_label, model = model_name.split('.')
            q |= Q(app_label__iexact=app_label, model__iexact=model)
        return ContentType.objects.filter(q)

    def handle(self, *model_names, **options):
        # Determine the models for which we're retracing all paths
        origin_types = self._get_content_types(model_names or ENDPOINT_MODELS)
        self.stdout.write(f"Retracing paths for models: {', '.join([str(ct) for ct in origin_types])}")

        # Delete all existing CablePath instances
        self.stdout.write(f"Deleting existing cable paths...")
        deleted_count, _ = CablePath.objects.filter(origin_type__in=origin_types).delete()
        self.stdout.write((self.style.SUCCESS(f'  Deleted {deleted_count} paths')))

        # Reset the SQL sequence. Can do this only if deleting _all_ CablePaths.
        if not CablePath.objects.count():
            self.stdout.write(f'Resetting database sequence for CablePath...')
            sequence_sql = connection.ops.sequence_reset_sql(no_style(), [CablePath])
            with connection.cursor() as cursor:
                for sql in sequence_sql:
                    cursor.execute(sql)
                self.stdout.write(self.style.SUCCESS('  Success.'))

        # Retrace interfaces
        for ct in origin_types:
            model = ct.model_class()
            origins = model.objects.filter(cable__isnull=False)
            print(f'Retracing {origins.count()} cabled {model._meta.verbose_name_plural}...')
            i = 0
            for i, obj in enumerate(origins, start=1):
                create_cablepath(obj)
                if not i % 1000:
                    self.stdout.write(f'  {i}')
            self.stdout.write(self.style.SUCCESS(f'  Retraced {i} {model._meta.verbose_name_plural}'))

        self.stdout.write(self.style.SUCCESS('Finished.'))
