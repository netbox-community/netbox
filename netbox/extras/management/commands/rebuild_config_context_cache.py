from django.apps import apps
from django.core.management.base import BaseCommand

from extras.jobs import RENDER_CONFIG_CONTEXT_CHUNK_SIZE

MODELS = ('dcim.device', 'virtualization.virtualmachine')


class Command(BaseCommand):
    help = "Pre-render and cache config context data for all devices and virtual machines"

    def add_arguments(self, parser):
        parser.add_argument(
            '--force', action='store_true',
            help="Re-render every object, including those whose cache is already populated"
        )

    def handle(self, *args, **options):
        for model_label in MODELS:
            Model = apps.get_model(model_label)
            qs = Model.objects.all()
            if not options['force']:
                qs = qs.filter(_config_context_data__isnull=True)

            # Annotate so each instance renders from the same aggregated subquery the on-demand path
            # uses, avoiding N additional queries per object.
            qs = qs.annotate_config_context_data()

            self.stdout.write(f'Rendering config context for {qs.count()} {model_label} object(s)...')

            rendered = 0
            for obj in qs.iterator(chunk_size=RENDER_CONFIG_CONTEXT_CHUNK_SIZE):
                # Capture the generation we render against and write the result back only if no
                # invalidation has bumped it in the meantime (compare-and-set). This mirrors
                # RenderConfigContextJob and ensures that running this command on a live system
                # cannot clobber a concurrent invalidation with a stale render (which would leave a
                # populated-but-stale cache that the background sweep would then skip).
                generation = obj._config_context_generation
                data = obj.render_config_context()
                rendered += Model.objects.filter(
                    pk=obj.pk,
                    _config_context_generation=generation,
                ).update(_config_context_data=data)

            self.stdout.write(self.style.SUCCESS(f'  Rendered {rendered} {model_label} object(s).'))

        self.stdout.write(self.style.SUCCESS('Finished.'))
