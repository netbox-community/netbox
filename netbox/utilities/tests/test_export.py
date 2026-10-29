import importlib
import sys

from django.test import TestCase

from dcim.models import Site
from dcim.tables import SiteTable


# TODO: Remove in NetBox v5.0 along with utilities.export
class DeprecatedExportModuleTestCase(TestCase):

    @classmethod
    def setUpTestData(cls):
        Site.objects.create(name='Site 1', slug='site-1')

    def setUp(self):
        # Re-import the module so that its deprecation warning is raised again
        sys.modules.pop('utilities.export', None)
        with self.assertWarns(DeprecationWarning):
            self.export = importlib.import_module('utilities.export')
        self.table = SiteTable(Site.objects.all())

    def test_table_export(self):
        exporter = self.export.TableExport(
            export_format=self.export.TableExport.CSV,
            table=self.table,
            exclude_columns={'pk', 'actions'},
            delimiter='semicolon',
        )
        response = exporter.response(filename='sites.csv')
        self.assertIn('Site 1;', response.content.decode())

    def test_stream_table_csv_response(self):
        response = self.export.stream_table_csv_response(
            table=self.table,
            exclude_columns={'pk', 'actions'},
            filename='sites.csv',
        )
        self.assertEqual(response['Content-Disposition'], 'attachment; filename="sites.csv"')
        self.assertIn('Site 1,', response.getvalue().decode())
