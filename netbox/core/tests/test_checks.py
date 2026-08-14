from unittest.mock import MagicMock, patch

from django.core.checks import Error
from django.test import SimpleTestCase

from core.checks import check_postgresql_version


def mock_connection(server_version_num):
    """
    Return a mock database connection whose cursor reports the given `server_version_num`.
    """
    connection = MagicMock()
    cursor = connection.cursor.return_value.__enter__.return_value
    cursor.fetchone.return_value = (str(server_version_num),)

    return connection


class CheckPostgresqlVersionTestCase(SimpleTestCase):

    def test_unsupported_version_reports_error(self):
        """
        A PostgreSQL version below the minimum must be reported as an error, to prevent NetBox from
        starting against a database it does not support.
        """
        for server_version_num, major_version in ((130005, 13), (140010, 14)):
            with self.subTest(server_version_num=server_version_num):
                with patch('core.checks.connection', mock_connection(server_version_num)):
                    results = check_postgresql_version(None)

                self.assertEqual(len(results), 1)
                self.assertIsInstance(results[0], Error)
                self.assertEqual(results[0].id, 'netbox.E001')
                self.assertTrue(results[0].is_serious())
                self.assertIn(f'PostgreSQL {major_version} is not supported', results[0].msg)

    def test_supported_version_reports_nothing(self):
        for server_version_num in (150000, 160002, 180001):
            with self.subTest(server_version_num=server_version_num):
                with patch('core.checks.connection', mock_connection(server_version_num)):
                    self.assertEqual(check_postgresql_version(None), [])

    def test_unreachable_database_reports_nothing(self):
        """
        The check must stay silent if the version cannot be determined, so that it does not mask the
        underlying connection failure.
        """
        connection = MagicMock()
        connection.cursor.side_effect = Exception('database unavailable')

        with patch('core.checks.connection', connection):
            self.assertEqual(check_postgresql_version(None), [])
