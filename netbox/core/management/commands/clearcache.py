from django.core.cache import cache
from django.core.management.base import BaseCommand

from extras.models import ConfigRevision


class Command(BaseCommand):
    """Command to clear the entire cache."""
    help = 'Clears the cache.'

    def handle(self, *args, **kwargs):
        # Fetch the current config revision from the cache
        config_version = cache.get('config_version')
        # Clear the cache
        cache.clear()
        self.stdout.write('Cache has been cleared.', ending="\n")
        if config_version:
            # Activate the current config revision
            ConfigRevision.objects.get(id=config_version).activate()
            self.stdout.write(f'Config revision ({config_version}) has been restored.', ending="\n")
