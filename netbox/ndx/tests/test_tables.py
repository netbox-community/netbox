from django.contrib.contenttypes.models import ContentType
from django.test import RequestFactory, TestCase

from dcim.models import DeviceType, Manufacturer
from dcim.tables import DeviceTypeTable
from ndx.models import ImportRecord
from users.models import ObjectPermission, User

from .utils import create_import_record


class ImportRecordColumnTestCase(TestCase):

    @classmethod
    def setUpTestData(cls):
        manufacturer = Manufacturer.objects.create(name='Manufacturer', slug='manufacturer')
        cls.device_types = [
            DeviceType.objects.create(manufacturer=manufacturer, model=f'Model {i}', slug=f'model-{i}')
            for i in range(1, 4)
        ]
        cls.records = [
            create_import_record(cls.device_types[0], 'acme/model-1'),
            create_import_record(cls.device_types[1], 'acme/model-2', update_available=True),
        ]
        cls.user = User.objects.create_user(username='user', is_superuser=True)

    def get_table(self, user=None):
        table = DeviceTypeTable(DeviceType.objects.order_by('pk'), exclude=('tags',))
        table.request = RequestFactory().get('/')
        table.request.user = user or self.user
        return table

    def test_render(self):
        table = self.get_table()
        table.paginate(page=1, per_page=10)
        rows = list(table.page.object_list)

        with self.assertNumQueries(1):
            cells = [row.get_cell('ndx') for row in rows]
        self.assertIn(self.records[0].get_absolute_url(), cells[0])
        self.assertIn('text-bg-blue', cells[0])
        self.assertIn('text-bg-warning', cells[1])
        self.assertEqual(cells[2], '')

    def test_export(self):
        table = self.get_table()
        table.columns.show('ndx')
        values = [row.get_cell_value('ndx') for row in table.rows]
        self.assertEqual(values, ['NDX', 'NDX', ''])

    def test_restricted(self):
        # Only import records the user may view are indicated
        user = User.objects.create_user(username='limited')
        permission = ObjectPermission.objects.create(
            name='View', actions=['view'], constraints={'ndx_id': 'acme/model-2'}
        )
        permission.users.add(user)
        permission.object_types.add(ContentType.objects.get_for_model(ImportRecord))
        table = self.get_table(User.objects.get(pk=user.pk))
        values = [row.get_cell_value('ndx') for row in table.rows]
        self.assertEqual(values, ['', 'NDX', ''])
