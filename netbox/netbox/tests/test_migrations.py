import re
from collections import defaultdict

from django.apps import apps
from django.conf import settings
from django.db.migrations.loader import MigrationLoader
from django.test import SimpleTestCase

# Migrations which share a numeric prefix with a sibling migration but predate
# enforcement of this convention. New duplicates must not be added; these are
# grandfathered in to avoid rewriting historical migration history.
#
# Keyed by app label, valued by the set of duplicated numeric prefixes.
EXEMPTIONS = {
    'dcim': {'0203', '0226'},
}

MIGRATION_PREFIX_RE = re.compile(r'^(\d+)_')


def first_party_app_labels():
    """
    Return the labels of NetBox's own apps (those living within the project
    source tree), excluding third-party and plugin apps.
    """
    labels = []
    for app_config in apps.get_app_configs():
        if app_config.path and app_config.path.startswith(settings.BASE_DIR):
            labels.append(app_config.label)
    return labels


class DuplicateMigrationIndexTestCase(SimpleTestCase):
    """
    Ensure that no two migrations within the same app share a numeric prefix
    (e.g. ``0123_foo.py`` and ``0123_bar.py``). While technically permissible,
    duplicate indexes invite confusion and have never been NetBox's (or
    Django's) convention. See netbox-community/netbox#21945.
    """

    def find_duplicate_prefixes(self, app_labels):
        """
        Map each given app label to the numeric prefixes shared by more than
        one of its migrations: ``{app_label: {prefix: [migration_name, ...]}}``.
        """
        per_app = {label: defaultdict(list) for label in app_labels}
        loader = MigrationLoader(connection=None, ignore_no_migrations=True)

        for (migration_app, migration_name) in loader.disk_migrations:
            if migration_app not in per_app:
                continue
            match = MIGRATION_PREFIX_RE.match(migration_name)
            if match:
                per_app[migration_app][match.group(1)].append(migration_name)

        return {
            label: {prefix: sorted(names) for prefix, names in prefixes.items() if len(names) > 1}
            for label, prefixes in per_app.items()
        }

    def test_no_duplicate_migration_indexes(self):
        errors = []
        app_labels = first_party_app_labels()
        duplicates_by_app = self.find_duplicate_prefixes(app_labels)

        for app_label in app_labels:
            duplicates = duplicates_by_app[app_label]
            exempted = EXEMPTIONS.get(app_label, set())

            # Flag any newly introduced duplicate prefixes.
            for prefix, names in sorted(duplicates.items()):
                if prefix in exempted:
                    continue
                joined = ', '.join(f'{name}.py' for name in names)
                errors.append(f'  {app_label}: prefix {prefix} is shared by {joined}')

            # Flag stale exemptions whose duplicates have since been resolved,
            # so the exemption list cannot rot.
            for prefix in sorted(exempted - set(duplicates)):
                errors.append(
                    f'  {app_label}: stale exemption for prefix {prefix} (no longer duplicated); '
                    f'remove it from EXEMPTIONS'
                )

        self.assertFalse(
            errors,
            'Duplicate migration indexes detected. Renumber new migrations so each has a unique '
            'numeric prefix within its app:\n' + '\n'.join(errors),
        )
