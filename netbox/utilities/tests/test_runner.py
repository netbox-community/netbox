import tempfile
from pathlib import Path
from unittest import mock

from django.db import OperationalError
from django.test import SimpleTestCase
from django.test.runner import DiscoverRunner

from utilities.testing import runner
from utilities.testing.runner import NetBoxTestRunner

STAMP = f'{runner.FINGERPRINT_PREFIX}abc'


class SchemaFingerprintTestCase(SimpleTestCase):

    def test_migration_files(self):
        files = runner.get_migration_files()

        self.assertIn('dcim.migrations/0001_squashed.py', files)
        # Plugin migrations
        self.assertIn('netbox.tests.dummy_plugin.migrations/0001_initial.py', files)
        # Data files loaded by migrations
        self.assertIn('dcim.migrations/initial_data/module_type_profiles/cpu.json', files)
        self.assertFalse([name for name in files if '__pycache__' in name])

    def test_migration_files_ignore_hidden_and_backup_files(self):
        module_name = 'netbox.tests.dummy_plugin.migrations'
        find_spec = runner.importlib.util.find_spec

        with tempfile.TemporaryDirectory() as tmpdir:
            for name in (
                '0001_initial.py',
                'data/profile.json',
                '.0001_initial.py.swp',
                '.hidden/0002_foo.py',
                '0001_initial.py~',
                '0001_initial.py.orig',
                '0001_initial.py.rej',
                '0001_initial.py.bak',
            ):
                path = Path(tmpdir) / name
                path.parent.mkdir(parents=True, exist_ok=True)
                path.touch()

            def mock_find_spec(name, *args, **kwargs):
                if name == module_name:
                    return mock.Mock(submodule_search_locations=[tmpdir])
                return find_spec(name, *args, **kwargs)

            with mock.patch.object(runner.importlib.util, 'find_spec', side_effect=mock_find_spec):
                files = runner.get_migration_files()

        plugin_files = sorted(name for name in files if name.startswith(f'{module_name}/'))
        self.assertEqual(plugin_files, [f'{module_name}/0001_initial.py', f'{module_name}/data/profile.json'])

    def test_fingerprint_reflects_names_and_contents(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / 'file.py'
            path.write_text('foo')

            with mock.patch.object(runner, 'get_migration_files', return_value={'a': path}):
                fingerprint = runner.get_schema_fingerprint()
                self.assertEqual(runner.get_schema_fingerprint(), fingerprint)

                # Changing a file's contents changes the fingerprint
                path.write_text('bar')
                self.assertNotEqual(runner.get_schema_fingerprint(), fingerprint)
                fingerprint = runner.get_schema_fingerprint()

            # Renaming a file changes the fingerprint
            with mock.patch.object(runner, 'get_migration_files', return_value={'b': path}):
                self.assertNotEqual(runner.get_schema_fingerprint(), fingerprint)


def get_mock_connection(name='netbox', mirror=None, databases=None):
    """
    Return a mock database connection whose server reports the given {name: comment} databases.
    """
    connection = mock.MagicMock(alias='default', settings_dict={'NAME': name, 'TEST': {'MIRROR': mirror}})
    connection.ops.quote_name.side_effect = lambda name: f'"{name}"'
    # Like Django, derive the test database name from the connection's current database name
    connection.creation._get_test_db_name.side_effect = lambda: f"test_{connection.settings_dict['NAME']}"
    cursor = connection.creation._nodb_cursor.return_value.__enter__.return_value
    cursor.fetchall.return_value = list((databases or {}).items())
    return connection


class DiscardStaleTestDatabasesTestCase(SimpleTestCase):

    def get_dropped_databases(self, databases):
        connection = get_mock_connection(databases=databases)
        NetBoxTestRunner(keepdb=True, verbosity=0)._discard_stale_test_databases(connection, STAMP)
        return {c.args[0] for c in connection.creation._destroy_test_db.call_args_list}

    def test_matching_stamp(self):
        dropped = self.get_dropped_databases({
            'test_netbox': STAMP,
            'test_netbox_1': None,
        })
        self.assertEqual(dropped, set())

    def test_stale_stamp(self):
        dropped = self.get_dropped_databases({
            'netbox': None,
            'test_netbox': f'{runner.FINGERPRINT_PREFIX}old',
            'test_netbox_1': None,
            'test_netbox_12': None,
            'test_netbox_branching': None,
            'test_netbox_1_old': None,
        })
        self.assertEqual(dropped, {'test_netbox', 'test_netbox_1', 'test_netbox_12'})

    def test_missing_stamp(self):
        dropped = self.get_dropped_databases({
            'test_netbox': None,
            'test_netbox_1': None,
        })
        self.assertEqual(dropped, {'test_netbox', 'test_netbox_1'})

    def test_missing_database(self):
        dropped = self.get_dropped_databases({
            'test_netbox_1': None,
        })
        self.assertEqual(dropped, {'test_netbox_1'})

    def test_drop_error(self):
        connection = get_mock_connection(databases={'test_netbox': None})
        connection.creation._destroy_test_db.side_effect = OperationalError('database is being accessed')

        with self.assertRaises(SystemExit) as cm:
            NetBoxTestRunner(keepdb=True, verbosity=0)._discard_stale_test_databases(connection, STAMP)
        self.assertEqual(cm.exception.code, 2)
        self.assertIn('Close any other connections', connection.creation.log.call_args.args[0])


@mock.patch.object(runner, 'get_schema_fingerprint', return_value='abc')
@mock.patch.object(runner, '_write_stamp')
@mock.patch.object(NetBoxTestRunner, '_discard_stale_test_databases')
class SetupDatabasesTestCase(SimpleTestCase):

    def setUp(self):
        self.connections = {
            'default': get_mock_connection(),
            'replica': get_mock_connection(mirror='default'),
        }

        def setup_databases(runner, **kwargs):
            # Mimic Django pointing each set up connection at its test database
            for alias in kwargs['aliases'] if kwargs['aliases'] is not None else self.connections:
                settings_dict = self.connections[alias].settings_dict
                settings_dict['NAME'] = f"test_{settings_dict['NAME']}"
            return 'old_config'

        patchers = (
            mock.patch.object(runner, 'connections', self.connections),
            mock.patch.object(DiscoverRunner, 'setup_databases', autospec=True, side_effect=setup_databases),
        )
        for patcher in patchers:
            patcher.start()
            self.addCleanup(patcher.stop)

    def test_without_keepdb(self, mock_discard, mock_write_stamp, mock_fingerprint):
        old_config = NetBoxTestRunner(keepdb=False, verbosity=0).setup_databases(aliases={'default'})

        self.assertEqual(old_config, 'old_config')
        mock_discard.assert_not_called()
        mock_write_stamp.assert_not_called()

    def test_with_keepdb(self, mock_discard, mock_write_stamp, mock_fingerprint):
        default = self.connections['default']
        old_config = NetBoxTestRunner(keepdb=True, verbosity=0).setup_databases(aliases={'default', 'replica'})

        self.assertEqual(old_config, 'old_config')
        # Mirrors are skipped
        mock_discard.assert_called_once_with(default, STAMP)
        # The stamp is written to the test database, not the original
        mock_write_stamp.assert_called_once_with(default, 'test_netbox', STAMP)

    def test_all_aliases(self, mock_discard, mock_write_stamp, mock_fingerprint):
        NetBoxTestRunner(keepdb=True, verbosity=0).setup_databases(aliases=None)

        mock_discard.assert_called_once_with(self.connections['default'], STAMP)
        mock_write_stamp.assert_called_once_with(self.connections['default'], 'test_netbox', STAMP)

    def test_no_aliases(self, mock_discard, mock_write_stamp, mock_fingerprint):
        # A suite without any database tests (e.g. only SimpleTestCases) must not touch any database
        NetBoxTestRunner(keepdb=True, verbosity=0).setup_databases(aliases=set())

        mock_discard.assert_not_called()
        mock_write_stamp.assert_not_called()


class StampTestDatabaseTestCase(SimpleTestCase):

    @mock.patch.object(runner, 'get_schema_fingerprint', return_value='abc')
    def test_stamp_test_database(self, mock_fingerprint):
        connection = get_mock_connection()

        with mock.patch.object(runner, 'connections', {'default': connection}):
            runner.stamp_test_database()

        cursor = connection.creation._nodb_cursor.return_value.__enter__.return_value
        cursor.execute.assert_called_once_with(f'COMMENT ON DATABASE "test_netbox" IS \'{STAMP}\'')
