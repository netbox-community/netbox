from django.apps import apps
from django.core.management.base import BaseCommand, CommandError
from django.db import connection, transaction

from netbox.models.ltree import LtreeModel
from netbox.plugins import PluginConfig
from utilities.mptt_to_ltree import populate_paths_sql


class Command(BaseCommand):
    help = (
        "Recompute the trigger-maintained path (and sort_path) columns of hierarchical models "
        "from their parent relationships"
    )

    def add_arguments(self, parser):
        parser.add_argument(
            'model', nargs='*',
            help="Limit the rebuild to these models, as app_label.ModelName (default: all)",
        )

    def get_models(self, names):
        """
        Return the concrete core hierarchical models to operate on, ordered by table name.

        Plugin models are excluded, including when named explicitly: the SQL which rebuilds
        `sort_path` reads the name column by name, while `InstallLtreeTriggers` lets a plugin
        maintain it from any column, so rebuilding one is not something this command can do
        correctly. A plugin in that position needs its own repair path.
        """
        def concrete_subclasses(base):
            for subclass in base.__subclasses__():
                if subclass._meta.abstract:
                    yield from concrete_subclasses(subclass)
                elif not isinstance(apps.get_app_config(subclass._meta.app_label), PluginConfig):
                    yield subclass

        candidates = {
            model._meta.label_lower: model for model in concrete_subclasses(LtreeModel)
        }

        if not names:
            return sorted(candidates.values(), key=lambda model: model._meta.db_table)

        models = []
        for name in names:
            model = candidates.get(name.lower())
            if model is None:
                raise CommandError(f"{name} is not a core hierarchical (ltree-backed) model")
            models.append(model)
        return models

    def handle(self, *args, **options):
        for model in self.get_models(options['model']):
            # populate_paths_sql() is the same SQL which backfilled these columns during the
            # ltree migrations. It relies on SET LOCAL, so it must run inside a transaction,
            # and the UPDATE it emits locks every row in the table until it commits.
            self.stdout.write(f'{model._meta.label_lower}: rebuilding... ', ending='')
            self.stdout.flush()
            with transaction.atomic(), connection.cursor() as cursor:
                cursor.execute(
                    populate_paths_sql(model._meta.db_table, sort_path=model._has_sort_path())
                )
            self.stdout.write(self.style.SUCCESS('done'))

        self.stdout.write(self.style.SUCCESS('Finished.'))
