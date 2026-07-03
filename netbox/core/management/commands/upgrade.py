from django.core.management.base import BaseCommand

from utilities.upgrade_tasks import add_upgrade_arguments, run_upgrade_tasks


class Command(BaseCommand):
    help = "Run the NetBox application tasks required after installing or upgrading NetBox."

    def add_arguments(self, parser):
        add_upgrade_arguments(parser)

    def handle(self, *args, **options):
        run_upgrade_tasks(
            self,
            no_input=options['no_input'],
            readonly=options['readonly'],
            skip_migrations=options['skip_migrations'],
            skip_static=options['skip_static'],
            skip_reindex=options['skip_reindex'],
            build_docs=options['build_docs'],
        )
