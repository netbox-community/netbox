from django.core.management.base import BaseCommand

from extras.models import CachedValue
from extras.registry import registry
from netbox.search.backends import search_backend


class Command(BaseCommand):
    """Reindex cached search values"""
    help = 'Reindex cached search values.'

    def handle(self, *args, **kwargs):

        self.stdout.write('Clearing cached values...', ending="\n")
        CachedValue.objects.all().delete()

        for app_label, models in registry['search'].items():
            for name, idx in models.items():
                self.stdout.write(f'Reindexing {app_label}.{name}...', ending="\n")
                model = idx.model
                for instance in model.objects.all():
                    search_backend.caching_handler(model, instance)

        cache_size = CachedValue.objects.count()
        self.stdout.write(f'Done. Generated {cache_size} cached values', ending="\n")
