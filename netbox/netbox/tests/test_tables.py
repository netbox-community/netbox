from django.contrib.auth.models import AnonymousUser
from django.template import Context, Template
from django.test import RequestFactory, TestCase

from core.models import ObjectType
from dcim.models import Device, Site
from dcim.tables import DeviceTable
from extras.choices import CustomFieldChoiceColorChoices, CustomFieldTypeChoices
from extras.models import CustomField, CustomFieldChoiceSet
from netbox.tables import NetBoxTable, columns
from utilities.testing import create_tags, create_test_device, create_test_user


class BaseTableTestCase(TestCase):
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

    def test_prefetch_all_columns_for_export(self):
        """
        Verify that related fields for *all* table columns are prefetched when preparing a CSV
        export, including columns which are not currently visible in the user's configured view.
        """
        request = RequestFactory().get('/')
        request.user = self.user

        # Configure the table with only local-field columns visible. Related columns like 'site',
        # 'rack', and 'region' are hidden in the user's view.
        self.user.config.set(
            'tables.DeviceTable.columns',
            ['name', 'status'],
            commit=True,
        )
        table = DeviceTable(Device.objects.all())
        table.configure(request)

        # With only local-field columns visible, no relations should be prefetched yet.
        self.assertEqual(table.data.data._prefetch_related_lookups, tuple())

        # Simulate the CSV "All data" export path: re-apply prefetching for every column that
        # will be included in the export, regardless of visibility.
        export_columns = [col_name for col_name, _ in table.selected_columns + table.available_columns]
        table._apply_prefetching(columns=export_columns)

        prefetch_lookups = table.data.data._prefetch_related_lookups
        self.assertIn('rack', prefetch_lookups)
        self.assertIn('site__region', prefetch_lookups)

    def test_configure_anonymous_user_with_ordering(self):
        """
        Verify that table.configure() does not raise an error when an anonymous
        user sorts a table column.
        """
        request = RequestFactory().get('/?sort=name')
        request.user = AnonymousUser()
        table = DeviceTable(Device.objects.all())
        table.configure(request)


class TagColumnTable(NetBoxTable):
    tags = columns.TagColumn(url_name='dcim:site_list')

    class Meta(NetBoxTable.Meta):
        model = Site
        fields = (
            'pk',
            'name',
            'tags',
        )
        default_columns = fields


class TagColumnTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        tags = create_tags('Alpha', 'Bravo', 'Charlie')

        sites = [Site(name=f'Site {i}', slug=f'site-{i}') for i in range(1, 6)]
        Site.objects.bulk_create(sites)
        for site in sites:
            site.tags.add(*tags)

    def test_tagcolumn(self):
        template = Template('{% load render_table from django_tables2 %}{% render_table table %}')
        table = TagColumnTable(Site.objects.all(), orderable=False)
        context = Context({'table': table})
        template.render(context)


class CustomFieldColumnTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.object_type = ObjectType.objects.get_for_model(Site)

        # Choice set containing one colored and two uncolored choices
        cls.mixed_choice_set = CustomFieldChoiceSet.objects.create(
            name='Mixed Choice Set',
            extra_choices=(
                ('a', 'Option A'),
                ('b', 'Option B'),
                ('c', 'Option C'),
            ),
            choice_colors={
                'a': CustomFieldChoiceColorChoices.RED,
            },
        )

        cls.select_cf = CustomField.objects.create(
            name='select_field',
            type=CustomFieldTypeChoices.TYPE_SELECT,
            choice_set=cls.mixed_choice_set,
            required=False,
        )
        cls.select_cf.object_types.set([cls.object_type])

        cls.multiselect_cf = CustomField.objects.create(
            name='multiselect_field',
            type=CustomFieldTypeChoices.TYPE_MULTISELECT,
            choice_set=cls.mixed_choice_set,
            required=False,
        )
        cls.multiselect_cf.object_types.set([cls.object_type])

    def test_colored_single_select(self):
        column = columns.CustomFieldColumn(self.select_cf)

        rendered = str(column.render('a'))

        self.assertIn('badge', rendered)
        self.assertIn('text-bg-red', rendered)
        self.assertIn('Option A', rendered)

    def test_uncolored_single_select(self):
        column = columns.CustomFieldColumn(self.select_cf)

        rendered = str(column.render('b'))

        self.assertEqual(rendered, 'Option B')
        self.assertNotIn('badge', rendered)

    def test_empty_multiselect(self):
        column = columns.CustomFieldColumn(self.multiselect_cf)

        rendered = column.render([])

        self.assertEqual(rendered, '')

    def test_multiselect_without_selected_colored_choices(self):
        column = columns.CustomFieldColumn(self.multiselect_cf)

        rendered = str(column.render(['b', 'c']))

        self.assertEqual(rendered, 'Option B, Option C')
        self.assertNotIn('badge', rendered)

    def test_multiselect_with_mixed_colored_choices(self):
        column = columns.CustomFieldColumn(self.multiselect_cf)

        rendered = str(column.render(['a', 'b']))

        self.assertIn('Option A', rendered)
        self.assertIn('Option B', rendered)

        self.assertIn('text-bg-red', rendered)
        self.assertIn('text-bg-secondary', rendered)

        self.assertNotIn(',', rendered)

    def test_html_sensitive_multiselect_labels(self):
        choice_set = CustomFieldChoiceSet.objects.create(
            name='HTML Choice Set',
            extra_choices=(
                ('x', '<b>Bold Option</b>'),
                ('y', "<script>alert('xss')</script>"),
            ),
            choice_colors={
                'x': CustomFieldChoiceColorChoices.RED,
            },
        )

        custom_field = CustomField.objects.create(
            name='html_multiselect_field',
            type=CustomFieldTypeChoices.TYPE_MULTISELECT,
            choice_set=choice_set,
            required=False,
        )
        custom_field.object_types.set([self.object_type])

        column = columns.CustomFieldColumn(custom_field)

        rendered = str(column.render(['x', 'y']))

        self.assertIn('&lt;b&gt;Bold Option&lt;/b&gt;', rendered)
        self.assertNotIn('&amp;lt;', rendered)

        self.assertIn('text-bg-red', rendered)
        self.assertIn('text-bg-secondary', rendered)
