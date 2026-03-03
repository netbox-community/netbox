from django.core.management.base import BaseCommand
from django.db import connection


class Command(BaseCommand):
    help = 'Rebuild pre-rendered config context data for all devices and/or virtual machines'

    def add_arguments(self, parser):
        parser.add_argument(
            '--devices-only',
            action='store_true',
            help='Only rebuild config context data for devices',
        )
        parser.add_argument(
            '--vms-only',
            action='store_true',
            help='Only rebuild config context data for virtual machines',
        )

    def handle(self, *args, **options):
        devices_only = options['devices_only']
        vms_only = options['vms_only']

        with connection.cursor() as cursor:
            if not vms_only:
                self.stdout.write('Rebuilding config context data for devices...')
                cursor.execute(
                    'UPDATE dcim_device SET config_context_data = compute_config_context_for_device(id)'
                )
                self.stdout.write(self.style.SUCCESS(f'  Updated {cursor.rowcount} devices'))

            if not devices_only:
                self.stdout.write('Rebuilding config context data for virtual machines...')
                cursor.execute(
                    'UPDATE virtualization_virtualmachine '
                    'SET config_context_data = compute_config_context_for_vm(id)'
                )
                self.stdout.write(self.style.SUCCESS(f'  Updated {cursor.rowcount} virtual machines'))

        self.stdout.write(self.style.SUCCESS('Done.'))
