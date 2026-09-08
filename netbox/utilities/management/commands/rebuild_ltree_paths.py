from django.apps import apps
from django.core.management.base import BaseCommand, CommandError
from django.db import connection, transaction

from netbox.models.ltree import LtreeModel
from netbox.plugins import PluginConfig
from utilities.mptt_to_ltree import (
    count_stale_rows_sql,
    populate_paths_sql,
    unreachable_rows_sql,
)


class Command(BaseCommand):
    help = (
        "Recompute the trigger-maintained path (and sort_path) columns of hierarchical models "
        "from their parent relationships"
    )

    # How many offending ids a refusal names. Enough to start from, short enough to read.
    REPORTED_IDS = 10

    def add_arguments(self, parser):
        parser.add_argument(
            'model', nargs='*',
            help="Limit the rebuild to these models, as app_label.ModelName (default: all)",
        )
        parser.add_argument(
            '--check', action='store_true',
            help="Report which models need rebuilding, without modifying anything",
        )

    def get_models(self, names):
        """
        Return the concrete core hierarchical models to operate on: those named, in the
        order given, or every one of them ordered by table name.

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

    def check_reachable(self, cursor, model):
        """
        Raise unless every row is reachable from a root by following `parent_id`.

        The rebuild walks down from `parent_id IS NULL`, so a row no root can reach is one
        it silently leaves alone. Reporting success in that case would be the same failure
        this command exists to repair: an operation which appears to have worked while the
        data is still wrong. Refuse instead, and leave correcting the parent relationships
        to the operator, since only they can say what the intended hierarchy was.

        Takes the caller's cursor to keep it visible that this must run in the same
        transaction as the rebuild it guards. Checking in a separate transaction would
        leave a window in which a concurrent write could strand a row between the two.
        """
        cursor.execute(unreachable_rows_sql(model._meta.db_table, self.REPORTED_IDS))
        unreachable, ids = cursor.fetchone()

        if unreachable:
            listed = ', '.join(str(pk) for pk in ids)
            if unreachable > len(ids):
                listed += ', ...'
            raise CommandError(
                f'{model._meta.label_lower}: {unreachable} row(s) cannot be reached from a '
                f'root by following parent_id, so a rebuild would skip them: {listed}. '
                f'Correct the parent relationships, then re-run.'
            )

    def report_stale(self, model):
        """
        Report whether a model's stored paths disagree with its parent relationships.

        Read-only, and takes no locks, so it can be run outside a maintenance window or
        against a replica. It answers which models need rebuilding, not how many rows are
        damaged: see `count_stale_rows_sql()` for why the counts understate a deep tree.
        """
        with connection.cursor() as cursor:
            cursor.execute(
                count_stale_rows_sql(model._meta.db_table, sort_path=model._has_sort_path())
            )
            stale_paths, stale_sort_paths = cursor.fetchone()

        if not (stale_paths or stale_sort_paths):
            self.stdout.write(f'{model._meta.label_lower}: OK')
            return False

        damage = []
        if stale_paths:
            damage.append(f'{stale_paths} path')
        if stale_sort_paths:
            damage.append(f'{stale_sort_paths} sort_path')
        self.stdout.write(self.style.WARNING(
            f"{model._meta.label_lower}: {', '.join(damage)} row(s) disagree with their parent"
        ))
        return True

    def handle(self, *args, **options):
        models = self.get_models(options['model'])

        if options['check']:
            stale = [model for model in models if self.report_stale(model)]
            if stale:
                names = ' '.join(model._meta.label_lower for model in stale)
                self.stdout.write(f'\nNeeds rebuilding: {names}')
            else:
                self.stdout.write(self.style.SUCCESS('Nothing to rebuild.'))
            return

        # Each table is checked and rebuilt in its own transaction. Tables already done
        # stay done if a later one fails or is refused: rebuilding one table cannot leave
        # another inconsistent, and holding every table's row locks until the last one
        # finished would turn several short blocking windows into one long one.
        for model in models:
            with transaction.atomic(), connection.cursor() as cursor:
                # Announce the rebuild only once the check has passed, so a refusal does
                # not print "rebuilding..." for a table left untouched.
                self.check_reachable(cursor, model)
                self.stdout.write(f'{model._meta.label_lower}: rebuilding... ', ending='')
                self.stdout.flush()
                # populate_paths_sql() is the same SQL which backfilled these columns
                # during the ltree migrations. It relies on SET LOCAL, so it must run
                # inside a transaction, and the UPDATE it emits locks every row in the
                # table until it commits.
                cursor.execute(
                    populate_paths_sql(model._meta.db_table, sort_path=model._has_sort_path())
                )
            self.stdout.write(self.style.SUCCESS('done'))

        self.stdout.write(self.style.SUCCESS('Finished.'))
