from django.core.cache import cache
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    """Command to clear the entire cache."""
    help = 'Clears the cache.'

    def handle(self, *args, **kwargs):
        cache.clear()
        self.stdout.write('Cache has been cleared.', ending="\n")
