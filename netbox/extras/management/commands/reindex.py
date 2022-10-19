from django.contrib.contenttypes.models import ContentType
from django.core.management.base import BaseCommand, CommandError

from extras.models import CachedValue
from extras.registry import registry
from netbox.search.backends import search_backend


class Command(BaseCommand):
    help = 'Reindex objects for search'

    def add_arguments(self, parser):
        parser.add_argument(
            'args',
            metavar='app_label[.ModelName]',
            nargs='*',
            help='One or more apps or models to reindex',
        )

    def _get_indexers(self, *model_names):
        indexers = {}

        # No models specified; pull in all registered indexers
        if not model_names:
            for app_label, models in registry['search'].items():
                for _, idx in models.items():
                    indexers[idx.model] = idx

        # Return only indexers for the specified models
        else:
            for label in model_names:
                try:
                    app_label, model_name = label.lower().split('.')
                except ValueError:
                    raise CommandError(
                        f"Invalid model: {label}. Model names must be in the format <app_label>.<model_name>."
                    )
                try:
                    idx = registry['search'][app_label][model_name]
                    indexers[idx.model] = idx
                except KeyError:
                    raise CommandError(f"No indexer found for {label}")

        return indexers

    def handle(self, *model_labels, **kwargs):

        # Determine which models to reindex
        indexers = self._get_indexers(*model_labels)
        if not indexers:
            raise CommandError("No indexers found!")
        self.stdout.write(f'Reindexing {len(indexers)} models.')

        # Clear all cached values for the specified models
        self.stdout.write('Clearing cached values... ', ending='')
        if model_labels:
            content_types = [
                ContentType.objects.get_for_model(model) for model in indexers.keys()
            ]
            del_count, _ = CachedValue.objects.filter(object_type__in=content_types).delete()
        else:
            del_count, _ = CachedValue.objects.all().delete()
        self.stdout.write(f'{del_count} deleted.')

        # Index models
        for model, idx in indexers.items():
            app_label = model._meta.app_label
            model_name = model._meta.model_name
            self.stdout.write(f'Reindexing {app_label}.{model_name}... ', ending='')
            i = 0
            for i, instance in enumerate(model.objects.all()):
                search_backend.caching_handler(model, instance)
            if i:
                self.stdout.write(f'{i} created.')

        cache_size = CachedValue.objects.count()
        self.stdout.write(f'Done. Finished with {cache_size} cached values')
