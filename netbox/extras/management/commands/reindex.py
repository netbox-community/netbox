from django.contrib.contenttypes.models import ContentType
from django.core.management.base import BaseCommand, CommandError
from django.utils.translation import gettext as _

from netbox.registry import registry
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
        parser.add_argument(
            '--lazy',
            action='store_true',
            help="For each model, reindex objects only if no cache entries already exist"
        )

    def _get_indexers(self, *model_names):
        indexers = {}

        # No models specified; pull in all registered indexers
        if not model_names:
            for idx in registry['search'].values():
                indexers[idx.model] = idx

        # Return only indexers for the specified models
        else:
            for label in model_names:
                labels = label.lower().split('.')

                # Label specifies an exact model
                if len(labels) == 2:
                    app_label, model_name = labels
                    try:
                        idx = registry['search'][f'{app_label}.{model_name}']
                        indexers[idx.model] = idx
                    except KeyError:
                        raise CommandError(f"No indexer registered for {label}")

                # Label specifies all the models of an app
                elif len(labels) == 1:
                    app_label = labels[0] + '.'
                    for indexer_label, idx in registry['search'].items():
                        if indexer_label.startswith(app_label):
                            indexers[idx.model] = idx

                else:
                    raise CommandError(
                        f"Invalid model: {label}. Model names must be in the format <app_label> or <app_label>.<model_name>."
                    )

        return indexers

    def handle(self, *model_labels, **kwargs):

        # Determine which models to reindex
        indexers = self._get_indexers(*model_labels)
        if not indexers:
            raise CommandError(_("No indexers found!"))
        self.stdout.write(f'Reindexing {len(indexers)} models.')

        # Clear cached values for the specified models (if not being lazy)
        if not kwargs['lazy']:
            if model_labels:
                content_types = [ContentType.objects.get_for_model(model) for model in indexers.keys()]
            else:
                content_types = None

            self.stdout.write('Clearing cached values... ', ending='')
            self.stdout.flush()
            deleted_count = search_backend.clear(object_types=content_types)
            self.stdout.write(f'{deleted_count} entries deleted.')

        # Index models
        self.stdout.write('Indexing models')
        for model, idx in indexers.items():
            app_label = model._meta.app_label
            model_name = model._meta.model_name
            self.stdout.write(f'  {app_label}.{model_name}... ', ending='')
            self.stdout.flush()

            if kwargs['lazy']:
                content_type = ContentType.objects.get_for_model(model)
                if cached_count := search_backend.count(object_types=[content_type]):
                    self.stdout.write(f'Skipping (found {cached_count} existing).')
                    continue

            i = search_backend.cache(model.objects.iterator(), remove_existing=False)
            if i:
                self.stdout.write(f'{i} entries cached.')
            else:
                self.stdout.write(f'No objects found.')

        msg = f'Completed.'
        if total_count := search_backend.size:
            msg += f' Total entries: {total_count}'
        self.stdout.write(msg, self.style.SUCCESS)
