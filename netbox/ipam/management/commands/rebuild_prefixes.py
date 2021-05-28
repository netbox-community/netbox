from django.core.management.base import BaseCommand

from ipam.models import Prefix, VRF
from ipam.utils import rebuild_prefixes


class Command(BaseCommand):
    help = "Rebuild the prefix hierarchy (depth and children counts)"

    def handle(self, *model_names, **options):
        self.stdout.write(f'Rebuilding {Prefix.objects.count()} prefixes...')

        # Reset existing counts
        Prefix.objects.update(_depth=0, _children=0)

        # Rebuild the global table
        global_count = Prefix.objects.filter(vrf__isnull=True).count()
        self.stdout.write(f'Global: {global_count} prefixes...')
        rebuild_prefixes(None)

        # Rebuild each VRF
        for vrf in VRF.objects.all():
            vrf_count = Prefix.objects.filter(vrf=vrf).count()
            self.stdout.write(f'VRF {vrf}: {vrf_count} prefixes...')
            rebuild_prefixes(vrf)

        self.stdout.write(self.style.SUCCESS('Finished.'))
