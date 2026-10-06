import hashlib
import importlib.util
import re
import sys
from pathlib import Path

from django.apps import apps
from django.db import DEFAULT_DB_ALIAS, DatabaseError, connections
from django.db.migrations.loader import MigrationLoader
from django.test.runner import DiscoverRunner

__all__ = (
    'NetBoxTestRunner',
    'get_migration_files',
    'get_schema_fingerprint',
    'stamp_test_database',
)

FINGERPRINT_PREFIX = 'netbox-schema:'

# Suffixes of editor backup and patch leftover files to exclude from the fingerprint
IGNORED_SUFFIXES = ('~', '.bak', '.orig', '.rej')


def get_migration_files():
    """
    Return a mapping of names to paths for all files (including data files) within the migrations package of each
    installed app, including plugins. Hidden files (e.g. editor swap files), __pycache__, and backup files are ignored.
    """
    files = {}
    for app_config in apps.get_app_configs():
        module_name, _ = MigrationLoader.migrations_module(app_config.label)
        if module_name and (spec := importlib.util.find_spec(module_name)) and spec.submodule_search_locations:
            for location in spec.submodule_search_locations:
                for path in Path(location).rglob('*'):
                    relative_path = path.relative_to(location)
                    if (
                        path.is_file()
                        and '__pycache__' not in relative_path.parts
                        and not any(part.startswith('.') for part in relative_path.parts)
                        and not path.name.endswith(IGNORED_SUFFIXES)
                    ):
                        files[f'{module_name}/{relative_path.as_posix()}'] = path
    return files


def get_schema_fingerprint():
    """
    Return a hash of the names and contents of all files returned by get_migration_files().

    Migrations may invoke code elsewhere (e.g. custom fields or trigger SQL) which can change without any change to the
    migrations themselves. Such changes are deliberately not tracked: they must be accompanied by a new migration to
    take effect on existing databases, and until then a reused test database reflects what an upgrade would produce.
    """
    files = get_migration_files()
    digest = hashlib.sha256()
    for name in sorted(files):
        digest.update(name.encode() + b'\0' + files[name].read_bytes() + b'\0')
    return digest.hexdigest()


def _write_stamp(connection, db_name, stamp):
    with connection.creation._nodb_cursor() as cursor:
        cursor.execute(f"COMMENT ON DATABASE {connection.ops.quote_name(db_name)} IS '{stamp}'")


def stamp_test_database(alias=DEFAULT_DB_ALIAS):
    """
    Mark an existing test database as matching the current migrations, so that NetBoxTestRunner will reuse it with
    --keepdb. Used by CI after restoring a cached test database.
    """
    connection = connections[alias]
    _write_stamp(connection, connection.creation._get_test_db_name(), FINGERPRINT_PREFIX + get_schema_fingerprint())


class NetBoxTestRunner(DiscoverRunner):
    """
    Extends Django's test runner to make --keepdb safe to use by default. Each kept test database is stamped with a
    fingerprint of all migrations (see get_schema_fingerprint()). If the database's stamp is missing or does not
    match the current fingerprint (e.g. after switching branches or editing a migration), the database and any clones
    used by --parallel are rebuilt from scratch, rather than being migrated forward (or in the case of clones, reused
    as-is).
    """
    def setup_databases(self, **kwargs):
        if not self.keepdb:
            return super().setup_databases(**kwargs)

        stamp = FINGERPRINT_PREFIX + get_schema_fingerprint()
        if (aliases := kwargs.get('aliases')) is None:
            aliases = connections
        aliases = [alias for alias in aliases if not connections[alias].settings_dict['TEST'].get('MIRROR')]
        for alias in aliases:
            self._discard_stale_test_databases(connections[alias], stamp)

        old_config = super().setup_databases(**kwargs)

        for alias in aliases:
            connection = connections[alias]
            _write_stamp(connection, connection.settings_dict['NAME'], stamp)

        return old_config

    def _discard_stale_test_databases(self, connection, stamp):
        creation = connection.creation
        test_db_name = creation._get_test_db_name()
        clone_pattern = re.compile(rf'{re.escape(test_db_name)}_\d+')

        with creation._nodb_cursor() as cursor:
            cursor.execute("SELECT datname, shobj_description(oid, 'pg_database') FROM pg_catalog.pg_database")
            databases = dict(cursor.fetchall())
        if databases.get(test_db_name) == stamp:
            return

        to_drop = [name for name in databases if name == test_db_name or clone_pattern.fullmatch(name)]
        if to_drop and self.verbosity >= 1:
            creation.log(
                f"Test database for alias '{connection.alias}' does not match the current migrations; "
                f"discarding {', '.join(sorted(to_drop))}..."
            )
        for name in to_drop:
            try:
                creation._destroy_test_db(name, self.verbosity)
            except DatabaseError as e:
                creation.log(
                    f"Got an error discarding test database {name}: {e}\n"
                    f"Close any other connections to it and try again."
                )
                sys.exit(2)
