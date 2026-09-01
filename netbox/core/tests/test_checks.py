from unittest.mock import MagicMock, patch

from django.db import InterfaceError, NotSupportedError, OperationalError, ProgrammingError
from django.test import TestCase

from core.checks import POSTGRESQL_MIN_VERSION, POSTGRESQL_VERSION_MULTIPLIER, check_postgresql_version

# `SHOW server_version_num` results representing the oldest supported and newest unsupported releases
SUPPORTED_VERSION = POSTGRESQL_MIN_VERSION * POSTGRESQL_VERSION_MULTIPLIER
UNSUPPORTED_VERSION = (POSTGRESQL_MIN_VERSION - 1) * POSTGRESQL_VERSION_MULTIPLIER + 10
OBSOLETE_VERSION = (POSTGRESQL_MIN_VERSION - 2) * POSTGRESQL_VERSION_MULTIPLIER + 1


class PostgreSQLVersionCheckTestCase(TestCase):
    """
    Test the system check which enforces NetBox's minimum PostgreSQL version.
    """
    @staticmethod
    def mock_connection(server_version_num=None, exception=None, vendor='postgresql'):
        """
        Return a mock database connection which yields the given `SHOW server_version_num` result, or
        which raises `exception` when a cursor is requested.
        """
        connection = MagicMock()
        connection.vendor = vendor
        if exception is not None:
            connection.cursor.side_effect = exception
        else:
            cursor = MagicMock()
            cursor.fetchone.return_value = (str(server_version_num),)
            connection.cursor.return_value.__enter__.return_value = cursor
        return connection

    @staticmethod
    def mock_connections(**connections):
        """
        Return a patcher replacing the connection handler with the given alias-to-connection mapping.
        """
        return patch('core.checks.connections', connections)

    def test_supported_version(self):
        """
        No error is reported for the minimum supported PostgreSQL version or later.
        """
        for version in (
            SUPPORTED_VERSION,
            SUPPORTED_VERSION + 2,
            SUPPORTED_VERSION + (2 * POSTGRESQL_VERSION_MULTIPLIER),
        ):
            with self.subTest(version=version):
                with self.mock_connections(default=self.mock_connection(version)):
                    self.assertEqual(check_postgresql_version(None, databases=['default']), [])

    def test_unsupported_version(self):
        """
        An error is reported for any release preceding the minimum supported version.
        """
        with self.mock_connections(default=self.mock_connection(UNSUPPORTED_VERSION)):
            errors = check_postgresql_version(None, databases=['default'])
        self.assertEqual(len(errors), 1)
        self.assertEqual(errors[0].id, 'netbox.E001')
        self.assertIn(f'PostgreSQL {POSTGRESQL_MIN_VERSION - 1} is not supported', errors[0].msg)

    def test_connection_rejected_by_django(self):
        """
        Django's backend refuses to connect at all when the server predates its own minimum supported
        version, so the version query never runs. The check must still report the requirement.
        """
        error = NotSupportedError('PostgreSQL 14 or later is required (found 13.10).')
        with self.mock_connections(default=self.mock_connection(exception=error)):
            errors = check_postgresql_version(None, databases=['default'])
        self.assertEqual(len(errors), 1)
        self.assertEqual(errors[0].id, 'netbox.E001')
        self.assertIn(f'NetBox requires PostgreSQL {POSTGRESQL_MIN_VERSION} or later', errors[0].msg)

    def test_database_unavailable(self):
        """
        An unreachable database leaves the version unverified rather than reporting a spurious error.
        """
        exception = OperationalError('could not connect to server')
        with self.mock_connections(default=self.mock_connection(exception=exception)):
            self.assertEqual(check_postgresql_version(None, databases=['default']), [])

    def test_version_query_rejected(self):
        """
        A reachable server which rejects the version query leaves the version unverified, but logs why.
        """
        exception = ProgrammingError('unrecognized configuration parameter')
        with self.mock_connections(default=self.mock_connection(exception=exception)):
            with self.assertLogs('netbox.core.checks', level='WARNING') as cm:
                self.assertEqual(check_postgresql_version(None, databases=['default']), [])
        self.assertIn('Failed to determine the PostgreSQL version', cm.output[0])

    def test_connection_unusable(self):
        """
        An unusable connection leaves the version unverified rather than raising out of the check.
        InterfaceError descends from Error rather than DatabaseError, so it is handled explicitly.
        """
        exception = InterfaceError('connection already closed')
        with self.mock_connections(default=self.mock_connection(exception=exception)):
            self.assertEqual(check_postgresql_version(None, databases=['default']), [])

    def test_version_unparseable(self):
        """
        A version which cannot be parsed as an integer (e.g. as reported by an intervening connection
        pooler) leaves the version unverified, but logs why.
        """
        connection = self.mock_connection(SUPPORTED_VERSION)
        connection.cursor.return_value.__enter__.return_value.fetchone.return_value = ('15.4',)
        with self.mock_connections(default=connection):
            with self.assertLogs('netbox.core.checks', level='WARNING') as cm:
                self.assertEqual(check_postgresql_version(None, databases=['default']), [])
        self.assertIn('Unable to parse the PostgreSQL version', cm.output[0])

    def test_version_query_empty(self):
        """
        A version query which returns no result leaves the version unverified, but logs why.
        """
        connection = self.mock_connection(SUPPORTED_VERSION)
        connection.cursor.return_value.__enter__.return_value.fetchone.return_value = None
        with self.mock_connections(default=connection):
            with self.assertLogs('netbox.core.checks', level='WARNING') as cm:
                self.assertEqual(check_postgresql_version(None, databases=['default']), [])
        self.assertIn('returned no result', cm.output[0])

    def test_specified_aliases(self):
        """
        Only the database aliases supplied by Django are checked, and each is identified by name.
        """
        connections = {
            'default': self.mock_connection(SUPPORTED_VERSION + 2),
            'legacy': self.mock_connection(UNSUPPORTED_VERSION),
        }
        with self.mock_connections(**connections):
            errors = check_postgresql_version(None, databases=['legacy'])
        self.assertEqual(len(errors), 1)
        self.assertIn("Database 'legacy'", errors[0].msg)
        connections['default'].cursor.assert_not_called()

    def test_multiple_aliases(self):
        """
        Every alias supplied by Django is checked.
        """
        connections = {
            'default': self.mock_connection(UNSUPPORTED_VERSION),
            'legacy': self.mock_connection(OBSOLETE_VERSION),
        }
        with self.mock_connections(**connections):
            errors = check_postgresql_version(None, databases=['default', 'legacy'])
        self.assertEqual(len(errors), 2)
        self.assertIn("Database 'default'", errors[0].msg)
        self.assertIn("Database 'legacy'", errors[1].msg)

    def test_no_aliases(self):
        """
        No connection is opened when Django supplies no aliases, indicating that this run may not touch
        the database (e.g. `collectstatic`, or any command which declares no aliases of its own).
        """
        connections = {
            'default': self.mock_connection(UNSUPPORTED_VERSION),
            'legacy': self.mock_connection(OBSOLETE_VERSION),
        }
        with self.mock_connections(**connections):
            self.assertEqual(check_postgresql_version(None, databases=None), [])
        connections['default'].cursor.assert_not_called()
        connections['legacy'].cursor.assert_not_called()

    def test_non_postgresql_connection(self):
        """
        Connections to other types of databases (e.g. those registered by a plugin) are ignored.
        """
        connection = self.mock_connection(vendor='mysql')
        with self.mock_connections(default=connection):
            self.assertEqual(check_postgresql_version(None, databases=['default']), [])
        connection.cursor.assert_not_called()
