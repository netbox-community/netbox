import urllib.parse

from dcim.models import *
from django.contrib.contenttypes.models import ContentType
from django.test import override_settings
from django.urls import reverse
from users.models import ObjectPermission
from utilities.testing import ModelViewTestCase, TestCase, create_tags


class CSVImportTestCase(ModelViewTestCase):
    model = Region

    @classmethod
    def setUpTestData(cls):
        tags = create_tags('Alpha', 'Bravo', 'Charlie')

        # Create three Regions
        regions = (
            Region(name='Region 1', slug='region-1'),
            Region(name='Region 2', slug='region-2'),
            Region(name='Region 3', slug='region-3'),
        )
        for region in regions:
            region.save()

    def _get_csv_data(self, csv_data):
        return '\n'.join(csv_data)

    @override_settings(EXEMPT_VIEW_PERMISSIONS=['*'])
    def test_valid_tags(self):
        csv_data = (
            'name,slug,description,tags',
            'Region 4,region-4,Fourth region,"Alpha,Bravo"',
            'Region 5,region-5,Fourth region,"Alpha,Charlie"',
        )

        data = {
            'csv': self._get_csv_data(csv_data),
        }

        # Assign model-level permission
        obj_perm = ObjectPermission(name='Test permission', actions=['add'])
        obj_perm.save()
        obj_perm.users.add(self.user)
        obj_perm.object_types.add(ContentType.objects.get_for_model(self.model))

        # Try GET with model-level permission
        self.assertHttpStatus(self.client.get(self._get_url('import')), 200)

        # Test POST with permission
        self.assertHttpStatus(self.client.post(self._get_url('import'), data), 200)
        region = Region.objects.get(slug="region-4")
        self.assertTrue("alpha" in region.tags.values_list("slug", flat=True))
        self.assertTrue("bravo" in region.tags.values_list("slug", flat=True))
        region = Region.objects.get(slug="region-5")
        self.assertTrue("alpha" in region.tags.values_list("slug", flat=True))
        self.assertTrue("charlie" in region.tags.values_list("slug", flat=True))

    @override_settings(EXEMPT_VIEW_PERMISSIONS=['*'])
    def test_non_valid_tags(self):
        csv_data = (
            'name,slug,description,tags',
            'Region 4,region-4,Fourth region,"Alpha,Tango"',
        )

        data = {
            'csv': self._get_csv_data(csv_data),
        }

        # Assign model-level permission
        obj_perm = ObjectPermission(name='Test permission', actions=['add'])
        obj_perm.save()
        obj_perm.users.add(self.user)
        obj_perm.object_types.add(ContentType.objects.get_for_model(self.model))

        # Try GET with model-level permission
        self.assertHttpStatus(self.client.get(self._get_url('import')), 200)
        print(self._get_url('import'))

        # Test POST with permission
        self.assertHttpStatus(self.client.post(self._get_url('import'), data), 200)
        self.assertFalse(Region.objects.filter(slug="region-4").exists())
