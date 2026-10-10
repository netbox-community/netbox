from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from dcim.models import Device, DeviceRole, DeviceType, Manufacturer, Site


class ObjectSelectorViewTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user = get_user_model().objects.create_superuser(username='testuser', password='testpass')

        cls.site_1 = Site.objects.create(name='Office1', slug='office1')
        cls.site_2 = Site.objects.create(name='office2', slug='office2')

        manufacturer = Manufacturer.objects.create(name='Test Mfr', slug='test-mfr')
        device_type = DeviceType.objects.create(manufacturer=manufacturer, model='Test Type', slug='test-type')
        role = DeviceRole.objects.create(name='Test Role', slug='test-role')

        cls.device_1 = Device.objects.create(name='Megatron 1', site=cls.site_1, device_type=device_type, role=role)
        cls.device_2 = Device.objects.create(name='Megatron 2', site=cls.site_2, device_type=device_type, role=role)

    def setUp(self):
        self.client.force_login(self.user)

    def get(self, **params):
        params = {'_model': 'dcim.device', 'target': 'id_select_vm', **params}
        return self.client.get(reverse('htmx_object_selector'), params)

    def test_modal_includes_hidden_input_for_static_param(self):
        response = self.get(site_id=self.site_1.pk)
        self.assertContains(response, f'type="hidden" name="site_id" value="{self.site_1.pk}"')

    def test_modal_includes_hidden_input_for_each_value(self):
        response = self.get(site_id=[self.site_1.pk, self.site_2.pk])
        self.assertContains(response, f'type="hidden" name="site_id" value="{self.site_1.pk}"')
        self.assertContains(response, f'type="hidden" name="site_id" value="{self.site_2.pk}"')

    def test_modal_does_not_duplicate_routing_params_as_hidden_inputs(self):
        response = self.get(site_id=self.site_1.pk)
        self.assertNotContains(response, 'type="hidden" name="_model"')
        self.assertNotContains(response, 'type="hidden" name="target"')

    def test_modal_without_static_params_has_no_site_id_hidden_input(self):
        response = self.get()
        self.assertNotContains(response, 'type="hidden" name="site_id"')

    def test_search_filters_by_site(self):
        response = self.get(_search='true', site_id=self.site_1.pk)
        self.assertContains(response, self.device_1.name)
        self.assertNotContains(response, self.device_2.name)
