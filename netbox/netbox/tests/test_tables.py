from django.template import Context, Template
from django.test import RequestFactory, TestCase

from dcim.models import Device, Site
from dcim.tables import DeviceTable
from netbox.tables import NetBoxTable, columns
from utilities.testing import create_tags, create_test_device, create_test_user


class BaseTableTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        create_test_device('Test Device 1')
        cls.user = create_test_user('testuser')

    def test_prefetch_visible_columns(self):
        """
        Verify that the table queryset's prefetch_related lookups correspond to the user's
        visible column preferences. Columns referencing related fields should only be
        prefetched when those columns are visible.
        """
        request = RequestFactory().get('/')
        request.user = self.user

        # Scenario 1: 'rack' (simple FK) and 'region' (nested accessor: site__region) are visible
        self.user.config.set(
            'tables.DeviceTable.columns',
            ['name', 'status', 'site', 'rack', 'region'],
            commit=True,
        )
        table = DeviceTable(Device.objects.all())
        table.configure(request)
        prefetch_lookups = table.data.data._prefetch_related_lookups
        self.assertIn('rack', prefetch_lookups)
        self.assertIn('site__region', prefetch_lookups)

        # Scenario 2: Local fields only; no prefetching
        self.user.config.set(
            'tables.DeviceTable.columns',
            ['name', 'status', 'description'],
            commit=True,
        )
        table = DeviceTable(Device.objects.all())
        table.configure(request)
        prefetch_lookups = table.data.data._prefetch_related_lookups
        self.assertEqual(prefetch_lookups, tuple())


class TagColumnTable(NetBoxTable):
    tags = columns.TagColumn(url_name='dcim:site_list')

    class Meta(NetBoxTable.Meta):
        model = Site
        fields = ('pk', 'name', 'tags',)
        default_columns = fields


class TagColumnTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        tags = create_tags('Alpha', 'Bravo', 'Charlie')

        sites = [
            Site(name=f'Site {i}', slug=f'site-{i}') for i in range(1, 6)
        ]
        Site.objects.bulk_create(sites)
        for site in sites:
            site.tags.add(*tags)

    def test_tagcolumn(self):
        template = Template('{% load render_table from django_tables2 %}{% render_table table %}')
        table = TagColumnTable(Site.objects.all(), orderable=False)
        context = Context({
            'table': table
        })
        template.render(context)
