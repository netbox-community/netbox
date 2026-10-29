import csv
from collections.abc import Iterator
from io import StringIO
from unittest import skipIf
from unittest.mock import patch

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.db import connection
from django.db.models import QuerySet
from django.http import StreamingHttpResponse
from django.test import RequestFactory, SimpleTestCase, override_settings
from django.test.utils import CaptureQueriesContext
from django.urls import reverse

from dcim.models import DeviceType, Manufacturer, Site
from dcim.views import DeviceTypeListView, SiteListView
from netbox.exporters import (
    CSVExporter,
    Exporter,
    YAMLExporter,
    get_exporter,
    get_exporters,
    register_exporter,
)
from netbox.registry import registry
from utilities.testing import TestCase


class ExporterRegistrationTestCase(SimpleTestCase):

    def _register(self, cls):
        self.addCleanup(registry['exporters'].pop, cls.slug, None)
        return register_exporter(cls)

    def test_core_exporters(self):
        self.assertIsInstance(get_exporter('csv'), CSVExporter)
        self.assertIsInstance(get_exporter('yaml'), YAMLExporter)

    def test_get_exporters(self):
        self.assertIn(get_exporter('csv'), get_exporters(Site))
        self.assertNotIn(get_exporter('yaml'), get_exporters(Site))
        self.assertIn(get_exporter('csv'), get_exporters(DeviceType))
        self.assertIn(get_exporter('yaml'), get_exporters(DeviceType))

    def test_register_exporter(self):
        class TestExporter(Exporter):
            slug = 'test.exporter'
            label = 'Test'
            content_type = 'text/plain'
            file_extension = 'txt'

        self.assertIs(self._register(TestExporter), TestExporter)
        self.assertIsInstance(get_exporter('test.exporter'), TestExporter)

    def test_register_exporter_not_subclass(self):
        class TestExporter:
            slug = 'test.exporter'
            label = 'Test'
            content_type = 'text/plain'
            file_extension = 'txt'

        with self.assertRaises(ImproperlyConfigured):
            self._register(TestExporter)

    def test_register_exporter_missing_attrs(self):
        for attr in ('slug', 'label', 'content_type', 'file_extension'):
            attrs = {
                'slug': 'test.exporter',
                'label': 'Test',
                'content_type': 'text/plain',
                'file_extension': 'txt',
                attr: None,
            }
            with self.subTest(attr=attr), self.assertRaises(ImproperlyConfigured):
                self._register(type('TestExporter', (Exporter,), attrs))

    def test_register_exporter_invalid_slug(self):
        for slug in ('Test', 'my-plugin.xlsx', '1test', 'test.', '.test'):
            attrs = {'slug': slug, 'label': 'Test', 'content_type': 'text/plain', 'file_extension': 'txt'}
            with self.subTest(slug=slug), self.assertRaises(ImproperlyConfigured):
                self._register(type('TestExporter', (Exporter,), attrs))

    def test_register_exporter_duplicate_slug(self):
        class TestExporter(Exporter):
            slug = 'csv'
            label = 'Test'
            content_type = 'text/plain'
            file_extension = 'txt'

        with self.assertRaises(ImproperlyConfigured):
            register_exporter(TestExporter)
        self.assertIsInstance(get_exporter('csv'), CSVExporter)


class CSVExporterTestCase(SimpleTestCase):
    headers = ['Name', 'Count']
    rows = [['Site 1', 1], ['Site, 2', None]]

    def test_write_rows(self):
        data = get_exporter('csv').write_rows(self.headers, iter(self.rows))
        self.assertEqual(list(data), ['Name,Count\r\n', 'Site 1,1\r\n', '"Site, 2",\r\n'])

    def test_write_rows_delimiter(self):
        data = get_exporter('csv').write_rows(self.headers, iter(self.rows), delimiter='semicolon')
        self.assertEqual(''.join(data), 'Name;Count\r\nSite 1;1\r\nSite, 2;\r\n')

    def test_write_rows_invalid_delimiter(self):
        with self.assertRaises(ValueError):
            get_exporter('csv').write_rows(self.headers, iter(self.rows), delimiter='invalid')

    def test_export(self):
        with self.assertRaisesMessage(NotImplementedError, 'call export_rows() instead'):
            get_exporter('csv').export(request=None, queryset=None)


class YAMLExporterTestCase(TestCase):

    def test_export_fetches_peers(self):
        """
        Related objects are fetched for all exported objects at once, rather than one by one.
        """
        for i in range(1, 4):
            manufacturer = Manufacturer.objects.create(name=f'Manufacturer {i}', slug=f'manufacturer-{i}')
            DeviceType.objects.create(manufacturer=manufacturer, model=f'Device Type {i}', slug=f'device-type-{i}')

        with CaptureQueriesContext(connection) as queries:
            get_exporter('yaml').export(request=None, queryset=DeviceType.objects.all())
        manufacturer_queries = [q for q in queries.captured_queries if 'FROM "dcim_manufacturer"' in q['sql']]
        self.assertEqual(len(manufacturer_queries), 1)


class ExportViewTestCase(TestCase):

    @classmethod
    def setUpTestData(cls):
        Site.objects.bulk_create([Site(name=f'Site {i}', slug=f'site-{i}') for i in range(1, 4)])

    def setUp(self):
        super().setUp()
        self.add_permissions('dcim.view_site')
        self.url = reverse('dcim:site_list')
        self.user.config.set('tables.SiteTable.columns', ['name', 'status'], commit=True)

    def get_csv_rows(self, response):
        return list(csv.reader(StringIO(response.content.decode())))

    def test_export_current_view(self):
        for params in ('export=table', 'export=table&export_format=csv'):
            with self.subTest(params=params):
                response = self.client.get(f'{self.url}?{params}')
                self.assertHttpStatus(response, 200)
                self.assertEqual(response['Content-Type'], 'text/csv; charset=utf-8')
                self.assertEqual(response['Content-Disposition'], 'attachment; filename="netbox_sites.csv"')
                rows = self.get_csv_rows(response)
                self.assertEqual(rows[0], ['Name', 'Status'])
                self.assertEqual(rows[1], ['Site 1', 'Active'])
                self.assertEqual(len(rows), 4)

    def test_export_all_data(self):
        for params in ('export', 'export&export_format=csv'):
            with self.subTest(params=params):
                response = self.client.get(f'{self.url}?{params}')
                self.assertHttpStatus(response, 200)
                self.assertEqual(response['Content-Type'], 'text/csv; charset=utf-8')
                rows = self.get_csv_rows(response)
                self.assertEqual(rows[0][:2], ['Name', 'Status'])
                self.assertGreater(len(rows[0]), 2)
                self.assertEqual(len(rows), 4)

    def test_export_filtered(self):
        response = self.client.get(f'{self.url}?export=table&export_format=csv&q=Site 2')
        self.assertEqual(self.get_csv_rows(response)[1:], [['Site 2', 'Active']])

    def test_export_chunked_only_if_streaming(self):
        """
        Table exports fetch records in chunks (using a server-side cursor) only if STREAMING_EXPORTS is enabled.
        """
        for streaming in (False, True):
            with self.subTest(streaming=streaming):
                with (
                    override_settings(STREAMING_EXPORTS=streaming),
                    patch.object(QuerySet, 'iterator', autospec=True, side_effect=QuerySet.iterator) as iterator,
                ):
                    response = self.client.get(f'{self.url}?export=table')
                    content = response.getvalue().decode()
                self.assertEqual(iterator.called, streaming)
                self.assertEqual(
                    content.splitlines(),
                    ['Name,Status', 'Site 1,Active', 'Site 2,Active', 'Site 3,Active'],
                )

    def test_export_csv_delimiter(self):
        self.user.config.set('csv_delimiter', 'semicolon', commit=True)
        response = self.client.get(f'{self.url}?export=table&export_format=csv')
        self.assertEqual(response.content.decode().splitlines()[0], 'Name;Status')

    def test_export_invalid_format(self):
        for params in (
            'export&export_format=invalid',
            'export=table&export_format=invalid',
            'export&export_format=yaml',
        ):
            with self.subTest(params=params):
                self.assertHttpStatus(self.client.get(f'{self.url}?{params}'), 404)

    @skipIf('netbox.tests.dummy_plugin' not in settings.PLUGINS, 'dummy_plugin not in settings.PLUGINS')
    def test_export_plugin_table_exporter(self):
        response = self.client.get(f'{self.url}?export=table&export_format=dummy_plugin.tsv')
        self.assertHttpStatus(response, 200)
        self.assertNotIsInstance(response, StreamingHttpResponse)
        self.assertEqual(response['Content-Type'], 'text/tab-separated-values; charset=utf-8')
        self.assertEqual(response['Content-Disposition'], 'attachment; filename="netbox_sites.tsv"')
        self.assertEqual(response.content.decode().splitlines()[:2], ['Name\tStatus', 'Site 1\tActive'])

    @skipIf('netbox.tests.dummy_plugin' not in settings.PLUGINS, 'dummy_plugin not in settings.PLUGINS')
    def test_export_plugin_exporter(self):
        response = self.client.get(f'{self.url}?export&export_format=dummy_plugin.site_names')
        self.assertHttpStatus(response, 200)
        self.assertNotIsInstance(response, StreamingHttpResponse)
        self.assertEqual(response['Content-Disposition'], 'attachment; filename="netbox_sites.txt"')
        self.assertEqual(response.content.decode(), 'Site 1\nSite 2\nSite 3\n')

        # Streamed if STREAMING_EXPORTS is enabled
        with override_settings(STREAMING_EXPORTS=True):
            response = self.client.get(f'{self.url}?export&export_format=dummy_plugin.site_names')
        self.assertIsInstance(response, StreamingHttpResponse)
        self.assertEqual(response.getvalue().decode(), 'Site 1\nSite 2\nSite 3\n')

        # Not available for the current view
        response = self.client.get(f'{self.url}?export=table&export_format=dummy_plugin.site_names')
        self.assertHttpStatus(response, 404)

        # Not available for other models
        self.add_permissions('dcim.view_devicetype')
        response = self.client.get(f'{reverse("dcim:devicetype_list")}?export&export_format=dummy_plugin.site_names')
        self.assertHttpStatus(response, 404)

    @skipIf('netbox.tests.dummy_plugin' not in settings.PLUGINS, 'dummy_plugin not in settings.PLUGINS')
    def test_export_dropdown(self):
        response = self.client.get(f'{self.url}?status=active')
        self.assertHttpStatus(response, 200)
        self.assertContains(response, '?status=active&export=table&export_format=csv"')
        self.assertContains(response, '?status=active&export=table&export_format=dummy_plugin.tsv"')
        self.assertContains(response, '?status=active&export&export_format=csv"')
        self.assertContains(response, '?status=active&export&export_format=dummy_plugin.tsv"')
        self.assertContains(response, '?status=active&export&export_format=dummy_plugin.site_names"')
        self.assertNotContains(response, 'export=table&export_format=dummy_plugin.site_names')
        self.assertNotContains(response, 'export_format=yaml')

    def test_export_response(self):
        view = SiteListView()
        view.queryset = Site.objects.all()
        exporter = get_exporter('csv')

        for streaming in (False, True):
            for data in ('a,b', b'a,b', bytearray(b'a,b'), memoryview(b'a,b'), iter(['a,', 'b'])):
                with self.subTest(streaming=streaming, type=type(data).__name__):
                    with override_settings(STREAMING_EXPORTS=streaming):
                        response = view.get_export_response(exporter, data)
                    # Only an iterator is streamed, and only if STREAMING_EXPORTS is enabled
                    expect_stream = streaming and isinstance(data, Iterator)
                    self.assertEqual(isinstance(response, StreamingHttpResponse), expect_stream)
                    self.assertEqual(response.getvalue(), b'a,b')

    def test_export_table_override(self):
        """
        Overriding the deprecated export_table() still applies to CSV exports.
        """
        class CustomSiteListView(SiteListView):
            def export_table(self, table, columns=None, filename=None, delimiter=None):
                return super().export_table(table, columns, filename='custom.csv', delimiter=delimiter)

        for params in ({'export': 'table'}, {'export': ''}, {'export': 'table', 'export_format': 'csv'}):
            with self.subTest(params=params):
                request = RequestFactory().get(self.url, params)
                request.user = self.user
                response = CustomSiteListView.as_view()(request)
                self.assertEqual(response['Content-Disposition'], 'attachment; filename="custom.csv"')

    def test_export_yaml_override(self):
        """
        Overriding the deprecated export_yaml() still applies to YAML exports.
        """
        class CustomDeviceTypeListView(DeviceTypeListView):
            def export_yaml(self):
                return 'custom'

        self.add_permissions('dcim.view_devicetype')
        url = reverse('dcim:devicetype_list')
        for params in ({'export': ''}, {'export': '', 'export_format': 'yaml'}):
            with self.subTest(params=params):
                request = RequestFactory().get(url, params)
                request.user = self.user
                response = CustomDeviceTypeListView.as_view()(request)
                self.assertEqual(response['Content-Type'], 'text/yaml')
                self.assertEqual(response.content, b'custom')

    def test_export_yaml(self):
        """
        The deprecated export_yaml() returns the YAML export of the view's queryset.
        """
        manufacturer = Manufacturer.objects.create(name='Manufacturer 1', slug='manufacturer-1')
        DeviceType.objects.create(manufacturer=manufacturer, model='Device Type 1', slug='device-type-1')
        view = DeviceTypeListView()
        view.request = RequestFactory().get('/')
        view.queryset = DeviceType.objects.all()
        self.assertIn('model: Device Type 1', view.export_yaml())
