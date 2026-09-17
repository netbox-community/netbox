from itertools import groupby, islice

from django.core.management.base import BaseCommand, CommandError
from django.core.management.color import no_style
from django.db import connection
from django.db.models import F, Q

from dcim.exceptions import UnsupportedCablePath
from dcim.models import CablePath, ConsolePort, ConsoleServerPort, Interface, PowerFeed, PowerOutlet, PowerPort
from dcim.utils import create_cablepaths, get_cable_end_terminations

ORIGIN_GROUP_BATCH_SIZE = 100

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
        self.stdout.write(f"\r  [{'#' * bar_size}{' ' * (20 - bar_size)}] {int(percentage)}%", ending='')

    @staticmethod
    def group_key(obj):
        """
        Key an annotated endpoint by its cable end, falling back to its own PK when it has no termination row.
        """
        if obj._trace_cable_id is not None:
            return (obj._trace_cable_id, obj._trace_cable_end)

        # Wireless endpoints and missing CableTermination rows retain the singleton fallback.
        return obj.pk

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
            self.stdout.write(self.style.SUCCESS(f'  Deleted {deleted_count} paths'))

            # Reinitialize the model's PK sequence
            self.stdout.write('Resetting database sequence for CablePath model')
            sequence_sql = connection.ops.sequence_reset_sql(no_style(), [CablePath])
            with connection.cursor() as cursor:
                for sql in sequence_sql:
                    cursor.execute(sql)

        # Retrace paths. A failed group must roll back, but must not prevent repairing independent groups.
        failures = 0
        for model in ENDPOINT_MODELS:
            params = Q(cable__isnull=False)
            if hasattr(model, 'wireless_link'):
                params |= Q(wireless_link__isnull=False)
            origins = model.objects.filter(params)
            if not options['force']:
                origins = origins.filter(_path__isnull=True)
            origins_count = origins.count()
            if not origins_count:
                self.stdout.write(f'Found no missing {model._meta.verbose_name} paths; skipping')
                continue
            self.stdout.write(f'Retracing {origins_count} cabled {model._meta.verbose_name_plural}...')
            # The unique termination relation gives each selected endpoint at most one authoritative end.
            # Adjacent cable ends can be processed together without keeping a set of all previously seen ends.
            origins = origins.annotate(
                _trace_cable_id=F('cable_terminations__cable_id'),
                _trace_cable_end=F('cable_terminations__cable_end'),
            ).order_by('_trace_cable_id', '_trace_cable_end', 'pk')

            grouped_origins = groupby(origins.iterator(chunk_size=1000), key=self.group_key)
            retraced = i = model_failures = 0
            while True:
                batch = []
                # Consume each group before advancing groupby: its iterators share the underlying stream.
                # Keep only a representative and count, not all selected endpoints on each end.
                for key, selected in islice(grouped_origins, ORIGIN_GROUP_BATCH_SIZE):
                    first = next(selected)
                    selected_count = 1 + sum(1 for _ in selected)
                    batch.append((key, first, selected_count))
                if not batch:
                    break

                cable_keys = [key for key, _, _ in batch if isinstance(key, tuple)]
                cable_ends = get_cable_end_terminations(cable_keys)
                for key, first, selected_count in batch:
                    group = cable_ends[key] if isinstance(key, tuple) else [first]
                    try:
                        if not group:
                            raise UnsupportedCablePath(
                                'No current terminations remain for the selected cable end; '
                                'its membership may have changed during tracing.'
                            )
                        create_cablepaths(group)
                    except UnsupportedCablePath as error:
                        # The helper's savepoint has unwound; other groups can still be repaired.
                        model_failures += 1
                        if isinstance(key, tuple):
                            target = f'cable #{key[0]} end {key[1]}'
                        else:
                            target = f'{first._meta.label} #{first.pk}'
                        self.stderr.write(self.style.ERROR(f'Unable to trace {target}: {error}'))
                    else:
                        retraced += selected_count

                    # Advance progress for every selected endpoint, even in a failed or shared group.
                    for completed in range((i // 100 + 1) * 100, i + selected_count + 1, 100):
                        self.draw_progress_bar(completed * 100 / origins_count)
                    i += selected_count
            self.draw_progress_bar(100)
            self.stdout.write(self.style.SUCCESS(f'\n  Retraced {retraced} {model._meta.verbose_name_plural}'))
            if model_failures:
                failed = origins_count - retraced
                self.stdout.write(self.style.WARNING(
                    f'  Failed to retrace {failed} selected {model._meta.verbose_name_plural} '
                    f'in {model_failures} origin group(s)'
                ))
                failures += model_failures

        if failures:
            raise CommandError(
                f'Unable to trace {failures} origin group(s) across all endpoint models. Other groups were processed; '
                'correct the reported topology or data inconsistencies and rerun trace_paths.'
            )
        self.stdout.write(self.style.SUCCESS('Finished.'))
