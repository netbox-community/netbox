from unittest.mock import MagicMock, patch

from django.db import NotSupportedError
from django.test import TestCase

from core.checks import check_postgresql_version


class PostgreSQLVersionCheckTestCase(TestCase):
    """
    Test the system check which enforces NetBox's minimum PostgreSQL version.
    """
    @staticmethod
    def mock_cursor(server_version_num):
        """
        Return a patcher for connection.cursor() yielding the given `SHOW server_version_num` result.
        """
        cursor = MagicMock()
        cursor.fetchone.return_value = (str(server_version_num),)
        context = MagicMock()
        context.__enter__.return_value = cursor
        return patch('core.checks.connection.cursor', return_value=context)

    def test_supported_version(self):
        """
        No error is reported for PostgreSQL 15 or later.
        """
        for version in (150000, 160002, 170000):
            with self.subTest(version=version), self.mock_cursor(version):
                self.assertEqual(check_postgresql_version(None), [])

    def test_unsupported_version(self):
        """
        An error is reported for PostgreSQL 14 and earlier.
        """
        with self.mock_cursor(140010):
            errors = check_postgresql_version(None)
        self.assertEqual(len(errors), 1)
        self.assertEqual(errors[0].id, 'netbox.E001')
        self.assertIn('PostgreSQL 14 is not supported', errors[0].msg)

    def test_connection_rejected_by_django(self):
        """
        Django's backend refuses to connect at all when the server predates its own minimum supported
        version, so the version query never runs. The check must still report the requirement.
        """
        error = NotSupportedError('PostgreSQL 15 or later is required (found 14.10).')
        with patch('core.checks.connection.cursor', side_effect=error):
            errors = check_postgresql_version(None)
        self.assertEqual(len(errors), 1)
        self.assertEqual(errors[0].id, 'netbox.E001')
        self.assertIn('NetBox requires PostgreSQL 15 or later', errors[0].msg)

    def test_database_unavailable(self):
        """
        An unreachable database leaves the version unverified rather than reporting a spurious error.
        """
        with patch('core.checks.connection.cursor', side_effect=Exception('could not connect to server')):
            self.assertEqual(check_postgresql_version(None), [])
