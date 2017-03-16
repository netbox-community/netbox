from rest_framework import status
from rest_framework.test import APITestCase

from django.contrib.auth.models import User
from django.urls import reverse

from dcim.models import (
    ConsolePortTemplate, ConsoleServerPortTemplate, DeviceBayTemplate, DeviceType, InterfaceTemplate, Manufacturer,
    PowerPortTemplate, PowerOutletTemplate, Rack, RackGroup, RackReservation, RackRole, Region, Site,
)
from users.models import Token


class RegionTest(APITestCase):

    def setUp(self):

        user = User.objects.create(username='testuser', is_superuser=True)
        token = Token.objects.create(user=user)
        self.header = {'HTTP_AUTHORIZATION': 'Token {}'.format(token.key)}

        self.region1 = Region.objects.create(name='Test Region 1', slug='test-region-1')
        self.region2 = Region.objects.create(name='Test Region 2', slug='test-region-2')
        self.region3 = Region.objects.create(name='Test Region 3', slug='test-region-3')

    def test_get_region(self):

        url = reverse('dcim-api:region-detail', kwargs={'pk': self.region1.pk})
        response = self.client.get(url, **self.header)

        self.assertEqual(response.data['name'], self.region1.name)

    def test_list_regions(self):

        url = reverse('dcim-api:region-list')
        response = self.client.get(url, **self.header)

        self.assertEqual(response.data['count'], 3)

    def test_create_region(self):

        data = {
            'name': 'Test Region 4',
            'slug': 'test-region-4',
        }

        url = reverse('dcim-api:region-list')
        response = self.client.post(url, data, **self.header)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Region.objects.count(), 4)
        region4 = Region.objects.get(pk=response.data['id'])
        self.assertEqual(region4.name, data['name'])
        self.assertEqual(region4.slug, data['slug'])

    def test_update_region(self):

        data = {
            'name': 'Test Region X',
            'slug': 'test-region-x',
        }

        url = reverse('dcim-api:region-detail', kwargs={'pk': self.region1.pk})
        response = self.client.put(url, data, **self.header)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Region.objects.count(), 3)
        region1 = Region.objects.get(pk=response.data['id'])
        self.assertEqual(region1.name, data['name'])
        self.assertEqual(region1.slug, data['slug'])

    def test_delete_region(self):

        url = reverse('dcim-api:region-detail', kwargs={'pk': self.region1.pk})
        response = self.client.delete(url, **self.header)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Region.objects.count(), 2)


class SiteTest(APITestCase):

    def setUp(self):

        user = User.objects.create(username='testuser', is_superuser=True)
        token = Token.objects.create(user=user)
        self.header = {'HTTP_AUTHORIZATION': 'Token {}'.format(token.key)}

        self.region1 = Region.objects.create(name='Test Region 1', slug='test-region-1')
        self.region2 = Region.objects.create(name='Test Region 2', slug='test-region-2')
        self.site1 = Site.objects.create(region=self.region1, name='Test Site 1', slug='test-site-1')
        self.site2 = Site.objects.create(region=self.region1, name='Test Site 2', slug='test-site-2')
        self.site3 = Site.objects.create(region=self.region1, name='Test Site 3', slug='test-site-3')

    def test_get_site(self):

        url = reverse('dcim-api:site-detail', kwargs={'pk': self.site1.pk})
        response = self.client.get(url, **self.header)

        self.assertEqual(response.data['name'], self.site1.name)

    def test_list_sites(self):

        url = reverse('dcim-api:site-list')
        response = self.client.get(url, **self.header)

        self.assertEqual(response.data['count'], 3)

    def test_create_site(self):

        data = {
            'name': 'Test Site 4',
            'slug': 'test-site-4',
            'region': self.region1.pk,
        }

        url = reverse('dcim-api:site-list')
        response = self.client.post(url, data, **self.header)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Site.objects.count(), 4)
        site4 = Site.objects.get(pk=response.data['id'])
        self.assertEqual(site4.name, data['name'])
        self.assertEqual(site4.slug, data['slug'])
        self.assertEqual(site4.region_id, data['region'])

    def test_update_site(self):

        data = {
            'name': 'Test Site X',
            'slug': 'test-site-x',
            'region': self.region2.pk,
        }

        url = reverse('dcim-api:site-detail', kwargs={'pk': self.site1.pk})
        response = self.client.put(url, data, **self.header)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Site.objects.count(), 3)
        site1 = Site.objects.get(pk=response.data['id'])
        self.assertEqual(site1.name, data['name'])
        self.assertEqual(site1.slug, data['slug'])
        self.assertEqual(site1.region_id, data['region'])

    def test_delete_site(self):

        url = reverse('dcim-api:site-detail', kwargs={'pk': self.site1.pk})
        response = self.client.delete(url, **self.header)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Site.objects.count(), 2)


class RackGroupTest(APITestCase):

    def setUp(self):

        user = User.objects.create(username='testuser', is_superuser=True)
        token = Token.objects.create(user=user)
        self.header = {'HTTP_AUTHORIZATION': 'Token {}'.format(token.key)}

        self.site1 = Site.objects.create(name='Test Site 1', slug='test-site-1')
        self.site2 = Site.objects.create(name='Test Site 2', slug='test-site-2')
        self.rackgroup1 = RackGroup.objects.create(site=self.site1, name='Test Rack Group 1', slug='test-rack-group-1')
        self.rackgroup2 = RackGroup.objects.create(site=self.site1, name='Test Rack Group 2', slug='test-rack-group-2')
        self.rackgroup3 = RackGroup.objects.create(site=self.site1, name='Test Rack Group 3', slug='test-rack-group-3')

    def test_get_rackgroup(self):

        url = reverse('dcim-api:rackgroup-detail', kwargs={'pk': self.rackgroup1.pk})
        response = self.client.get(url, **self.header)

        self.assertEqual(response.data['name'], self.rackgroup1.name)

    def test_list_rackgroups(self):

        url = reverse('dcim-api:rackgroup-list')
        response = self.client.get(url, **self.header)

        self.assertEqual(response.data['count'], 3)

    def test_create_rackgroup(self):

        data = {
            'name': 'Test Rack Group 4',
            'slug': 'test-rack-group-4',
            'site': self.site1.pk,
        }

        url = reverse('dcim-api:rackgroup-list')
        response = self.client.post(url, data, **self.header)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(RackGroup.objects.count(), 4)
        rackgroup4 = RackGroup.objects.get(pk=response.data['id'])
        self.assertEqual(rackgroup4.name, data['name'])
        self.assertEqual(rackgroup4.slug, data['slug'])
        self.assertEqual(rackgroup4.site_id, data['site'])

    def test_update_rackgroup(self):

        data = {
            'name': 'Test Rack Group X',
            'slug': 'test-rack-group-x',
            'site': self.site2.pk,
        }

        url = reverse('dcim-api:rackgroup-detail', kwargs={'pk': self.rackgroup1.pk})
        response = self.client.put(url, data, **self.header)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(RackGroup.objects.count(), 3)
        rackgroup1 = RackGroup.objects.get(pk=response.data['id'])
        self.assertEqual(rackgroup1.name, data['name'])
        self.assertEqual(rackgroup1.slug, data['slug'])
        self.assertEqual(rackgroup1.site_id, data['site'])

    def test_delete_rackgroup(self):

        url = reverse('dcim-api:rackgroup-detail', kwargs={'pk': self.rackgroup1.pk})
        response = self.client.delete(url, **self.header)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(RackGroup.objects.count(), 2)


class RackRoleTest(APITestCase):

    def setUp(self):

        user = User.objects.create(username='testuser', is_superuser=True)
        token = Token.objects.create(user=user)
        self.header = {'HTTP_AUTHORIZATION': 'Token {}'.format(token.key)}

        self.rackrole1 = RackRole.objects.create(name='Test Rack Role 1', slug='test-rack-role-1', color='ff0000')
        self.rackrole2 = RackRole.objects.create(name='Test Rack Role 2', slug='test-rack-role-2', color='00ff00')
        self.rackrole3 = RackRole.objects.create(name='Test Rack Role 3', slug='test-rack-role-3', color='0000ff')

    def test_get_rackrole(self):

        url = reverse('dcim-api:rackrole-detail', kwargs={'pk': self.rackrole1.pk})
        response = self.client.get(url, **self.header)

        self.assertEqual(response.data['name'], self.rackrole1.name)

    def test_list_rackroles(self):

        url = reverse('dcim-api:rackrole-list')
        response = self.client.get(url, **self.header)

        self.assertEqual(response.data['count'], 3)

    def test_create_rackrole(self):

        data = {
            'name': 'Test Rack Role 4',
            'slug': 'test-rack-role-4',
            'color': 'ffff00',
        }

        url = reverse('dcim-api:rackrole-list')
        response = self.client.post(url, data, **self.header)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(RackRole.objects.count(), 4)
        rackrole1 = RackRole.objects.get(pk=response.data['id'])
        self.assertEqual(rackrole1.name, data['name'])
        self.assertEqual(rackrole1.slug, data['slug'])
        self.assertEqual(rackrole1.color, data['color'])

    def test_update_rackrole(self):

        data = {
            'name': 'Test Rack Role X',
            'slug': 'test-rack-role-x',
            'color': 'ffff00',
        }

        url = reverse('dcim-api:rackrole-detail', kwargs={'pk': self.rackrole1.pk})
        response = self.client.put(url, data, **self.header)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(RackRole.objects.count(), 3)
        rackrole1 = RackRole.objects.get(pk=response.data['id'])
        self.assertEqual(rackrole1.name, data['name'])
        self.assertEqual(rackrole1.slug, data['slug'])
        self.assertEqual(rackrole1.color, data['color'])

    def test_delete_rackrole(self):

        url = reverse('dcim-api:rackrole-detail', kwargs={'pk': self.rackrole1.pk})
        response = self.client.delete(url, **self.header)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(RackRole.objects.count(), 2)


class RackTest(APITestCase):

    def setUp(self):

        user = User.objects.create(username='testuser', is_superuser=True)
        token = Token.objects.create(user=user)
        self.header = {'HTTP_AUTHORIZATION': 'Token {}'.format(token.key)}

        self.site1 = Site.objects.create(name='Test Site 1', slug='test-site-1')
        self.site2 = Site.objects.create(name='Test Site 2', slug='test-site-2')
        self.rackgroup1 = RackGroup.objects.create(site=self.site1, name='Test Rack Group 1', slug='test-rack-group-1')
        self.rackgroup2 = RackGroup.objects.create(site=self.site2, name='Test Rack Group 2', slug='test-rack-group-2')
        self.rackrole1 = RackRole.objects.create(name='Test Rack Role 1', slug='test-rack-role-1', color='ff0000')
        self.rackrole2 = RackRole.objects.create(name='Test Rack Role 2', slug='test-rack-role-2', color='00ff00')
        self.rack1 = Rack.objects.create(
            site=self.site1, group=self.rackgroup1, role=self.rackrole1, name='Test Rack 1',
        )
        self.rack2 = Rack.objects.create(
            site=self.site1, group=self.rackgroup1, role=self.rackrole1, name='Test Rack 2'
        )
        self.rack3 = Rack.objects.create(
            site=self.site1, group=self.rackgroup1, role=self.rackrole1, name='Test Rack 3'
        )

    def test_get_rack(self):

        url = reverse('dcim-api:rack-detail', kwargs={'pk': self.rack1.pk})
        response = self.client.get(url, **self.header)

        self.assertEqual(response.data['name'], self.rack1.name)

    def test_list_racks(self):

        url = reverse('dcim-api:rack-list')
        response = self.client.get(url, **self.header)

        self.assertEqual(response.data['count'], 3)

    def test_create_rack(self):

        data = {
            'name': 'Test Rack 4',
            'site': self.site1.pk,
            'group': self.rackgroup1.pk,
            'role': self.rackrole1.pk,
        }

        url = reverse('dcim-api:rack-list')
        response = self.client.post(url, data, **self.header)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Rack.objects.count(), 4)
        rack4 = Rack.objects.get(pk=response.data['id'])
        self.assertEqual(rack4.name, data['name'])
        self.assertEqual(rack4.site_id, data['site'])
        self.assertEqual(rack4.group_id, data['group'])
        self.assertEqual(rack4.role_id, data['role'])

    def test_update_rack(self):

        data = {
            'name': 'Test Rack X',
            'site': self.site2.pk,
            'group': self.rackgroup2.pk,
            'role': self.rackrole2.pk,
        }

        url = reverse('dcim-api:rack-detail', kwargs={'pk': self.rack1.pk})
        response = self.client.put(url, data, **self.header)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Rack.objects.count(), 3)
        rack1 = Rack.objects.get(pk=response.data['id'])
        self.assertEqual(rack1.name, data['name'])
        self.assertEqual(rack1.site_id, data['site'])
        self.assertEqual(rack1.group_id, data['group'])
        self.assertEqual(rack1.role_id, data['role'])

    def test_delete_rack(self):

        url = reverse('dcim-api:rack-detail', kwargs={'pk': self.rack1.pk})
        response = self.client.delete(url, **self.header)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Rack.objects.count(), 2)


class RackReservationTest(APITestCase):

    def setUp(self):

        user = User.objects.create(username='testuser', is_superuser=True)
        token = Token.objects.create(user=user)
        self.header = {'HTTP_AUTHORIZATION': 'Token {}'.format(token.key)}

        self.user1 = user
        self.site1 = Site.objects.create(name='Test Site 1', slug='test-site-1')
        self.rack1 = Rack.objects.create(site=self.site1, name='Test Rack 1')
        self.rackreservation1 = RackReservation.objects.create(
            rack=self.rack1, units=[1, 2, 3], user=user, description='First reservation',
        )
        self.rackreservation2 = RackReservation.objects.create(
            rack=self.rack1, units=[4, 5, 6], user=user, description='Second reservation',
        )
        self.rackreservation3 = RackReservation.objects.create(
            rack=self.rack1, units=[7, 8, 9], user=user, description='Third reservation',
        )

    def test_get_rackreservation(self):

        url = reverse('dcim-api:rackreservation-detail', kwargs={'pk': self.rackreservation1.pk})
        response = self.client.get(url, **self.header)

        self.assertEqual(response.data['id'], self.rackreservation1.pk)

    def test_list_rackreservations(self):

        url = reverse('dcim-api:rackreservation-list')
        response = self.client.get(url, **self.header)

        self.assertEqual(response.data['count'], 3)

    def test_create_rackreservation(self):

        data = {
            'rack': self.rack1.pk,
            'units': [10, 11, 12],
            'user': self.user1.pk,
            'description': 'Fourth reservation',
        }

        url = reverse('dcim-api:rackreservation-list')
        response = self.client.post(url, data, **self.header)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(RackReservation.objects.count(), 4)
        rackreservation4 = RackReservation.objects.get(pk=response.data['id'])
        self.assertEqual(rackreservation4.rack_id, data['rack'])
        self.assertEqual(rackreservation4.units, data['units'])
        self.assertEqual(rackreservation4.user_id, data['user'])
        self.assertEqual(rackreservation4.description, data['description'])

    def test_update_rackreservation(self):

        data = {
            'rack': self.rack1.pk,
            'units': [10, 11, 12],
            'user': self.user1.pk,
            'description': 'Modified reservation',
        }

        url = reverse('dcim-api:rackreservation-detail', kwargs={'pk': self.rackreservation1.pk})
        response = self.client.put(url, data, **self.header)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(RackReservation.objects.count(), 3)
        rackreservation1 = RackReservation.objects.get(pk=response.data['id'])
        self.assertEqual(rackreservation1.units, data['units'])
        self.assertEqual(rackreservation1.description, data['description'])

    def test_delete_rackreservation(self):

        url = reverse('dcim-api:rackreservation-detail', kwargs={'pk': self.rackreservation1.pk})
        response = self.client.delete(url, **self.header)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(RackReservation.objects.count(), 2)


class ManufacturerTest(APITestCase):

    def setUp(self):

        user = User.objects.create(username='testuser', is_superuser=True)
        token = Token.objects.create(user=user)
        self.header = {'HTTP_AUTHORIZATION': 'Token {}'.format(token.key)}

        self.manufacturer1 = Manufacturer.objects.create(name='Test Manufacturer 1', slug='test-manufacturer-1')
        self.manufacturer2 = Manufacturer.objects.create(name='Test Manufacturer 2', slug='test-manufacturer-2')
        self.manufacturer3 = Manufacturer.objects.create(name='Test Manufacturer 3', slug='test-manufacturer-3')

    def test_get_manufacturer(self):

        url = reverse('dcim-api:manufacturer-detail', kwargs={'pk': self.manufacturer1.pk})
        response = self.client.get(url, **self.header)

        self.assertEqual(response.data['name'], self.manufacturer1.name)

    def test_list_manufacturers(self):

        url = reverse('dcim-api:manufacturer-list')
        response = self.client.get(url, **self.header)

        self.assertEqual(response.data['count'], 3)

    def test_create_manufacturer(self):

        data = {
            'name': 'Test Manufacturer 4',
            'slug': 'test-manufacturer-4',
        }

        url = reverse('dcim-api:manufacturer-list')
        response = self.client.post(url, data, **self.header)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Manufacturer.objects.count(), 4)
        manufacturer4 = Manufacturer.objects.get(pk=response.data['id'])
        self.assertEqual(manufacturer4.name, data['name'])
        self.assertEqual(manufacturer4.slug, data['slug'])

    def test_update_manufacturer(self):

        data = {
            'name': 'Test Manufacturer X',
            'slug': 'test-manufacturer-x',
        }

        url = reverse('dcim-api:manufacturer-detail', kwargs={'pk': self.manufacturer1.pk})
        response = self.client.put(url, data, **self.header)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Manufacturer.objects.count(), 3)
        manufacturer1 = Manufacturer.objects.get(pk=response.data['id'])
        self.assertEqual(manufacturer1.name, data['name'])
        self.assertEqual(manufacturer1.slug, data['slug'])

    def test_delete_manufacturer(self):

        url = reverse('dcim-api:manufacturer-detail', kwargs={'pk': self.manufacturer1.pk})
        response = self.client.delete(url, **self.header)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Manufacturer.objects.count(), 2)


class DeviceTypeTest(APITestCase):

    def setUp(self):

        user = User.objects.create(username='testuser', is_superuser=True)
        token = Token.objects.create(user=user)
        self.header = {'HTTP_AUTHORIZATION': 'Token {}'.format(token.key)}

        self.manufacturer1 = Manufacturer.objects.create(name='Test Manufacturer 1', slug='test-manufacturer-1')
        self.manufacturer2 = Manufacturer.objects.create(name='Test Manufacturer 2', slug='test-manufacturer-2')
        self.devicetype1 = DeviceType.objects.create(
            manufacturer=self.manufacturer1, model='Test Device Type 1', slug='test-device-type-1'
        )
        self.devicetype2 = DeviceType.objects.create(
            manufacturer=self.manufacturer1, model='Test Device Type 2', slug='test-device-type-2'
        )
        self.devicetype3 = DeviceType.objects.create(
            manufacturer=self.manufacturer1, model='Test Device Type 3', slug='test-device-type-3'
        )

    def test_get_devicetype(self):

        url = reverse('dcim-api:devicetype-detail', kwargs={'pk': self.devicetype1.pk})
        response = self.client.get(url, **self.header)

        self.assertEqual(response.data['model'], self.devicetype1.model)

    def test_list_devicetypes(self):

        url = reverse('dcim-api:devicetype-list')
        response = self.client.get(url, **self.header)

        self.assertEqual(response.data['count'], 3)

    def test_create_devicetype(self):

        data = {
            'manufacturer': self.manufacturer1.pk,
            'model': 'Test Device Type 4',
            'slug': 'test-device-type-4',
        }

        url = reverse('dcim-api:devicetype-list')
        response = self.client.post(url, data, **self.header)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(DeviceType.objects.count(), 4)
        devicetype4 = DeviceType.objects.get(pk=response.data['id'])
        self.assertEqual(devicetype4.manufacturer_id, data['manufacturer'])
        self.assertEqual(devicetype4.model, data['model'])
        self.assertEqual(devicetype4.slug, data['slug'])

    def test_update_devicetype(self):

        data = {
            'manufacturer': self.manufacturer2.pk,
            'model': 'Test Device Type X',
            'slug': 'test-device-type-x',
        }

        url = reverse('dcim-api:devicetype-detail', kwargs={'pk': self.devicetype1.pk})
        response = self.client.put(url, data, **self.header)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(DeviceType.objects.count(), 3)
        devicetype1 = DeviceType.objects.get(pk=response.data['id'])
        self.assertEqual(devicetype1.manufacturer_id, data['manufacturer'])
        self.assertEqual(devicetype1.model, data['model'])
        self.assertEqual(devicetype1.slug, data['slug'])

    def test_delete_devicetype(self):

        url = reverse('dcim-api:devicetype-detail', kwargs={'pk': self.devicetype1.pk})
        response = self.client.delete(url, **self.header)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(DeviceType.objects.count(), 2)


class ConsolePortTemplateTest(APITestCase):

    def setUp(self):

        user = User.objects.create(username='testuser', is_superuser=True)
        token = Token.objects.create(user=user)
        self.header = {'HTTP_AUTHORIZATION': 'Token {}'.format(token.key)}

        self.manufacturer = Manufacturer.objects.create(name='Test Manufacturer 1', slug='test-manufacturer-1')
        self.devicetype = DeviceType.objects.create(
            manufacturer=self.manufacturer, model='Test Device Type 1', slug='test-device-type-1'
        )
        self.consoleporttemplate1 = ConsolePortTemplate.objects.create(
            device_type=self.devicetype, name='Test CP Template 1'
        )
        self.consoleporttemplate2 = ConsolePortTemplate.objects.create(
            device_type=self.devicetype, name='Test CP Template 2'
        )
        self.consoleporttemplate3 = ConsolePortTemplate.objects.create(
            device_type=self.devicetype, name='Test CP Template 3'
        )

    def test_get_consoleporttemplate(self):

        url = reverse('dcim-api:consoleporttemplate-detail', kwargs={'pk': self.consoleporttemplate1.pk})
        response = self.client.get(url, **self.header)

        self.assertEqual(response.data['name'], self.consoleporttemplate1.name)

    def test_list_consoleporttemplates(self):

        url = reverse('dcim-api:consoleporttemplate-list')
        response = self.client.get(url, **self.header)

        self.assertEqual(response.data['count'], 3)

    def test_create_consoleporttemplate(self):

        data = {
            'device_type': self.devicetype.pk,
            'name': 'Test CP Template 4',
        }

        url = reverse('dcim-api:consoleporttemplate-list')
        response = self.client.post(url, data, **self.header)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(ConsolePortTemplate.objects.count(), 4)
        consoleporttemplate4 = ConsolePortTemplate.objects.get(pk=response.data['id'])
        self.assertEqual(consoleporttemplate4.device_type_id, data['device_type'])
        self.assertEqual(consoleporttemplate4.name, data['name'])

    def test_update_consoleporttemplate(self):

        data = {
            'device_type': self.devicetype.pk,
            'name': 'Test CP Template X',
        }

        url = reverse('dcim-api:consoleporttemplate-detail', kwargs={'pk': self.consoleporttemplate1.pk})
        response = self.client.put(url, data, **self.header)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(ConsolePortTemplate.objects.count(), 3)
        consoleporttemplate1 = ConsolePortTemplate.objects.get(pk=response.data['id'])
        self.assertEqual(consoleporttemplate1.name, data['name'])

    def test_delete_consoleporttemplate(self):

        url = reverse('dcim-api:consoleporttemplate-detail', kwargs={'pk': self.consoleporttemplate1.pk})
        response = self.client.delete(url, **self.header)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(ConsolePortTemplate.objects.count(), 2)


class ConsoleServerPortTemplateTest(APITestCase):

    def setUp(self):

        user = User.objects.create(username='testuser', is_superuser=True)
        token = Token.objects.create(user=user)
        self.header = {'HTTP_AUTHORIZATION': 'Token {}'.format(token.key)}

        self.manufacturer = Manufacturer.objects.create(name='Test Manufacturer 1', slug='test-manufacturer-1')
        self.devicetype = DeviceType.objects.create(
            manufacturer=self.manufacturer, model='Test Device Type 1', slug='test-device-type-1'
        )
        self.consoleserverporttemplate1 = ConsoleServerPortTemplate.objects.create(
            device_type=self.devicetype, name='Test CSP Template 1'
        )
        self.consoleserverporttemplate2 = ConsoleServerPortTemplate.objects.create(
            device_type=self.devicetype, name='Test CSP Template 2'
        )
        self.consoleserverporttemplate3 = ConsoleServerPortTemplate.objects.create(
            device_type=self.devicetype, name='Test CSP Template 3'
        )

    def test_get_consoleserverporttemplate(self):

        url = reverse('dcim-api:consoleserverporttemplate-detail', kwargs={'pk': self.consoleserverporttemplate1.pk})
        response = self.client.get(url, **self.header)

        self.assertEqual(response.data['name'], self.consoleserverporttemplate1.name)

    def test_list_consoleserverporttemplates(self):

        url = reverse('dcim-api:consoleserverporttemplate-list')
        response = self.client.get(url, **self.header)

        self.assertEqual(response.data['count'], 3)

    def test_create_consoleserverporttemplate(self):

        data = {
            'device_type': self.devicetype.pk,
            'name': 'Test CSP Template 4',
        }

        url = reverse('dcim-api:consoleserverporttemplate-list')
        response = self.client.post(url, data, **self.header)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(ConsoleServerPortTemplate.objects.count(), 4)
        consoleserverporttemplate4 = ConsoleServerPortTemplate.objects.get(pk=response.data['id'])
        self.assertEqual(consoleserverporttemplate4.device_type_id, data['device_type'])
        self.assertEqual(consoleserverporttemplate4.name, data['name'])

    def test_update_consoleserverporttemplate(self):

        data = {
            'device_type': self.devicetype.pk,
            'name': 'Test CSP Template X',
        }

        url = reverse('dcim-api:consoleserverporttemplate-detail', kwargs={'pk': self.consoleserverporttemplate1.pk})
        response = self.client.put(url, data, **self.header)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(ConsoleServerPortTemplate.objects.count(), 3)
        consoleserverporttemplate1 = ConsoleServerPortTemplate.objects.get(pk=response.data['id'])
        self.assertEqual(consoleserverporttemplate1.name, data['name'])

    def test_delete_consoleserverporttemplate(self):

        url = reverse('dcim-api:consoleserverporttemplate-detail', kwargs={'pk': self.consoleserverporttemplate1.pk})
        response = self.client.delete(url, **self.header)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(ConsoleServerPortTemplate.objects.count(), 2)


class PowerPortTemplateTest(APITestCase):

    def setUp(self):

        user = User.objects.create(username='testuser', is_superuser=True)
        token = Token.objects.create(user=user)
        self.header = {'HTTP_AUTHORIZATION': 'Token {}'.format(token.key)}

        self.manufacturer = Manufacturer.objects.create(name='Test Manufacturer 1', slug='test-manufacturer-1')
        self.devicetype = DeviceType.objects.create(
            manufacturer=self.manufacturer, model='Test Device Type 1', slug='test-device-type-1'
        )
        self.powerporttemplate1 = PowerPortTemplate.objects.create(
            device_type=self.devicetype, name='Test PP Template 1'
        )
        self.powerporttemplate2 = PowerPortTemplate.objects.create(
            device_type=self.devicetype, name='Test PP Template 2'
        )
        self.powerporttemplate3 = PowerPortTemplate.objects.create(
            device_type=self.devicetype, name='Test PP Template 3'
        )

    def test_get_powerporttemplate(self):

        url = reverse('dcim-api:powerporttemplate-detail', kwargs={'pk': self.powerporttemplate1.pk})
        response = self.client.get(url, **self.header)

        self.assertEqual(response.data['name'], self.powerporttemplate1.name)

    def test_list_powerporttemplates(self):

        url = reverse('dcim-api:powerporttemplate-list')
        response = self.client.get(url, **self.header)

        self.assertEqual(response.data['count'], 3)

    def test_create_powerporttemplate(self):

        data = {
            'device_type': self.devicetype.pk,
            'name': 'Test PP Template 4',
        }

        url = reverse('dcim-api:powerporttemplate-list')
        response = self.client.post(url, data, **self.header)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(PowerPortTemplate.objects.count(), 4)
        powerporttemplate4 = PowerPortTemplate.objects.get(pk=response.data['id'])
        self.assertEqual(powerporttemplate4.device_type_id, data['device_type'])
        self.assertEqual(powerporttemplate4.name, data['name'])

    def test_update_powerporttemplate(self):

        data = {
            'device_type': self.devicetype.pk,
            'name': 'Test PP Template X',
        }

        url = reverse('dcim-api:powerporttemplate-detail', kwargs={'pk': self.powerporttemplate1.pk})
        response = self.client.put(url, data, **self.header)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(PowerPortTemplate.objects.count(), 3)
        powerporttemplate1 = PowerPortTemplate.objects.get(pk=response.data['id'])
        self.assertEqual(powerporttemplate1.name, data['name'])

    def test_delete_powerporttemplate(self):

        url = reverse('dcim-api:powerporttemplate-detail', kwargs={'pk': self.powerporttemplate1.pk})
        response = self.client.delete(url, **self.header)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(PowerPortTemplate.objects.count(), 2)


class PowerOutletTemplateTest(APITestCase):

    def setUp(self):

        user = User.objects.create(username='testuser', is_superuser=True)
        token = Token.objects.create(user=user)
        self.header = {'HTTP_AUTHORIZATION': 'Token {}'.format(token.key)}

        self.manufacturer = Manufacturer.objects.create(name='Test Manufacturer 1', slug='test-manufacturer-1')
        self.devicetype = DeviceType.objects.create(
            manufacturer=self.manufacturer, model='Test Device Type 1', slug='test-device-type-1'
        )
        self.poweroutlettemplate1 = PowerOutletTemplate.objects.create(
            device_type=self.devicetype, name='Test PO Template 1'
        )
        self.poweroutlettemplate2 = PowerOutletTemplate.objects.create(
            device_type=self.devicetype, name='Test PO Template 2'
        )
        self.poweroutlettemplate3 = PowerOutletTemplate.objects.create(
            device_type=self.devicetype, name='Test PO Template 3'
        )

    def test_get_poweroutlettemplate(self):

        url = reverse('dcim-api:poweroutlettemplate-detail', kwargs={'pk': self.poweroutlettemplate1.pk})
        response = self.client.get(url, **self.header)

        self.assertEqual(response.data['name'], self.poweroutlettemplate1.name)

    def test_list_poweroutlettemplates(self):

        url = reverse('dcim-api:poweroutlettemplate-list')
        response = self.client.get(url, **self.header)

        self.assertEqual(response.data['count'], 3)

    def test_create_poweroutlettemplate(self):

        data = {
            'device_type': self.devicetype.pk,
            'name': 'Test PO Template 4',
        }

        url = reverse('dcim-api:poweroutlettemplate-list')
        response = self.client.post(url, data, **self.header)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(PowerOutletTemplate.objects.count(), 4)
        poweroutlettemplate4 = PowerOutletTemplate.objects.get(pk=response.data['id'])
        self.assertEqual(poweroutlettemplate4.device_type_id, data['device_type'])
        self.assertEqual(poweroutlettemplate4.name, data['name'])

    def test_update_poweroutlettemplate(self):

        data = {
            'device_type': self.devicetype.pk,
            'name': 'Test PO Template X',
        }

        url = reverse('dcim-api:poweroutlettemplate-detail', kwargs={'pk': self.poweroutlettemplate1.pk})
        response = self.client.put(url, data, **self.header)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(PowerOutletTemplate.objects.count(), 3)
        poweroutlettemplate1 = PowerOutletTemplate.objects.get(pk=response.data['id'])
        self.assertEqual(poweroutlettemplate1.name, data['name'])

    def test_delete_poweroutlettemplate(self):

        url = reverse('dcim-api:poweroutlettemplate-detail', kwargs={'pk': self.poweroutlettemplate1.pk})
        response = self.client.delete(url, **self.header)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(PowerOutletTemplate.objects.count(), 2)


class InterfaceTemplateTest(APITestCase):

    def setUp(self):

        user = User.objects.create(username='testuser', is_superuser=True)
        token = Token.objects.create(user=user)
        self.header = {'HTTP_AUTHORIZATION': 'Token {}'.format(token.key)}

        self.manufacturer = Manufacturer.objects.create(name='Test Manufacturer 1', slug='test-manufacturer-1')
        self.devicetype = DeviceType.objects.create(
            manufacturer=self.manufacturer, model='Test Device Type 1', slug='test-device-type-1'
        )
        self.interfacetemplate1 = InterfaceTemplate.objects.create(
            device_type=self.devicetype, name='Test Interface Template 1'
        )
        self.interfacetemplate2 = InterfaceTemplate.objects.create(
            device_type=self.devicetype, name='Test Interface Template 2'
        )
        self.interfacetemplate3 = InterfaceTemplate.objects.create(
            device_type=self.devicetype, name='Test Interface Template 3'
        )

    def test_get_interfacetemplate(self):

        url = reverse('dcim-api:interfacetemplate-detail', kwargs={'pk': self.interfacetemplate1.pk})
        response = self.client.get(url, **self.header)

        self.assertEqual(response.data['name'], self.interfacetemplate1.name)

    def test_list_interfacetemplates(self):

        url = reverse('dcim-api:interfacetemplate-list')
        response = self.client.get(url, **self.header)

        self.assertEqual(response.data['count'], 3)

    def test_create_interfacetemplate(self):

        data = {
            'device_type': self.devicetype.pk,
            'name': 'Test Interface Template 4',
        }

        url = reverse('dcim-api:interfacetemplate-list')
        response = self.client.post(url, data, **self.header)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(InterfaceTemplate.objects.count(), 4)
        interfacetemplate4 = InterfaceTemplate.objects.get(pk=response.data['id'])
        self.assertEqual(interfacetemplate4.device_type_id, data['device_type'])
        self.assertEqual(interfacetemplate4.name, data['name'])

    def test_update_interfacetemplate(self):

        data = {
            'device_type': self.devicetype.pk,
            'name': 'Test Interface Template X',
        }

        url = reverse('dcim-api:interfacetemplate-detail', kwargs={'pk': self.interfacetemplate1.pk})
        response = self.client.put(url, data, **self.header)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(InterfaceTemplate.objects.count(), 3)
        interfacetemplate1 = InterfaceTemplate.objects.get(pk=response.data['id'])
        self.assertEqual(interfacetemplate1.name, data['name'])

    def test_delete_interfacetemplate(self):

        url = reverse('dcim-api:interfacetemplate-detail', kwargs={'pk': self.interfacetemplate1.pk})
        response = self.client.delete(url, **self.header)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(InterfaceTemplate.objects.count(), 2)


class DeviceBayTemplateTest(APITestCase):

    def setUp(self):

        user = User.objects.create(username='testuser', is_superuser=True)
        token = Token.objects.create(user=user)
        self.header = {'HTTP_AUTHORIZATION': 'Token {}'.format(token.key)}

        self.manufacturer = Manufacturer.objects.create(name='Test Manufacturer 1', slug='test-manufacturer-1')
        self.devicetype = DeviceType.objects.create(
            manufacturer=self.manufacturer, model='Test Device Type 1', slug='test-device-type-1'
        )
        self.devicebaytemplate1 = DeviceBayTemplate.objects.create(
            device_type=self.devicetype, name='Test Device Bay Template 1'
        )
        self.devicebaytemplate2 = DeviceBayTemplate.objects.create(
            device_type=self.devicetype, name='Test Device Bay Template 2'
        )
        self.devicebaytemplate3 = DeviceBayTemplate.objects.create(
            device_type=self.devicetype, name='Test Device Bay Template 3'
        )

    def test_get_devicebaytemplate(self):

        url = reverse('dcim-api:devicebaytemplate-detail', kwargs={'pk': self.devicebaytemplate1.pk})
        response = self.client.get(url, **self.header)

        self.assertEqual(response.data['name'], self.devicebaytemplate1.name)

    def test_list_devicebaytemplates(self):

        url = reverse('dcim-api:devicebaytemplate-list')
        response = self.client.get(url, **self.header)

        self.assertEqual(response.data['count'], 3)

    def test_create_devicebaytemplate(self):

        data = {
            'device_type': self.devicetype.pk,
            'name': 'Test Device Bay Template 4',
        }

        url = reverse('dcim-api:devicebaytemplate-list')
        response = self.client.post(url, data, **self.header)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(DeviceBayTemplate.objects.count(), 4)
        devicebaytemplate4 = DeviceBayTemplate.objects.get(pk=response.data['id'])
        self.assertEqual(devicebaytemplate4.device_type_id, data['device_type'])
        self.assertEqual(devicebaytemplate4.name, data['name'])

    def test_update_devicebaytemplate(self):

        data = {
            'device_type': self.devicetype.pk,
            'name': 'Test Device Bay Template X',
        }

        url = reverse('dcim-api:devicebaytemplate-detail', kwargs={'pk': self.devicebaytemplate1.pk})
        response = self.client.put(url, data, **self.header)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(DeviceBayTemplate.objects.count(), 3)
        devicebaytemplate1 = DeviceBayTemplate.objects.get(pk=response.data['id'])
        self.assertEqual(devicebaytemplate1.name, data['name'])

    def test_delete_devicebaytemplate(self):

        url = reverse('dcim-api:devicebaytemplate-detail', kwargs={'pk': self.devicebaytemplate1.pk})
        response = self.client.delete(url, **self.header)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(DeviceBayTemplate.objects.count(), 2)
