from __future__ import unicode_literals

from django.urls import reverse
from netaddr import IPNetwork
from rest_framework import status

from dcim.constants import (
    IFACE_FF_1GE_FIXED, IFACE_FF_LAG, IFACE_MODE_TAGGED, SITE_STATUS_ACTIVE, SUBDEVICE_ROLE_CHILD,
    SUBDEVICE_ROLE_PARENT,
)
from dcim.models import (
    ConsolePort, ConsolePortTemplate, ConsoleServerPort, ConsoleServerPortTemplate, Device, DeviceBay,
    DeviceBayTemplate, DeviceRole, DeviceType, Interface, InterfaceConnection, InterfaceTemplate, Manufacturer,
    InventoryItem, Platform, PowerPort, PowerPortTemplate, PowerOutlet, PowerOutletTemplate, Rack, RackGroup,
    RackReservation, RackRole, Region, Site, VirtualChassis,
)
from ipam.models import IPAddress, VLAN
from extras.models import Graph, GRAPH_TYPE_INTERFACE, GRAPH_TYPE_SITE
from utilities.testing import APITestCase
from virtualization.models import Cluster, ClusterType


class RegionTest(APITestCase):

    def setUp(self):

        super(RegionTest, self).setUp()

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

    def test_list_regions_brief(self):

        url = reverse('dcim-api:region-list')
        response = self.client.get('{}?brief=1'.format(url), **self.header)

        self.assertEqual(
            sorted(response.data['results'][0]),
            ['id', 'name', 'slug', 'url']
        )

    def test_create_region(self):

        data = {
            'name': 'Test Region 4',
            'slug': 'test-region-4',
        }

        url = reverse('dcim-api:region-list')
        response = self.client.post(url, data, format='json', **self.header)

        self.assertHttpStatus(response, status.HTTP_201_CREATED)
        self.assertEqual(Region.objects.count(), 4)
        region4 = Region.objects.get(pk=response.data['id'])
        self.assertEqual(region4.name, data['name'])
        self.assertEqual(region4.slug, data['slug'])

    def test_create_region_bulk(self):

        data = [
            {
                'name': 'Test Region 4',
                'slug': 'test-region-4',
            },
            {
                'name': 'Test Region 5',
                'slug': 'test-region-5',
            },
            {
                'name': 'Test Region 6',
                'slug': 'test-region-6',
            },
        ]

        url = reverse('dcim-api:region-list')
        response = self.client.post(url, data, format='json', **self.header)

        self.assertHttpStatus(response, status.HTTP_201_CREATED)
        self.assertEqual(Region.objects.count(), 6)
        self.assertEqual(response.data[0]['name'], data[0]['name'])
        self.assertEqual(response.data[1]['name'], data[1]['name'])
        self.assertEqual(response.data[2]['name'], data[2]['name'])

    def test_update_region(self):

        data = {
            'name': 'Test Region X',
            'slug': 'test-region-x',
        }

        url = reverse('dcim-api:region-detail', kwargs={'pk': self.region1.pk})
        response = self.client.put(url, data, format='json', **self.header)

        self.assertHttpStatus(response, status.HTTP_200_OK)
        self.assertEqual(Region.objects.count(), 3)
        region1 = Region.objects.get(pk=response.data['id'])
        self.assertEqual(region1.name, data['name'])
        self.assertEqual(region1.slug, data['slug'])

    def test_delete_region(self):

        url = reverse('dcim-api:region-detail', kwargs={'pk': self.region1.pk})
        response = self.client.delete(url, **self.header)

        self.assertHttpStatus(response, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Region.objects.count(), 2)


class SiteTest(APITestCase):

    def setUp(self):

        super(SiteTest, self).setUp()

        self.region1 = Region.objects.create(name='Test Region 1', slug='test-region-1')
        self.region2 = Region.objects.create(name='Test Region 2', slug='test-region-2')
        self.site1 = Site.objects.create(region=self.region1, name='Test Site 1', slug='test-site-1')
        self.site2 = Site.objects.create(region=self.region1, name='Test Site 2', slug='test-site-2')
        self.site3 = Site.objects.create(region=self.region1, name='Test Site 3', slug='test-site-3')

    def test_get_site(self):

        url = reverse('dcim-api:site-detail', kwargs={'pk': self.site1.pk})
        response = self.client.get(url, **self.header)

        self.assertEqual(response.data['name'], self.site1.name)

    def test_get_site_graphs(self):

        self.graph1 = Graph.objects.create(
            type=GRAPH_TYPE_SITE, name='Test Graph 1',
            source='http://example.com/graphs.py?site={{ obj.slug }}&foo=1'
        )
        self.graph2 = Graph.objects.create(
            type=GRAPH_TYPE_SITE, name='Test Graph 2',
            source='http://example.com/graphs.py?site={{ obj.slug }}&foo=2'
        )
        self.graph3 = Graph.objects.create(
            type=GRAPH_TYPE_SITE, name='Test Graph 3',
            source='http://example.com/graphs.py?site={{ obj.slug }}&foo=3'
        )

        url = reverse('dcim-api:site-graphs', kwargs={'pk': self.site1.pk})
        response = self.client.get(url, **self.header)

        self.assertEqual(len(response.data), 3)
        self.assertEqual(response.data[0]['embed_url'], 'http://example.com/graphs.py?site=test-site-1&foo=1')

    def test_list_sites(self):

        url = reverse('dcim-api:site-list')
        response = self.client.get(url, **self.header)

        self.assertEqual(response.data['count'], 3)

    def test_list_sites_brief(self):

        url = reverse('dcim-api:site-list')
        response = self.client.get('{}?brief=1'.format(url), **self.header)

        self.assertEqual(
            sorted(response.data['results'][0]),
            ['id', 'name', 'slug', 'url']
        )

    def test_create_site(self):

        data = {
            'name': 'Test Site 4',
            'slug': 'test-site-4',
            'region': self.region1.pk,
            'status': SITE_STATUS_ACTIVE,
        }

        url = reverse('dcim-api:site-list')
        response = self.client.post(url, data, format='json', **self.header)

        self.assertHttpStatus(response, status.HTTP_201_CREATED)
        self.assertEqual(Site.objects.count(), 4)
        site4 = Site.objects.get(pk=response.data['id'])
        self.assertEqual(site4.name, data['name'])
        self.assertEqual(site4.slug, data['slug'])
        self.assertEqual(site4.region_id, data['region'])

    def test_create_site_bulk(self):

        data = [
            {
                'name': 'Test Site 4',
                'slug': 'test-site-4',
                'region': self.region1.pk,
                'status': SITE_STATUS_ACTIVE,
            },
            {
                'name': 'Test Site 5',
                'slug': 'test-site-5',
                'region': self.region1.pk,
                'status': SITE_STATUS_ACTIVE,
            },
            {
                'name': 'Test Site 6',
                'slug': 'test-site-6',
                'region': self.region1.pk,
                'status': SITE_STATUS_ACTIVE,
            },
        ]

        url = reverse('dcim-api:site-list')
        response = self.client.post(url, data, format='json', **self.header)

        self.assertHttpStatus(response, status.HTTP_201_CREATED)
        self.assertEqual(Site.objects.count(), 6)
        self.assertEqual(response.data[0]['name'], data[0]['name'])
        self.assertEqual(response.data[1]['name'], data[1]['name'])
        self.assertEqual(response.data[2]['name'], data[2]['name'])

    def test_update_site(self):

        data = {
            'name': 'Test Site X',
            'slug': 'test-site-x',
            'region': self.region2.pk,
        }

        url = reverse('dcim-api:site-detail', kwargs={'pk': self.site1.pk})
        response = self.client.put(url, data, format='json', **self.header)

        self.assertHttpStatus(response, status.HTTP_200_OK)
        self.assertEqual(Site.objects.count(), 3)
        site1 = Site.objects.get(pk=response.data['id'])
        self.assertEqual(site1.name, data['name'])
        self.assertEqual(site1.slug, data['slug'])
        self.assertEqual(site1.region_id, data['region'])

    def test_delete_site(self):

        url = reverse('dcim-api:site-detail', kwargs={'pk': self.site1.pk})
        response = self.client.delete(url, **self.header)

        self.assertHttpStatus(response, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Site.objects.count(), 2)


class RackGroupTest(APITestCase):

    def setUp(self):

        super(RackGroupTest, self).setUp()

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

    def test_list_rackgroups_brief(self):

        url = reverse('dcim-api:rackgroup-list')
        response = self.client.get('{}?brief=1'.format(url), **self.header)

        self.assertEqual(
            sorted(response.data['results'][0]),
            ['id', 'name', 'slug', 'url']
        )

    def test_create_rackgroup(self):

        data = {
            'name': 'Test Rack Group 4',
            'slug': 'test-rack-group-4',
            'site': self.site1.pk,
        }

        url = reverse('dcim-api:rackgroup-list')
        response = self.client.post(url, data, format='json', **self.header)

        self.assertHttpStatus(response, status.HTTP_201_CREATED)
        self.assertEqual(RackGroup.objects.count(), 4)
        rackgroup4 = RackGroup.objects.get(pk=response.data['id'])
        self.assertEqual(rackgroup4.name, data['name'])
        self.assertEqual(rackgroup4.slug, data['slug'])
        self.assertEqual(rackgroup4.site_id, data['site'])

    def test_create_rackgroup_bulk(self):

        data = [
            {
                'name': 'Test Rack Group 4',
                'slug': 'test-rack-group-4',
                'site': self.site1.pk,
            },
            {
                'name': 'Test Rack Group 5',
                'slug': 'test-rack-group-5',
                'site': self.site1.pk,
            },
            {
                'name': 'Test Rack Group 6',
                'slug': 'test-rack-group-6',
                'site': self.site1.pk,
            },
        ]

        url = reverse('dcim-api:rackgroup-list')
        response = self.client.post(url, data, format='json', **self.header)

        self.assertHttpStatus(response, status.HTTP_201_CREATED)
        self.assertEqual(RackGroup.objects.count(), 6)
        self.assertEqual(response.data[0]['name'], data[0]['name'])
        self.assertEqual(response.data[1]['name'], data[1]['name'])
        self.assertEqual(response.data[2]['name'], data[2]['name'])

    def test_update_rackgroup(self):

        data = {
            'name': 'Test Rack Group X',
            'slug': 'test-rack-group-x',
            'site': self.site2.pk,
        }

        url = reverse('dcim-api:rackgroup-detail', kwargs={'pk': self.rackgroup1.pk})
        response = self.client.put(url, data, format='json', **self.header)

        self.assertHttpStatus(response, status.HTTP_200_OK)
        self.assertEqual(RackGroup.objects.count(), 3)
        rackgroup1 = RackGroup.objects.get(pk=response.data['id'])
        self.assertEqual(rackgroup1.name, data['name'])
        self.assertEqual(rackgroup1.slug, data['slug'])
        self.assertEqual(rackgroup1.site_id, data['site'])

    def test_delete_rackgroup(self):

        url = reverse('dcim-api:rackgroup-detail', kwargs={'pk': self.rackgroup1.pk})
        response = self.client.delete(url, **self.header)

        self.assertHttpStatus(response, status.HTTP_204_NO_CONTENT)
        self.assertEqual(RackGroup.objects.count(), 2)


class RackRoleTest(APITestCase):

    def setUp(self):

        super(RackRoleTest, self).setUp()

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

    def test_list_rackroles_brief(self):

        url = reverse('dcim-api:rackrole-list')
        response = self.client.get('{}?brief=1'.format(url), **self.header)

        self.assertEqual(
            sorted(response.data['results'][0]),
            ['id', 'name', 'slug', 'url']
        )

    def test_create_rackrole(self):

        data = {
            'name': 'Test Rack Role 4',
            'slug': 'test-rack-role-4',
            'color': 'ffff00',
        }

        url = reverse('dcim-api:rackrole-list')
        response = self.client.post(url, data, format='json', **self.header)

        self.assertHttpStatus(response, status.HTTP_201_CREATED)
        self.assertEqual(RackRole.objects.count(), 4)
        rackrole1 = RackRole.objects.get(pk=response.data['id'])
        self.assertEqual(rackrole1.name, data['name'])
        self.assertEqual(rackrole1.slug, data['slug'])
        self.assertEqual(rackrole1.color, data['color'])

    def test_create_rackrole_bulk(self):

        data = [
            {
                'name': 'Test Rack Role 4',
                'slug': 'test-rack-role-4',
                'color': 'ffff00',
            },
            {
                'name': 'Test Rack Role 5',
                'slug': 'test-rack-role-5',
                'color': 'ffff00',
            },
            {
                'name': 'Test Rack Role 6',
                'slug': 'test-rack-role-6',
                'color': 'ffff00',
            },
        ]

        url = reverse('dcim-api:rackrole-list')
        response = self.client.post(url, data, format='json', **self.header)

        self.assertHttpStatus(response, status.HTTP_201_CREATED)
        self.assertEqual(RackRole.objects.count(), 6)
        self.assertEqual(response.data[0]['name'], data[0]['name'])
        self.assertEqual(response.data[1]['name'], data[1]['name'])
        self.assertEqual(response.data[2]['name'], data[2]['name'])

    def test_update_rackrole(self):

        data = {
            'name': 'Test Rack Role X',
            'slug': 'test-rack-role-x',
            'color': 'ffff00',
        }

        url = reverse('dcim-api:rackrole-detail', kwargs={'pk': self.rackrole1.pk})
        response = self.client.put(url, data, format='json', **self.header)

        self.assertHttpStatus(response, status.HTTP_200_OK)
        self.assertEqual(RackRole.objects.count(), 3)
        rackrole1 = RackRole.objects.get(pk=response.data['id'])
        self.assertEqual(rackrole1.name, data['name'])
        self.assertEqual(rackrole1.slug, data['slug'])
        self.assertEqual(rackrole1.color, data['color'])

    def test_delete_rackrole(self):

        url = reverse('dcim-api:rackrole-detail', kwargs={'pk': self.rackrole1.pk})
        response = self.client.delete(url, **self.header)

        self.assertHttpStatus(response, status.HTTP_204_NO_CONTENT)
        self.assertEqual(RackRole.objects.count(), 2)


class RackTest(APITestCase):

    def setUp(self):

        super(RackTest, self).setUp()

        self.site1 = Site.objects.create(name='Test Site 1', slug='test-site-1')
        self.site2 = Site.objects.create(name='Test Site 2', slug='test-site-2')
        self.rackgroup1 = RackGroup.objects.create(site=self.site1, name='Test Rack Group 1', slug='test-rack-group-1')
        self.rackgroup2 = RackGroup.objects.create(site=self.site2, name='Test Rack Group 2', slug='test-rack-group-2')
        self.rackrole1 = RackRole.objects.create(name='Test Rack Role 1', slug='test-rack-role-1', color='ff0000')
        self.rackrole2 = RackRole.objects.create(name='Test Rack Role 2', slug='test-rack-role-2', color='00ff00')
        self.rack1 = Rack.objects.create(
            site=self.site1, group=self.rackgroup1, role=self.rackrole1, name='Test Rack 1', u_height=42,
        )
        self.rack2 = Rack.objects.create(
            site=self.site1, group=self.rackgroup1, role=self.rackrole1, name='Test Rack 2', u_height=42,
        )
        self.rack3 = Rack.objects.create(
            site=self.site1, group=self.rackgroup1, role=self.rackrole1, name='Test Rack 3', u_height=42,
        )

    def test_get_rack(self):

        url = reverse('dcim-api:rack-detail', kwargs={'pk': self.rack1.pk})
        response = self.client.get(url, **self.header)

        self.assertEqual(response.data['name'], self.rack1.name)

    def test_get_rack_units(self):

        url = reverse('dcim-api:rack-units', kwargs={'pk': self.rack1.pk})
        response = self.client.get(url, **self.header)

        self.assertEqual(response.data['count'], 42)

    def test_list_racks(self):

        url = reverse('dcim-api:rack-list')
        response = self.client.get(url, **self.header)

        self.assertEqual(response.data['count'], 3)

    def test_list_racks_brief(self):

        url = reverse('dcim-api:rack-list')
        response = self.client.get('{}?brief=1'.format(url), **self.header)

        self.assertEqual(
            sorted(response.data['results'][0]),
            ['display_name', 'id', 'name', 'url']
        )

    def test_create_rack(self):

        data = {
            'name': 'Test Rack 4',
            'site': self.site1.pk,
            'group': self.rackgroup1.pk,
            'role': self.rackrole1.pk,
        }

        url = reverse('dcim-api:rack-list')
        response = self.client.post(url, data, format='json', **self.header)

        self.assertHttpStatus(response, status.HTTP_201_CREATED)
        self.assertEqual(Rack.objects.count(), 4)
        rack4 = Rack.objects.get(pk=response.data['id'])
        self.assertEqual(rack4.name, data['name'])
        self.assertEqual(rack4.site_id, data['site'])
        self.assertEqual(rack4.group_id, data['group'])
        self.assertEqual(rack4.role_id, data['role'])

    def test_create_rack_bulk(self):

        data = [
            {
                'name': 'Test Rack 4',
                'site': self.site1.pk,
                'group': self.rackgroup1.pk,
                'role': self.rackrole1.pk,
            },
            {
                'name': 'Test Rack 5',
                'site': self.site1.pk,
                'group': self.rackgroup1.pk,
                'role': self.rackrole1.pk,
            },
            {
                'name': 'Test Rack 6',
                'site': self.site1.pk,
                'group': self.rackgroup1.pk,
                'role': self.rackrole1.pk,
            },
        ]

        url = reverse('dcim-api:rack-list')
        response = self.client.post(url, data, format='json', **self.header)

        self.assertHttpStatus(response, status.HTTP_201_CREATED)
        self.assertEqual(Rack.objects.count(), 6)
        self.assertEqual(response.data[0]['name'], data[0]['name'])
        self.assertEqual(response.data[1]['name'], data[1]['name'])
        self.assertEqual(response.data[2]['name'], data[2]['name'])

    def test_update_rack(self):

        data = {
            'name': 'Test Rack X',
            'site': self.site2.pk,
            'group': self.rackgroup2.pk,
            'role': self.rackrole2.pk,
        }

        url = reverse('dcim-api:rack-detail', kwargs={'pk': self.rack1.pk})
        response = self.client.put(url, data, format='json', **self.header)

        self.assertHttpStatus(response, status.HTTP_200_OK)
        self.assertEqual(Rack.objects.count(), 3)
        rack1 = Rack.objects.get(pk=response.data['id'])
        self.assertEqual(rack1.name, data['name'])
        self.assertEqual(rack1.site_id, data['site'])
        self.assertEqual(rack1.group_id, data['group'])
        self.assertEqual(rack1.role_id, data['role'])

    def test_delete_rack(self):

        url = reverse('dcim-api:rack-detail', kwargs={'pk': self.rack1.pk})
        response = self.client.delete(url, **self.header)

        self.assertHttpStatus(response, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Rack.objects.count(), 2)


class RackReservationTest(APITestCase):

    def setUp(self):

        super(RackReservationTest, self).setUp()

        self.site1 = Site.objects.create(name='Test Site 1', slug='test-site-1')
        self.rack1 = Rack.objects.create(site=self.site1, name='Test Rack 1')
        self.rackreservation1 = RackReservation.objects.create(
            rack=self.rack1, units=[1, 2, 3], user=self.user, description='Reservation #1',
        )
        self.rackreservation2 = RackReservation.objects.create(
            rack=self.rack1, units=[4, 5, 6], user=self.user, description='Reservation #2',
        )
        self.rackreservation3 = RackReservation.objects.create(
            rack=self.rack1, units=[7, 8, 9], user=self.user, description='Reservation #3',
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
            'user': self.user.pk,
            'description': 'Fourth reservation',
        }

        url = reverse('dcim-api:rackreservation-list')
        response = self.client.post(url, data, format='json', **self.header)

        self.assertHttpStatus(response, status.HTTP_201_CREATED)
        self.assertEqual(RackReservation.objects.count(), 4)
        rackreservation4 = RackReservation.objects.get(pk=response.data['id'])
        self.assertEqual(rackreservation4.rack_id, data['rack'])
        self.assertEqual(rackreservation4.units, data['units'])
        self.assertEqual(rackreservation4.user_id, data['user'])
        self.assertEqual(rackreservation4.description, data['description'])

    def test_create_rackreservation_bulk(self):

        data = [
            {
                'rack': self.rack1.pk,
                'units': [10, 11, 12],
                'user': self.user.pk,
                'description': 'Reservation #4',
            },
            {
                'rack': self.rack1.pk,
                'units': [13, 14, 15],
                'user': self.user.pk,
                'description': 'Reservation #5',
            },
            {
                'rack': self.rack1.pk,
                'units': [16, 17, 18],
                'user': self.user.pk,
                'description': 'Reservation #6',
            },
        ]

        url = reverse('dcim-api:rackreservation-list')
        response = self.client.post(url, data, format='json', **self.header)

        self.assertHttpStatus(response, status.HTTP_201_CREATED)
        self.assertEqual(RackReservation.objects.count(), 6)
        self.assertEqual(response.data[0]['description'], data[0]['description'])
        self.assertEqual(response.data[1]['description'], data[1]['description'])
        self.assertEqual(response.data[2]['description'], data[2]['description'])

    def test_update_rackreservation(self):

        data = {
            'rack': self.rack1.pk,
            'units': [10, 11, 12],
            'user': self.user.pk,
            'description': 'Modified reservation',
        }

        url = reverse('dcim-api:rackreservation-detail', kwargs={'pk': self.rackreservation1.pk})
        response = self.client.put(url, data, format='json', **self.header)

        self.assertHttpStatus(response, status.HTTP_200_OK)
        self.assertEqual(RackReservation.objects.count(), 3)
        rackreservation1 = RackReservation.objects.get(pk=response.data['id'])
        self.assertEqual(rackreservation1.units, data['units'])
        self.assertEqual(rackreservation1.description, data['description'])

    def test_delete_rackreservation(self):

        url = reverse('dcim-api:rackreservation-detail', kwargs={'pk': self.rackreservation1.pk})
        response = self.client.delete(url, **self.header)

        self.assertHttpStatus(response, status.HTTP_204_NO_CONTENT)
        self.assertEqual(RackReservation.objects.count(), 2)


class ManufacturerTest(APITestCase):

    def setUp(self):

        super(ManufacturerTest, self).setUp()

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

    def test_list_manufacturers_brief(self):

        url = reverse('dcim-api:manufacturer-list')
        response = self.client.get('{}?brief=1'.format(url), **self.header)

        self.assertEqual(
            sorted(response.data['results'][0]),
            ['id', 'name', 'slug', 'url']
        )

    def test_create_manufacturer(self):

        data = {
            'name': 'Test Manufacturer 4',
            'slug': 'test-manufacturer-4',
        }

        url = reverse('dcim-api:manufacturer-list')
        response = self.client.post(url, data, format='json', **self.header)

        self.assertHttpStatus(response, status.HTTP_201_CREATED)
        self.assertEqual(Manufacturer.objects.count(), 4)
        manufacturer4 = Manufacturer.objects.get(pk=response.data['id'])
        self.assertEqual(manufacturer4.name, data['name'])
        self.assertEqual(manufacturer4.slug, data['slug'])

    def test_create_manufacturer_bulk(self):

        data = [
            {
                'name': 'Test Manufacturer 4',
                'slug': 'test-manufacturer-4',
            },
            {
                'name': 'Test Manufacturer 5',
                'slug': 'test-manufacturer-5',
            },
            {
                'name': 'Test Manufacturer 6',
                'slug': 'test-manufacturer-6',
            },
        ]

        url = reverse('dcim-api:manufacturer-list')
        response = self.client.post(url, data, format='json', **self.header)

        self.assertHttpStatus(response, status.HTTP_201_CREATED)
        self.assertEqual(Manufacturer.objects.count(), 6)
        self.assertEqual(response.data[0]['name'], data[0]['name'])
        self.assertEqual(response.data[1]['name'], data[1]['name'])
        self.assertEqual(response.data[2]['name'], data[2]['name'])

    def test_update_manufacturer(self):

        data = {
            'name': 'Test Manufacturer X',
            'slug': 'test-manufacturer-x',
        }

        url = reverse('dcim-api:manufacturer-detail', kwargs={'pk': self.manufacturer1.pk})
        response = self.client.put(url, data, format='json', **self.header)

        self.assertHttpStatus(response, status.HTTP_200_OK)
        self.assertEqual(Manufacturer.objects.count(), 3)
        manufacturer1 = Manufacturer.objects.get(pk=response.data['id'])
        self.assertEqual(manufacturer1.name, data['name'])
        self.assertEqual(manufacturer1.slug, data['slug'])

    def test_delete_manufacturer(self):

        url = reverse('dcim-api:manufacturer-detail', kwargs={'pk': self.manufacturer1.pk})
        response = self.client.delete(url, **self.header)

        self.assertHttpStatus(response, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Manufacturer.objects.count(), 2)


class DeviceTypeTest(APITestCase):

    def setUp(self):

        super(DeviceTypeTest, self).setUp()

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

    def test_list_devicetypes_brief(self):

        url = reverse('dcim-api:devicetype-list')
        response = self.client.get('{}?brief=1'.format(url), **self.header)

        self.assertEqual(
            sorted(response.data['results'][0]),
            ['id', 'manufacturer', 'model', 'slug', 'url']
        )

    def test_create_devicetype(self):

        data = {
            'manufacturer': self.manufacturer1.pk,
            'model': 'Test Device Type 4',
            'slug': 'test-device-type-4',
        }

        url = reverse('dcim-api:devicetype-list')
        response = self.client.post(url, data, format='json', **self.header)

        self.assertHttpStatus(response, status.HTTP_201_CREATED)
        self.assertEqual(DeviceType.objects.count(), 4)
        devicetype4 = DeviceType.objects.get(pk=response.data['id'])
        self.assertEqual(devicetype4.manufacturer_id, data['manufacturer'])
        self.assertEqual(devicetype4.model, data['model'])
        self.assertEqual(devicetype4.slug, data['slug'])

    def test_create_devicetype_bulk(self):

        data = [
            {
                'manufacturer': self.manufacturer1.pk,
                'model': 'Test Device Type 4',
                'slug': 'test-device-type-4',
            },
            {
                'manufacturer': self.manufacturer1.pk,
                'model': 'Test Device Type 5',
                'slug': 'test-device-type-5',
            },
            {
                'manufacturer': self.manufacturer1.pk,
                'model': 'Test Device Type 6',
                'slug': 'test-device-type-6',
            },
        ]

        url = reverse('dcim-api:devicetype-list')
        response = self.client.post(url, data, format='json', **self.header)

        self.assertHttpStatus(response, status.HTTP_201_CREATED)
        self.assertEqual(DeviceType.objects.count(), 6)
        self.assertEqual(response.data[0]['model'], data[0]['model'])
        self.assertEqual(response.data[1]['model'], data[1]['model'])
        self.assertEqual(response.data[2]['model'], data[2]['model'])

    def test_update_devicetype(self):

        data = {
            'manufacturer': self.manufacturer2.pk,
            'model': 'Test Device Type X',
            'slug': 'test-device-type-x',
        }

        url = reverse('dcim-api:devicetype-detail', kwargs={'pk': self.devicetype1.pk})
        response = self.client.put(url, data, format='json', **self.header)

        self.assertHttpStatus(response, status.HTTP_200_OK)
        self.assertEqual(DeviceType.objects.count(), 3)
        devicetype1 = DeviceType.objects.get(pk=response.data['id'])
        self.assertEqual(devicetype1.manufacturer_id, data['manufacturer'])
        self.assertEqual(devicetype1.model, data['model'])
        self.assertEqual(devicetype1.slug, data['slug'])

    def test_delete_devicetype(self):

        url = reverse('dcim-api:devicetype-detail', kwargs={'pk': self.devicetype1.pk})
        response = self.client.delete(url, **self.header)

        self.assertHttpStatus(response, status.HTTP_204_NO_CONTENT)
        self.assertEqual(DeviceType.objects.count(), 2)


class ConsolePortTemplateTest(APITestCase):

    def setUp(self):

        super(ConsolePortTemplateTest, self).setUp()

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
        response = self.client.post(url, data, format='json', **self.header)

        self.assertHttpStatus(response, status.HTTP_201_CREATED)
        self.assertEqual(ConsolePortTemplate.objects.count(), 4)
        consoleporttemplate4 = ConsolePortTemplate.objects.get(pk=response.data['id'])
        self.assertEqual(consoleporttemplate4.device_type_id, data['device_type'])
        self.assertEqual(consoleporttemplate4.name, data['name'])

    def test_create_consoleporttemplate_bulk(self):

        data = [
            {
                'device_type': self.devicetype.pk,
                'name': 'Test CP Template 4',
            },
            {
                'device_type': self.devicetype.pk,
                'name': 'Test CP Template 5',
            },
            {
                'device_type': self.devicetype.pk,
                'name': 'Test CP Template 6',
            },
        ]

        url = reverse('dcim-api:consoleporttemplate-list')
        response = self.client.post(url, data, format='json', **self.header)

        self.assertHttpStatus(response, status.HTTP_201_CREATED)
        self.assertEqual(ConsolePortTemplate.objects.count(), 6)
        self.assertEqual(response.data[0]['name'], data[0]['name'])
        self.assertEqual(response.data[1]['name'], data[1]['name'])
        self.assertEqual(response.data[2]['name'], data[2]['name'])

    def test_update_consoleporttemplate(self):

        data = {
            'device_type': self.devicetype.pk,
            'name': 'Test CP Template X',
        }

        url = reverse('dcim-api:consoleporttemplate-detail', kwargs={'pk': self.consoleporttemplate1.pk})
        response = self.client.put(url, data, format='json', **self.header)

        self.assertHttpStatus(response, status.HTTP_200_OK)
        self.assertEqual(ConsolePortTemplate.objects.count(), 3)
        consoleporttemplate1 = ConsolePortTemplate.objects.get(pk=response.data['id'])
        self.assertEqual(consoleporttemplate1.name, data['name'])

    def test_delete_consoleporttemplate(self):

        url = reverse('dcim-api:consoleporttemplate-detail', kwargs={'pk': self.consoleporttemplate1.pk})
        response = self.client.delete(url, **self.header)

        self.assertHttpStatus(response, status.HTTP_204_NO_CONTENT)
        self.assertEqual(ConsolePortTemplate.objects.count(), 2)


class ConsoleServerPortTemplateTest(APITestCase):

    def setUp(self):

        super(ConsoleServerPortTemplateTest, self).setUp()

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
        response = self.client.post(url, data, format='json', **self.header)

        self.assertHttpStatus(response, status.HTTP_201_CREATED)
        self.assertEqual(ConsoleServerPortTemplate.objects.count(), 4)
        consoleserverporttemplate4 = ConsoleServerPortTemplate.objects.get(pk=response.data['id'])
        self.assertEqual(consoleserverporttemplate4.device_type_id, data['device_type'])
        self.assertEqual(consoleserverporttemplate4.name, data['name'])

    def test_create_consoleserverporttemplate_bulk(self):

        data = [
            {
                'device_type': self.devicetype.pk,
                'name': 'Test CSP Template 4',
            },
            {
                'device_type': self.devicetype.pk,
                'name': 'Test CSP Template 5',
            },
            {
                'device_type': self.devicetype.pk,
                'name': 'Test CSP Template 6',
            },
        ]

        url = reverse('dcim-api:consoleserverporttemplate-list')
        response = self.client.post(url, data, format='json', **self.header)

        self.assertHttpStatus(response, status.HTTP_201_CREATED)
        self.assertEqual(ConsoleServerPortTemplate.objects.count(), 6)
        self.assertEqual(response.data[0]['name'], data[0]['name'])
        self.assertEqual(response.data[1]['name'], data[1]['name'])
        self.assertEqual(response.data[2]['name'], data[2]['name'])

    def test_update_consoleserverporttemplate(self):

        data = {
            'device_type': self.devicetype.pk,
            'name': 'Test CSP Template X',
        }

        url = reverse('dcim-api:consoleserverporttemplate-detail', kwargs={'pk': self.consoleserverporttemplate1.pk})
        response = self.client.put(url, data, format='json', **self.header)

        self.assertHttpStatus(response, status.HTTP_200_OK)
        self.assertEqual(ConsoleServerPortTemplate.objects.count(), 3)
        consoleserverporttemplate1 = ConsoleServerPortTemplate.objects.get(pk=response.data['id'])
        self.assertEqual(consoleserverporttemplate1.name, data['name'])

    def test_delete_consoleserverporttemplate(self):

        url = reverse('dcim-api:consoleserverporttemplate-detail', kwargs={'pk': self.consoleserverporttemplate1.pk})
        response = self.client.delete(url, **self.header)

        self.assertHttpStatus(response, status.HTTP_204_NO_CONTENT)
        self.assertEqual(ConsoleServerPortTemplate.objects.count(), 2)


class PowerPortTemplateTest(APITestCase):

    def setUp(self):

        super(PowerPortTemplateTest, self).setUp()

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
        response = self.client.post(url, data, format='json', **self.header)

        self.assertHttpStatus(response, status.HTTP_201_CREATED)
        self.assertEqual(PowerPortTemplate.objects.count(), 4)
        powerporttemplate4 = PowerPortTemplate.objects.get(pk=response.data['id'])
        self.assertEqual(powerporttemplate4.device_type_id, data['device_type'])
        self.assertEqual(powerporttemplate4.name, data['name'])

    def test_create_powerporttemplate_bulk(self):

        data = [
            {
                'device_type': self.devicetype.pk,
                'name': 'Test PP Template 4',
            },
            {
                'device_type': self.devicetype.pk,
                'name': 'Test PP Template 5',
            },
            {
                'device_type': self.devicetype.pk,
                'name': 'Test PP Template 6',
            },
        ]

        url = reverse('dcim-api:powerporttemplate-list')
        response = self.client.post(url, data, format='json', **self.header)

        self.assertHttpStatus(response, status.HTTP_201_CREATED)
        self.assertEqual(PowerPortTemplate.objects.count(), 6)
        self.assertEqual(response.data[0]['name'], data[0]['name'])
        self.assertEqual(response.data[1]['name'], data[1]['name'])
        self.assertEqual(response.data[2]['name'], data[2]['name'])

    def test_update_powerporttemplate(self):

        data = {
            'device_type': self.devicetype.pk,
            'name': 'Test PP Template X',
        }

        url = reverse('dcim-api:powerporttemplate-detail', kwargs={'pk': self.powerporttemplate1.pk})
        response = self.client.put(url, data, format='json', **self.header)

        self.assertHttpStatus(response, status.HTTP_200_OK)
        self.assertEqual(PowerPortTemplate.objects.count(), 3)
        powerporttemplate1 = PowerPortTemplate.objects.get(pk=response.data['id'])
        self.assertEqual(powerporttemplate1.name, data['name'])

    def test_delete_powerporttemplate(self):

        url = reverse('dcim-api:powerporttemplate-detail', kwargs={'pk': self.powerporttemplate1.pk})
        response = self.client.delete(url, **self.header)

        self.assertHttpStatus(response, status.HTTP_204_NO_CONTENT)
        self.assertEqual(PowerPortTemplate.objects.count(), 2)


class PowerOutletTemplateTest(APITestCase):

    def setUp(self):

        super(PowerOutletTemplateTest, self).setUp()

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
        response = self.client.post(url, data, format='json', **self.header)

        self.assertHttpStatus(response, status.HTTP_201_CREATED)
        self.assertEqual(PowerOutletTemplate.objects.count(), 4)
        poweroutlettemplate4 = PowerOutletTemplate.objects.get(pk=response.data['id'])
        self.assertEqual(poweroutlettemplate4.device_type_id, data['device_type'])
        self.assertEqual(poweroutlettemplate4.name, data['name'])

    def test_create_poweroutlettemplate_bulk(self):

        data = [
            {
                'device_type': self.devicetype.pk,
                'name': 'Test PO Template 4',
            },
            {
                'device_type': self.devicetype.pk,
                'name': 'Test PO Template 5',
            },
            {
                'device_type': self.devicetype.pk,
                'name': 'Test PO Template 6',
            },
        ]

        url = reverse('dcim-api:poweroutlettemplate-list')
        response = self.client.post(url, data, format='json', **self.header)

        self.assertHttpStatus(response, status.HTTP_201_CREATED)
        self.assertEqual(PowerOutletTemplate.objects.count(), 6)
        self.assertEqual(response.data[0]['name'], data[0]['name'])
        self.assertEqual(response.data[1]['name'], data[1]['name'])
        self.assertEqual(response.data[2]['name'], data[2]['name'])

    def test_update_poweroutlettemplate(self):

        data = {
            'device_type': self.devicetype.pk,
            'name': 'Test PO Template X',
        }

        url = reverse('dcim-api:poweroutlettemplate-detail', kwargs={'pk': self.poweroutlettemplate1.pk})
        response = self.client.put(url, data, format='json', **self.header)

        self.assertHttpStatus(response, status.HTTP_200_OK)
        self.assertEqual(PowerOutletTemplate.objects.count(), 3)
        poweroutlettemplate1 = PowerOutletTemplate.objects.get(pk=response.data['id'])
        self.assertEqual(poweroutlettemplate1.name, data['name'])

    def test_delete_poweroutlettemplate(self):

        url = reverse('dcim-api:poweroutlettemplate-detail', kwargs={'pk': self.poweroutlettemplate1.pk})
        response = self.client.delete(url, **self.header)

        self.assertHttpStatus(response, status.HTTP_204_NO_CONTENT)
        self.assertEqual(PowerOutletTemplate.objects.count(), 2)


class InterfaceTemplateTest(APITestCase):

    def setUp(self):

        super(InterfaceTemplateTest, self).setUp()

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
        response = self.client.post(url, data, format='json', **self.header)

        self.assertHttpStatus(response, status.HTTP_201_CREATED)
        self.assertEqual(InterfaceTemplate.objects.count(), 4)
        interfacetemplate4 = InterfaceTemplate.objects.get(pk=response.data['id'])
        self.assertEqual(interfacetemplate4.device_type_id, data['device_type'])
        self.assertEqual(interfacetemplate4.name, data['name'])

    def test_create_interfacetemplate_bulk(self):

        data = [
            {
                'device_type': self.devicetype.pk,
                'name': 'Test Interface Template 4',
            },
            {
                'device_type': self.devicetype.pk,
                'name': 'Test Interface Template 5',
            },
            {
                'device_type': self.devicetype.pk,
                'name': 'Test Interface Template 6',
            },
        ]

        url = reverse('dcim-api:interfacetemplate-list')
        response = self.client.post(url, data, format='json', **self.header)

        self.assertHttpStatus(response, status.HTTP_201_CREATED)
        self.assertEqual(InterfaceTemplate.objects.count(), 6)
        self.assertEqual(response.data[0]['name'], data[0]['name'])
        self.assertEqual(response.data[1]['name'], data[1]['name'])
        self.assertEqual(response.data[2]['name'], data[2]['name'])

    def test_update_interfacetemplate(self):

        data = {
            'device_type': self.devicetype.pk,
            'name': 'Test Interface Template X',
        }

        url = reverse('dcim-api:interfacetemplate-detail', kwargs={'pk': self.interfacetemplate1.pk})
        response = self.client.put(url, data, format='json', **self.header)

        self.assertHttpStatus(response, status.HTTP_200_OK)
        self.assertEqual(InterfaceTemplate.objects.count(), 3)
        interfacetemplate1 = InterfaceTemplate.objects.get(pk=response.data['id'])
        self.assertEqual(interfacetemplate1.name, data['name'])

    def test_delete_interfacetemplate(self):

        url = reverse('dcim-api:interfacetemplate-detail', kwargs={'pk': self.interfacetemplate1.pk})
        response = self.client.delete(url, **self.header)

        self.assertHttpStatus(response, status.HTTP_204_NO_CONTENT)
        self.assertEqual(InterfaceTemplate.objects.count(), 2)


class DeviceBayTemplateTest(APITestCase):

    def setUp(self):

        super(DeviceBayTemplateTest, self).setUp()

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
        response = self.client.post(url, data, format='json', **self.header)

        self.assertHttpStatus(response, status.HTTP_201_CREATED)
        self.assertEqual(DeviceBayTemplate.objects.count(), 4)
        devicebaytemplate4 = DeviceBayTemplate.objects.get(pk=response.data['id'])
        self.assertEqual(devicebaytemplate4.device_type_id, data['device_type'])
        self.assertEqual(devicebaytemplate4.name, data['name'])

    def test_create_devicebaytemplate_bulk(self):

        data = [
            {
                'device_type': self.devicetype.pk,
                'name': 'Test Device Bay Template 4',
            },
            {
                'device_type': self.devicetype.pk,
                'name': 'Test Device Bay Template 5',
            },
            {
                'device_type': self.devicetype.pk,
                'name': 'Test Device Bay Template 6',
            },
        ]

        url = reverse('dcim-api:devicebaytemplate-list')
        response = self.client.post(url, data, format='json', **self.header)

        self.assertHttpStatus(response, status.HTTP_201_CREATED)
        self.assertEqual(DeviceBayTemplate.objects.count(), 6)
        self.assertEqual(response.data[0]['name'], data[0]['name'])
        self.assertEqual(response.data[1]['name'], data[1]['name'])
        self.assertEqual(response.data[2]['name'], data[2]['name'])

    def test_update_devicebaytemplate(self):

        data = {
            'device_type': self.devicetype.pk,
            'name': 'Test Device Bay Template X',
        }

        url = reverse('dcim-api:devicebaytemplate-detail', kwargs={'pk': self.devicebaytemplate1.pk})
        response = self.client.put(url, data, format='json', **self.header)

        self.assertHttpStatus(response, status.HTTP_200_OK)
        self.assertEqual(DeviceBayTemplate.objects.count(), 3)
        devicebaytemplate1 = DeviceBayTemplate.objects.get(pk=response.data['id'])
        self.assertEqual(devicebaytemplate1.name, data['name'])

    def test_delete_devicebaytemplate(self):

        url = reverse('dcim-api:devicebaytemplate-detail', kwargs={'pk': self.devicebaytemplate1.pk})
        response = self.client.delete(url, **self.header)

        self.assertHttpStatus(response, status.HTTP_204_NO_CONTENT)
        self.assertEqual(DeviceBayTemplate.objects.count(), 2)


class DeviceRoleTest(APITestCase):

    def setUp(self):

        super(DeviceRoleTest, self).setUp()

        self.devicerole1 = DeviceRole.objects.create(
            name='Test Device Role 1', slug='test-device-role-1', color='ff0000'
        )
        self.devicerole2 = DeviceRole.objects.create(
            name='Test Device Role 2', slug='test-device-role-2', color='00ff00'
        )
        self.devicerole3 = DeviceRole.objects.create(
            name='Test Device Role 3', slug='test-device-role-3', color='0000ff'
        )

    def test_get_devicerole(self):

        url = reverse('dcim-api:devicerole-detail', kwargs={'pk': self.devicerole1.pk})
        response = self.client.get(url, **self.header)

        self.assertEqual(response.data['name'], self.devicerole1.name)

    def test_list_deviceroles(self):

        url = reverse('dcim-api:devicerole-list')
        response = self.client.get(url, **self.header)

        self.assertEqual(response.data['count'], 3)

    def test_list_deviceroles_brief(self):

        url = reverse('dcim-api:devicerole-list')
        response = self.client.get('{}?brief=1'.format(url), **self.header)

        self.assertEqual(
            sorted(response.data['results'][0]),
            ['id', 'name', 'slug', 'url']
        )

    def test_create_devicerole(self):

        data = {
            'name': 'Test Device Role 4',
            'slug': 'test-device-role-4',
            'color': 'ffff00',
        }

        url = reverse('dcim-api:devicerole-list')
        response = self.client.post(url, data, format='json', **self.header)

        self.assertHttpStatus(response, status.HTTP_201_CREATED)
        self.assertEqual(DeviceRole.objects.count(), 4)
        devicerole4 = DeviceRole.objects.get(pk=response.data['id'])
        self.assertEqual(devicerole4.name, data['name'])
        self.assertEqual(devicerole4.slug, data['slug'])
        self.assertEqual(devicerole4.color, data['color'])

    def test_create_devicerole_bulk(self):

        data = [
            {
                'name': 'Test Device Role 4',
                'slug': 'test-device-role-4',
                'color': 'ffff00',
            },
            {
                'name': 'Test Device Role 5',
                'slug': 'test-device-role-5',
                'color': 'ffff00',
            },
            {
                'name': 'Test Device Role 6',
                'slug': 'test-device-role-6',
                'color': 'ffff00',
            },
        ]

        url = reverse('dcim-api:devicerole-list')
        response = self.client.post(url, data, format='json', **self.header)

        self.assertHttpStatus(response, status.HTTP_201_CREATED)
        self.assertEqual(DeviceRole.objects.count(), 6)
        self.assertEqual(response.data[0]['name'], data[0]['name'])
        self.assertEqual(response.data[1]['name'], data[1]['name'])
        self.assertEqual(response.data[2]['name'], data[2]['name'])

    def test_update_devicerole(self):

        data = {
            'name': 'Test Device Role X',
            'slug': 'test-device-role-x',
            'color': '00ffff',
        }

        url = reverse('dcim-api:devicerole-detail', kwargs={'pk': self.devicerole1.pk})
        response = self.client.put(url, data, format='json', **self.header)

        self.assertHttpStatus(response, status.HTTP_200_OK)
        self.assertEqual(DeviceRole.objects.count(), 3)
        devicerole1 = DeviceRole.objects.get(pk=response.data['id'])
        self.assertEqual(devicerole1.name, data['name'])
        self.assertEqual(devicerole1.slug, data['slug'])
        self.assertEqual(devicerole1.color, data['color'])

    def test_delete_devicerole(self):

        url = reverse('dcim-api:devicerole-detail', kwargs={'pk': self.devicerole1.pk})
        response = self.client.delete(url, **self.header)

        self.assertHttpStatus(response, status.HTTP_204_NO_CONTENT)
        self.assertEqual(DeviceRole.objects.count(), 2)


class PlatformTest(APITestCase):

    def setUp(self):

        super(PlatformTest, self).setUp()

        self.platform1 = Platform.objects.create(name='Test Platform 1', slug='test-platform-1')
        self.platform2 = Platform.objects.create(name='Test Platform 2', slug='test-platform-2')
        self.platform3 = Platform.objects.create(name='Test Platform 3', slug='test-platform-3')

    def test_get_platform(self):

        url = reverse('dcim-api:platform-detail', kwargs={'pk': self.platform1.pk})
        response = self.client.get(url, **self.header)

        self.assertEqual(response.data['name'], self.platform1.name)

    def test_list_platforms(self):

        url = reverse('dcim-api:platform-list')
        response = self.client.get(url, **self.header)

        self.assertEqual(response.data['count'], 3)

    def test_list_platforms_brief(self):

        url = reverse('dcim-api:platform-list')
        response = self.client.get('{}?brief=1'.format(url), **self.header)

        self.assertEqual(
            sorted(response.data['results'][0]),
            ['id', 'name', 'slug', 'url']
        )

    def test_create_platform(self):

        data = {
            'name': 'Test Platform 4',
            'slug': 'test-platform-4',
        }

        url = reverse('dcim-api:platform-list')
        response = self.client.post(url, data, format='json', **self.header)

        self.assertHttpStatus(response, status.HTTP_201_CREATED)
        self.assertEqual(Platform.objects.count(), 4)
        platform4 = Platform.objects.get(pk=response.data['id'])
        self.assertEqual(platform4.name, data['name'])
        self.assertEqual(platform4.slug, data['slug'])

    def test_create_platform_bulk(self):

        data = [
            {
                'name': 'Test Platform 4',
                'slug': 'test-platform-4',
            },
            {
                'name': 'Test Platform 5',
                'slug': 'test-platform-5',
            },
            {
                'name': 'Test Platform 6',
                'slug': 'test-platform-6',
            },
        ]

        url = reverse('dcim-api:platform-list')
        response = self.client.post(url, data, format='json', **self.header)

        self.assertHttpStatus(response, status.HTTP_201_CREATED)
        self.assertEqual(Platform.objects.count(), 6)
        self.assertEqual(response.data[0]['name'], data[0]['name'])
        self.assertEqual(response.data[1]['name'], data[1]['name'])
        self.assertEqual(response.data[2]['name'], data[2]['name'])

    def test_update_platform(self):

        data = {
            'name': 'Test Platform X',
            'slug': 'test-platform-x',
        }

        url = reverse('dcim-api:platform-detail', kwargs={'pk': self.platform1.pk})
        response = self.client.put(url, data, format='json', **self.header)

        self.assertHttpStatus(response, status.HTTP_200_OK)
        self.assertEqual(Platform.objects.count(), 3)
        platform1 = Platform.objects.get(pk=response.data['id'])
        self.assertEqual(platform1.name, data['name'])
        self.assertEqual(platform1.slug, data['slug'])

    def test_delete_platform(self):

        url = reverse('dcim-api:platform-detail', kwargs={'pk': self.platform1.pk})
        response = self.client.delete(url, **self.header)

        self.assertHttpStatus(response, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Platform.objects.count(), 2)


class DeviceTest(APITestCase):

    def setUp(self):

        super(DeviceTest, self).setUp()

        self.site1 = Site.objects.create(name='Test Site 1', slug='test-site-1')
        self.site2 = Site.objects.create(name='Test Site 2', slug='test-site-2')
        manufacturer = Manufacturer.objects.create(name='Test Manufacturer 1', slug='test-manufacturer-1')
        self.devicetype1 = DeviceType.objects.create(
            manufacturer=manufacturer, model='Test Device Type 1', slug='test-device-type-1'
        )
        self.devicetype2 = DeviceType.objects.create(
            manufacturer=manufacturer, model='Test Device Type 2', slug='test-device-type-2'
        )
        self.devicerole1 = DeviceRole.objects.create(
            name='Test Device Role 1', slug='test-device-role-1', color='ff0000'
        )
        self.devicerole2 = DeviceRole.objects.create(
            name='Test Device Role 2', slug='test-device-role-2', color='00ff00'
        )
        cluster_type = ClusterType.objects.create(name='Test Cluster Type 1', slug='test-cluster-type-1')
        self.cluster1 = Cluster.objects.create(name='Test Cluster 1', type=cluster_type)
        self.device1 = Device.objects.create(
            device_type=self.devicetype1,
            device_role=self.devicerole1,
            name='Test Device 1',
            site=self.site1,
            cluster=self.cluster1
        )
        self.device2 = Device.objects.create(
            device_type=self.devicetype1,
            device_role=self.devicerole1,
            name='Test Device 2',
            site=self.site1,
            cluster=self.cluster1
        )
        self.device3 = Device.objects.create(
            device_type=self.devicetype1,
            device_role=self.devicerole1,
            name='Test Device 3',
            site=self.site1,
            cluster=self.cluster1
        )

    def test_get_device(self):

        url = reverse('dcim-api:device-detail', kwargs={'pk': self.device1.pk})
        response = self.client.get(url, **self.header)

        self.assertEqual(response.data['name'], self.device1.name)
        self.assertEqual(response.data['device_role']['id'], self.devicerole1.pk)
        self.assertEqual(response.data['cluster']['id'], self.cluster1.pk)

    def test_list_devices(self):

        url = reverse('dcim-api:device-list')
        response = self.client.get(url, **self.header)

        self.assertEqual(response.data['count'], 3)

    def test_list_devices_brief(self):

        url = reverse('dcim-api:device-list')
        response = self.client.get('{}?brief=1'.format(url), **self.header)

        self.assertEqual(
            sorted(response.data['results'][0]),
            ['display_name', 'id', 'name', 'url']
        )

    def test_create_device(self):

        data = {
            'device_type': self.devicetype1.pk,
            'device_role': self.devicerole1.pk,
            'name': 'Test Device 4',
            'site': self.site1.pk,
            'cluster': self.cluster1.pk,
        }

        url = reverse('dcim-api:device-list')
        response = self.client.post(url, data, format='json', **self.header)

        self.assertHttpStatus(response, status.HTTP_201_CREATED)
        self.assertEqual(Device.objects.count(), 4)
        device4 = Device.objects.get(pk=response.data['id'])
        self.assertEqual(device4.device_type_id, data['device_type'])
        self.assertEqual(device4.device_role_id, data['device_role'])
        self.assertEqual(device4.name, data['name'])
        self.assertEqual(device4.site.pk, data['site'])
        self.assertEqual(device4.cluster.pk, data['cluster'])

    def test_create_device_bulk(self):

        data = [
            {
                'device_type': self.devicetype1.pk,
                'device_role': self.devicerole1.pk,
                'name': 'Test Device 4',
                'site': self.site1.pk,
            },
            {
                'device_type': self.devicetype1.pk,
                'device_role': self.devicerole1.pk,
                'name': 'Test Device 5',
                'site': self.site1.pk,
            },
            {
                'device_type': self.devicetype1.pk,
                'device_role': self.devicerole1.pk,
                'name': 'Test Device 6',
                'site': self.site1.pk,
            },
        ]

        url = reverse('dcim-api:device-list')
        response = self.client.post(url, data, format='json', **self.header)

        self.assertHttpStatus(response, status.HTTP_201_CREATED)
        self.assertEqual(Device.objects.count(), 6)
        self.assertEqual(response.data[0]['name'], data[0]['name'])
        self.assertEqual(response.data[1]['name'], data[1]['name'])
        self.assertEqual(response.data[2]['name'], data[2]['name'])

    def test_update_device(self):

        interface = Interface.objects.create(name='Test Interface 1', device=self.device1)
        ip4_address = IPAddress.objects.create(address=IPNetwork('192.0.2.1/24'), interface=interface)
        ip6_address = IPAddress.objects.create(address=IPNetwork('2001:db8::1/64'), interface=interface)

        data = {
            'device_type': self.devicetype2.pk,
            'device_role': self.devicerole2.pk,
            'name': 'Test Device X',
            'site': self.site2.pk,
            'primary_ip4': ip4_address.pk,
            'primary_ip6': ip6_address.pk,
        }

        url = reverse('dcim-api:device-detail', kwargs={'pk': self.device1.pk})
        response = self.client.put(url, data, format='json', **self.header)

        self.assertHttpStatus(response, status.HTTP_200_OK)
        self.assertEqual(Device.objects.count(), 3)
        device1 = Device.objects.get(pk=response.data['id'])
        self.assertEqual(device1.device_type_id, data['device_type'])
        self.assertEqual(device1.device_role_id, data['device_role'])
        self.assertEqual(device1.name, data['name'])
        self.assertEqual(device1.site.pk, data['site'])
        self.assertEqual(device1.primary_ip4.pk, data['primary_ip4'])
        self.assertEqual(device1.primary_ip6.pk, data['primary_ip6'])

    def test_delete_device(self):

        url = reverse('dcim-api:device-detail', kwargs={'pk': self.device1.pk})
        response = self.client.delete(url, **self.header)

        self.assertHttpStatus(response, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Device.objects.count(), 2)


class ConsolePortTest(APITestCase):

    def setUp(self):

        super(ConsolePortTest, self).setUp()

        site = Site.objects.create(name='Test Site 1', slug='test-site-1')
        manufacturer = Manufacturer.objects.create(name='Test Manufacturer 1', slug='test-manufacturer-1')
        devicetype = DeviceType.objects.create(
            manufacturer=manufacturer, model='Test Device Type 1', slug='test-device-type-1'
        )
        devicerole = DeviceRole.objects.create(
            name='Test Device Role 1', slug='test-device-role-1', color='ff0000'
        )
        self.device = Device.objects.create(
            device_type=devicetype, device_role=devicerole, name='Test Device 1', site=site
        )
        self.consoleport1 = ConsolePort.objects.create(device=self.device, name='Test Console Port 1')
        self.consoleport2 = ConsolePort.objects.create(device=self.device, name='Test Console Port 2')
        self.consoleport3 = ConsolePort.objects.create(device=self.device, name='Test Console Port 3')

    def test_get_consoleport(self):

        url = reverse('dcim-api:consoleport-detail', kwargs={'pk': self.consoleport1.pk})
        response = self.client.get(url, **self.header)

        self.assertEqual(response.data['name'], self.consoleport1.name)

    def test_list_consoleports(self):

        url = reverse('dcim-api:consoleport-list')
        response = self.client.get(url, **self.header)

        self.assertEqual(response.data['count'], 3)

    def test_list_consoleports_brief(self):

        url = reverse('dcim-api:consoleport-list')
        response = self.client.get('{}?brief=1'.format(url), **self.header)

        self.assertEqual(
            sorted(response.data['results'][0]),
            ['device', 'id', 'is_connected', 'name', 'url']
        )

    def test_create_consoleport(self):

        data = {
            'device': self.device.pk,
            'name': 'Test Console Port 4',
        }

        url = reverse('dcim-api:consoleport-list')
        response = self.client.post(url, data, format='json', **self.header)

        self.assertHttpStatus(response, status.HTTP_201_CREATED)
        self.assertEqual(ConsolePort.objects.count(), 4)
        consoleport4 = ConsolePort.objects.get(pk=response.data['id'])
        self.assertEqual(consoleport4.device_id, data['device'])
        self.assertEqual(consoleport4.name, data['name'])

    def test_create_consoleport_bulk(self):

        data = [
            {
                'device': self.device.pk,
                'name': 'Test Console Port 4',
            },
            {
                'device': self.device.pk,
                'name': 'Test Console Port 5',
            },
            {
                'device': self.device.pk,
                'name': 'Test Console Port 6',
            },
        ]

        url = reverse('dcim-api:consoleport-list')
        response = self.client.post(url, data, format='json', **self.header)

        self.assertHttpStatus(response, status.HTTP_201_CREATED)
        self.assertEqual(ConsolePort.objects.count(), 6)
        self.assertEqual(response.data[0]['name'], data[0]['name'])
        self.assertEqual(response.data[1]['name'], data[1]['name'])
        self.assertEqual(response.data[2]['name'], data[2]['name'])

    def test_update_consoleport(self):

        consoleserverport = ConsoleServerPort.objects.create(device=self.device, name='Test CS Port 1')

        data = {
            'device': self.device.pk,
            'name': 'Test Console Port X',
            'cs_port': consoleserverport.pk,
        }

        url = reverse('dcim-api:consoleport-detail', kwargs={'pk': self.consoleport1.pk})
        response = self.client.put(url, data, format='json', **self.header)

        self.assertHttpStatus(response, status.HTTP_200_OK)
        self.assertEqual(ConsolePort.objects.count(), 3)
        consoleport1 = ConsolePort.objects.get(pk=response.data['id'])
        self.assertEqual(consoleport1.name, data['name'])
        self.assertEqual(consoleport1.cs_port_id, data['cs_port'])

    def test_delete_consoleport(self):

        url = reverse('dcim-api:consoleport-detail', kwargs={'pk': self.consoleport1.pk})
        response = self.client.delete(url, **self.header)

        self.assertHttpStatus(response, status.HTTP_204_NO_CONTENT)
        self.assertEqual(ConsolePort.objects.count(), 2)


class ConsoleServerPortTest(APITestCase):

    def setUp(self):

        super(ConsoleServerPortTest, self).setUp()

        site = Site.objects.create(name='Test Site 1', slug='test-site-1')
        manufacturer = Manufacturer.objects.create(name='Test Manufacturer 1', slug='test-manufacturer-1')
        devicetype = DeviceType.objects.create(
            manufacturer=manufacturer, model='Test Device Type 1', slug='test-device-type-1', is_console_server=True
        )
        devicerole = DeviceRole.objects.create(
            name='Test Device Role 1', slug='test-device-role-1', color='ff0000'
        )
        self.device = Device.objects.create(
            device_type=devicetype, device_role=devicerole, name='Test Device 1', site=site
        )
        self.consoleserverport1 = ConsoleServerPort.objects.create(device=self.device, name='Test CS Port 1')
        self.consoleserverport2 = ConsoleServerPort.objects.create(device=self.device, name='Test CS Port 2')
        self.consoleserverport3 = ConsoleServerPort.objects.create(device=self.device, name='Test CS Port 3')

    def test_get_consoleserverport(self):

        url = reverse('dcim-api:consoleserverport-detail', kwargs={'pk': self.consoleserverport1.pk})
        response = self.client.get(url, **self.header)

        self.assertEqual(response.data['name'], self.consoleserverport1.name)

    def test_list_consoleserverports(self):

        url = reverse('dcim-api:consoleserverport-list')
        response = self.client.get(url, **self.header)

        self.assertEqual(response.data['count'], 3)

    def test_list_consoleserverports_brief(self):

        url = reverse('dcim-api:consoleserverport-list')
        response = self.client.get('{}?brief=1'.format(url), **self.header)

        self.assertEqual(
            sorted(response.data['results'][0]),
            ['device', 'id', 'is_connected', 'name', 'url']
        )

    def test_create_consoleserverport(self):

        data = {
            'device': self.device.pk,
            'name': 'Test CS Port 4',
        }

        url = reverse('dcim-api:consoleserverport-list')
        response = self.client.post(url, data, format='json', **self.header)

        self.assertHttpStatus(response, status.HTTP_201_CREATED)
        self.assertEqual(ConsoleServerPort.objects.count(), 4)
        consoleserverport4 = ConsoleServerPort.objects.get(pk=response.data['id'])
        self.assertEqual(consoleserverport4.device_id, data['device'])
        self.assertEqual(consoleserverport4.name, data['name'])

    def test_create_consoleserverport_bulk(self):

        data = [
            {
                'device': self.device.pk,
                'name': 'Test CS Port 4',
            },
            {
                'device': self.device.pk,
                'name': 'Test CS Port 5',
            },
            {
                'device': self.device.pk,
                'name': 'Test CS Port 6',
            },
        ]

        url = reverse('dcim-api:consoleserverport-list')
        response = self.client.post(url, data, format='json', **self.header)

        self.assertHttpStatus(response, status.HTTP_201_CREATED)
        self.assertEqual(ConsoleServerPort.objects.count(), 6)
        self.assertEqual(response.data[0]['name'], data[0]['name'])
        self.assertEqual(response.data[1]['name'], data[1]['name'])
        self.assertEqual(response.data[2]['name'], data[2]['name'])

    def test_update_consoleserverport(self):

        data = {
            'device': self.device.pk,
            'name': 'Test CS Port X',
        }

        url = reverse('dcim-api:consoleserverport-detail', kwargs={'pk': self.consoleserverport1.pk})
        response = self.client.put(url, data, format='json', **self.header)

        self.assertHttpStatus(response, status.HTTP_200_OK)
        self.assertEqual(ConsoleServerPort.objects.count(), 3)
        consoleserverport1 = ConsoleServerPort.objects.get(pk=response.data['id'])
        self.assertEqual(consoleserverport1.name, data['name'])

    def test_delete_consoleserverport(self):

        url = reverse('dcim-api:consoleserverport-detail', kwargs={'pk': self.consoleserverport1.pk})
        response = self.client.delete(url, **self.header)

        self.assertHttpStatus(response, status.HTTP_204_NO_CONTENT)
        self.assertEqual(ConsoleServerPort.objects.count(), 2)


class PowerPortTest(APITestCase):

    def setUp(self):

        super(PowerPortTest, self).setUp()

        site = Site.objects.create(name='Test Site 1', slug='test-site-1')
        manufacturer = Manufacturer.objects.create(name='Test Manufacturer 1', slug='test-manufacturer-1')
        devicetype = DeviceType.objects.create(
            manufacturer=manufacturer, model='Test Device Type 1', slug='test-device-type-1'
        )
        devicerole = DeviceRole.objects.create(
            name='Test Device Role 1', slug='test-device-role-1', color='ff0000'
        )
        self.device = Device.objects.create(
            device_type=devicetype, device_role=devicerole, name='Test Device 1', site=site
        )
        self.powerport1 = PowerPort.objects.create(device=self.device, name='Test Power Port 1')
        self.powerport2 = PowerPort.objects.create(device=self.device, name='Test Power Port 2')
        self.powerport3 = PowerPort.objects.create(device=self.device, name='Test Power Port 3')

    def test_get_powerport(self):

        url = reverse('dcim-api:powerport-detail', kwargs={'pk': self.powerport1.pk})
        response = self.client.get(url, **self.header)

        self.assertEqual(response.data['name'], self.powerport1.name)

    def test_list_powerports(self):

        url = reverse('dcim-api:powerport-list')
        response = self.client.get(url, **self.header)

        self.assertEqual(response.data['count'], 3)

    def test_list_powerports_brief(self):

        url = reverse('dcim-api:powerport-list')
        response = self.client.get('{}?brief=1'.format(url), **self.header)

        self.assertEqual(
            sorted(response.data['results'][0]),
            ['device', 'id', 'is_connected', 'name', 'url']
        )

    def test_create_powerport(self):

        data = {
            'device': self.device.pk,
            'name': 'Test Power Port 4',
        }

        url = reverse('dcim-api:powerport-list')
        response = self.client.post(url, data, format='json', **self.header)

        self.assertHttpStatus(response, status.HTTP_201_CREATED)
        self.assertEqual(PowerPort.objects.count(), 4)
        powerport4 = PowerPort.objects.get(pk=response.data['id'])
        self.assertEqual(powerport4.device_id, data['device'])
        self.assertEqual(powerport4.name, data['name'])

    def test_create_powerport_bulk(self):

        data = [
            {
                'device': self.device.pk,
                'name': 'Test Power Port 4',
            },
            {
                'device': self.device.pk,
                'name': 'Test Power Port 5',
            },
            {
                'device': self.device.pk,
                'name': 'Test Power Port 6',
            },
        ]

        url = reverse('dcim-api:powerport-list')
        response = self.client.post(url, data, format='json', **self.header)

        self.assertHttpStatus(response, status.HTTP_201_CREATED)
        self.assertEqual(PowerPort.objects.count(), 6)
        self.assertEqual(response.data[0]['name'], data[0]['name'])
        self.assertEqual(response.data[1]['name'], data[1]['name'])
        self.assertEqual(response.data[2]['name'], data[2]['name'])

    def test_update_powerport(self):

        poweroutlet = PowerOutlet.objects.create(device=self.device, name='Test Power Outlet 1')

        data = {
            'device': self.device.pk,
            'name': 'Test Power Port X',
            'power_outlet': poweroutlet.pk,
        }

        url = reverse('dcim-api:powerport-detail', kwargs={'pk': self.powerport1.pk})
        response = self.client.put(url, data, format='json', **self.header)

        self.assertHttpStatus(response, status.HTTP_200_OK)
        self.assertEqual(PowerPort.objects.count(), 3)
        powerport1 = PowerPort.objects.get(pk=response.data['id'])
        self.assertEqual(powerport1.name, data['name'])
        self.assertEqual(powerport1.power_outlet_id, data['power_outlet'])

    def test_delete_powerport(self):

        url = reverse('dcim-api:powerport-detail', kwargs={'pk': self.powerport1.pk})
        response = self.client.delete(url, **self.header)

        self.assertHttpStatus(response, status.HTTP_204_NO_CONTENT)
        self.assertEqual(PowerPort.objects.count(), 2)


class PowerOutletTest(APITestCase):

    def setUp(self):

        super(PowerOutletTest, self).setUp()

        site = Site.objects.create(name='Test Site 1', slug='test-site-1')
        manufacturer = Manufacturer.objects.create(name='Test Manufacturer 1', slug='test-manufacturer-1')
        devicetype = DeviceType.objects.create(
            manufacturer=manufacturer, model='Test Device Type 1', slug='test-device-type-1', is_pdu=True
        )
        devicerole = DeviceRole.objects.create(
            name='Test Device Role 1', slug='test-device-role-1', color='ff0000'
        )
        self.device = Device.objects.create(
            device_type=devicetype, device_role=devicerole, name='Test Device 1', site=site
        )
        self.poweroutlet1 = PowerOutlet.objects.create(device=self.device, name='Test Power Outlet 1')
        self.poweroutlet2 = PowerOutlet.objects.create(device=self.device, name='Test Power Outlet 2')
        self.poweroutlet3 = PowerOutlet.objects.create(device=self.device, name='Test Power Outlet 3')

    def test_get_poweroutlet(self):

        url = reverse('dcim-api:poweroutlet-detail', kwargs={'pk': self.poweroutlet1.pk})
        response = self.client.get(url, **self.header)

        self.assertEqual(response.data['name'], self.poweroutlet1.name)

    def test_list_poweroutlets(self):

        url = reverse('dcim-api:poweroutlet-list')
        response = self.client.get(url, **self.header)

        self.assertEqual(response.data['count'], 3)

    def test_list_poweroutlets_brief(self):

        url = reverse('dcim-api:poweroutlet-list')
        response = self.client.get('{}?brief=1'.format(url), **self.header)

        self.assertEqual(
            sorted(response.data['results'][0]),
            ['device', 'id', 'is_connected', 'name', 'url']
        )

    def test_create_poweroutlet(self):

        data = {
            'device': self.device.pk,
            'name': 'Test Power Outlet 4',
        }

        url = reverse('dcim-api:poweroutlet-list')
        response = self.client.post(url, data, format='json', **self.header)

        self.assertHttpStatus(response, status.HTTP_201_CREATED)
        self.assertEqual(PowerOutlet.objects.count(), 4)
        poweroutlet4 = PowerOutlet.objects.get(pk=response.data['id'])
        self.assertEqual(poweroutlet4.device_id, data['device'])
        self.assertEqual(poweroutlet4.name, data['name'])

    def test_create_poweroutlet_bulk(self):

        data = [
            {
                'device': self.device.pk,
                'name': 'Test Power Outlet 4',
            },
            {
                'device': self.device.pk,
                'name': 'Test Power Outlet 5',
            },
            {
                'device': self.device.pk,
                'name': 'Test Power Outlet 6',
            },
        ]

        url = reverse('dcim-api:poweroutlet-list')
        response = self.client.post(url, data, format='json', **self.header)

        self.assertHttpStatus(response, status.HTTP_201_CREATED)
        self.assertEqual(PowerOutlet.objects.count(), 6)
        self.assertEqual(response.data[0]['name'], data[0]['name'])
        self.assertEqual(response.data[1]['name'], data[1]['name'])
        self.assertEqual(response.data[2]['name'], data[2]['name'])

    def test_update_poweroutlet(self):

        data = {
            'device': self.device.pk,
            'name': 'Test Power Outlet X',
        }

        url = reverse('dcim-api:poweroutlet-detail', kwargs={'pk': self.poweroutlet1.pk})
        response = self.client.put(url, data, format='json', **self.header)

        self.assertHttpStatus(response, status.HTTP_200_OK)
        self.assertEqual(PowerOutlet.objects.count(), 3)
        poweroutlet1 = PowerOutlet.objects.get(pk=response.data['id'])
        self.assertEqual(poweroutlet1.name, data['name'])

    def test_delete_poweroutlet(self):

        url = reverse('dcim-api:poweroutlet-detail', kwargs={'pk': self.poweroutlet1.pk})
        response = self.client.delete(url, **self.header)

        self.assertHttpStatus(response, status.HTTP_204_NO_CONTENT)
        self.assertEqual(PowerOutlet.objects.count(), 2)


class InterfaceTest(APITestCase):

    def setUp(self):

        super(InterfaceTest, self).setUp()

        site = Site.objects.create(name='Test Site 1', slug='test-site-1')
        manufacturer = Manufacturer.objects.create(name='Test Manufacturer 1', slug='test-manufacturer-1')
        devicetype = DeviceType.objects.create(
            manufacturer=manufacturer, model='Test Device Type 1', slug='test-device-type-1', is_network_device=True
        )
        devicerole = DeviceRole.objects.create(
            name='Test Device Role 1', slug='test-device-role-1', color='ff0000'
        )
        self.device = Device.objects.create(
            device_type=devicetype, device_role=devicerole, name='Test Device 1', site=site
        )
        self.interface1 = Interface.objects.create(device=self.device, name='Test Interface 1')
        self.interface2 = Interface.objects.create(device=self.device, name='Test Interface 2')
        self.interface3 = Interface.objects.create(device=self.device, name='Test Interface 3')

        self.vlan1 = VLAN.objects.create(name="Test VLAN 1", vid=1)
        self.vlan2 = VLAN.objects.create(name="Test VLAN 2", vid=2)
        self.vlan3 = VLAN.objects.create(name="Test VLAN 3", vid=3)

    def test_get_interface(self):

        url = reverse('dcim-api:interface-detail', kwargs={'pk': self.interface1.pk})
        response = self.client.get(url, **self.header)

        self.assertEqual(response.data['name'], self.interface1.name)

    def test_get_interface_graphs(self):

        self.graph1 = Graph.objects.create(
            type=GRAPH_TYPE_INTERFACE, name='Test Graph 1',
            source='http://example.com/graphs.py?interface={{ obj.name }}&foo=1'
        )
        self.graph2 = Graph.objects.create(
            type=GRAPH_TYPE_INTERFACE, name='Test Graph 2',
            source='http://example.com/graphs.py?interface={{ obj.name }}&foo=2'
        )
        self.graph3 = Graph.objects.create(
            type=GRAPH_TYPE_INTERFACE, name='Test Graph 3',
            source='http://example.com/graphs.py?interface={{ obj.name }}&foo=3'
        )

        url = reverse('dcim-api:interface-graphs', kwargs={'pk': self.interface1.pk})
        response = self.client.get(url, **self.header)

        self.assertEqual(len(response.data), 3)
        self.assertEqual(response.data[0]['embed_url'], 'http://example.com/graphs.py?interface=Test Interface 1&foo=1')

    def test_list_interfaces(self):

        url = reverse('dcim-api:interface-list')
        response = self.client.get(url, **self.header)

        self.assertEqual(response.data['count'], 3)

    def test_list_interfaces_brief(self):

        url = reverse('dcim-api:interface-list')
        response = self.client.get('{}?brief=1'.format(url), **self.header)

        self.assertEqual(
            sorted(response.data['results'][0]),
            ['device', 'id', 'is_connected', 'name', 'url']
        )

    def test_create_interface(self):

        data = {
            'device': self.device.pk,
            'name': 'Test Interface 4',
        }

        url = reverse('dcim-api:interface-list')
        response = self.client.post(url, data, format='json', **self.header)

        self.assertHttpStatus(response, status.HTTP_201_CREATED)
        self.assertEqual(Interface.objects.count(), 4)
        interface4 = Interface.objects.get(pk=response.data['id'])
        self.assertEqual(interface4.device_id, data['device'])
        self.assertEqual(interface4.name, data['name'])

    def test_create_interface_with_802_1q(self):

        data = {
            'device': self.device.pk,
            'name': 'Test Interface 4',
            'mode': IFACE_MODE_TAGGED,
            'untagged_vlan': self.vlan3.id,
            'tagged_vlans': [self.vlan1.id, self.vlan2.id],
        }

        url = reverse('dcim-api:interface-list')
        response = self.client.post(url, data, format='json', **self.header)

        self.assertHttpStatus(response, status.HTTP_201_CREATED)
        self.assertEqual(Interface.objects.count(), 4)
        self.assertEqual(response.data['device']['id'], data['device'])
        self.assertEqual(response.data['name'], data['name'])
        self.assertEqual(response.data['untagged_vlan']['id'], data['untagged_vlan'])
        self.assertEqual([v['id'] for v in response.data['tagged_vlans']], data['tagged_vlans'])

    def test_create_interface_bulk(self):

        data = [
            {
                'device': self.device.pk,
                'name': 'Test Interface 4',
            },
            {
                'device': self.device.pk,
                'name': 'Test Interface 5',
            },
            {
                'device': self.device.pk,
                'name': 'Test Interface 6',
            },
        ]

        url = reverse('dcim-api:interface-list')
        response = self.client.post(url, data, format='json', **self.header)

        self.assertHttpStatus(response, status.HTTP_201_CREATED)
        self.assertEqual(Interface.objects.count(), 6)
        self.assertEqual(response.data[0]['name'], data[0]['name'])
        self.assertEqual(response.data[1]['name'], data[1]['name'])
        self.assertEqual(response.data[2]['name'], data[2]['name'])

    def test_create_interface_802_1q_bulk(self):

        data = [
            {
                'device': self.device.pk,
                'name': 'Test Interface 4',
                'mode': IFACE_MODE_TAGGED,
                'untagged_vlan': self.vlan2.id,
                'tagged_vlans': [self.vlan1.id],
            },
            {
                'device': self.device.pk,
                'name': 'Test Interface 5',
                'mode': IFACE_MODE_TAGGED,
                'untagged_vlan': self.vlan2.id,
                'tagged_vlans': [self.vlan1.id],
            },
            {
                'device': self.device.pk,
                'name': 'Test Interface 6',
                'mode': IFACE_MODE_TAGGED,
                'untagged_vlan': self.vlan2.id,
                'tagged_vlans': [self.vlan1.id],
            },
        ]

        url = reverse('dcim-api:interface-list')
        response = self.client.post(url, data, format='json', **self.header)

        self.assertHttpStatus(response, status.HTTP_201_CREATED)
        self.assertEqual(Interface.objects.count(), 6)
        for i in range(0, 3):
            self.assertEqual(response.data[i]['name'], data[i]['name'])
            self.assertEqual([v['id'] for v in response.data[i]['tagged_vlans']], data[i]['tagged_vlans'])
            self.assertEqual(response.data[i]['untagged_vlan']['id'], data[i]['untagged_vlan'])

    def test_update_interface(self):

        lag_interface = Interface.objects.create(
            device=self.device, name='Test LAG Interface', form_factor=IFACE_FF_LAG
        )

        data = {
            'device': self.device.pk,
            'name': 'Test Interface X',
            'lag': lag_interface.pk,
        }

        url = reverse('dcim-api:interface-detail', kwargs={'pk': self.interface1.pk})
        response = self.client.put(url, data, format='json', **self.header)

        self.assertHttpStatus(response, status.HTTP_200_OK)
        self.assertEqual(Interface.objects.count(), 4)
        interface1 = Interface.objects.get(pk=response.data['id'])
        self.assertEqual(interface1.name, data['name'])
        self.assertEqual(interface1.lag_id, data['lag'])

    def test_delete_interface(self):

        url = reverse('dcim-api:interface-detail', kwargs={'pk': self.interface1.pk})
        response = self.client.delete(url, **self.header)

        self.assertHttpStatus(response, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Interface.objects.count(), 2)


class DeviceBayTest(APITestCase):

    def setUp(self):

        super(DeviceBayTest, self).setUp()

        site = Site.objects.create(name='Test Site 1', slug='test-site-1')
        manufacturer = Manufacturer.objects.create(name='Test Manufacturer 1', slug='test-manufacturer-1')
        self.devicetype1 = DeviceType.objects.create(
            manufacturer=manufacturer, model='Parent Device Type', slug='parent-device-type',
            subdevice_role=SUBDEVICE_ROLE_PARENT
        )
        self.devicetype2 = DeviceType.objects.create(
            manufacturer=manufacturer, model='Child Device Type', slug='child-device-type',
            subdevice_role=SUBDEVICE_ROLE_CHILD
        )
        devicerole = DeviceRole.objects.create(
            name='Test Device Role 1', slug='test-device-role-1', color='ff0000'
        )
        self.parent_device = Device.objects.create(
            device_type=self.devicetype1, device_role=devicerole, name='Parent Device 1', site=site
        )
        self.child_device = Device.objects.create(
            device_type=self.devicetype2, device_role=devicerole, name='Child Device 1', site=site
        )
        self.devicebay1 = DeviceBay.objects.create(device=self.parent_device, name='Test Device Bay 1')
        self.devicebay2 = DeviceBay.objects.create(device=self.parent_device, name='Test Device Bay 2')
        self.devicebay3 = DeviceBay.objects.create(device=self.parent_device, name='Test Device Bay 3')

    def test_get_devicebay(self):

        url = reverse('dcim-api:devicebay-detail', kwargs={'pk': self.devicebay1.pk})
        response = self.client.get(url, **self.header)

        self.assertEqual(response.data['name'], self.devicebay1.name)

    def test_list_devicebays(self):

        url = reverse('dcim-api:devicebay-list')
        response = self.client.get(url, **self.header)

        self.assertEqual(response.data['count'], 3)

    def test_list_devicebays_brief(self):

        url = reverse('dcim-api:devicebay-list')
        response = self.client.get('{}?brief=1'.format(url), **self.header)

        self.assertEqual(
            sorted(response.data['results'][0]),
            ['device', 'id', 'name', 'url']
        )

    def test_create_devicebay(self):

        data = {
            'device': self.parent_device.pk,
            'name': 'Test Device Bay 4',
            'installed_device': self.child_device.pk,
        }

        url = reverse('dcim-api:devicebay-list')
        response = self.client.post(url, data, format='json', **self.header)

        self.assertHttpStatus(response, status.HTTP_201_CREATED)
        self.assertEqual(DeviceBay.objects.count(), 4)
        devicebay4 = DeviceBay.objects.get(pk=response.data['id'])
        self.assertEqual(devicebay4.device_id, data['device'])
        self.assertEqual(devicebay4.name, data['name'])
        self.assertEqual(devicebay4.installed_device_id, data['installed_device'])

    def test_create_devicebay_bulk(self):

        data = [
            {
                'device': self.parent_device.pk,
                'name': 'Test Device Bay 4',
            },
            {
                'device': self.parent_device.pk,
                'name': 'Test Device Bay 5',
            },
            {
                'device': self.parent_device.pk,
                'name': 'Test Device Bay 6',
            },
        ]

        url = reverse('dcim-api:devicebay-list')
        response = self.client.post(url, data, format='json', **self.header)

        self.assertHttpStatus(response, status.HTTP_201_CREATED)
        self.assertEqual(DeviceBay.objects.count(), 6)
        self.assertEqual(response.data[0]['name'], data[0]['name'])
        self.assertEqual(response.data[1]['name'], data[1]['name'])
        self.assertEqual(response.data[2]['name'], data[2]['name'])

    def test_update_devicebay(self):

        data = {
            'device': self.parent_device.pk,
            'name': 'Test Device Bay X',
            'installed_device': self.child_device.pk,
        }

        url = reverse('dcim-api:devicebay-detail', kwargs={'pk': self.devicebay1.pk})
        response = self.client.put(url, data, format='json', **self.header)

        self.assertHttpStatus(response, status.HTTP_200_OK)
        self.assertEqual(DeviceBay.objects.count(), 3)
        devicebay1 = DeviceBay.objects.get(pk=response.data['id'])
        self.assertEqual(devicebay1.name, data['name'])
        self.assertEqual(devicebay1.installed_device_id, data['installed_device'])

    def test_delete_devicebay(self):

        url = reverse('dcim-api:devicebay-detail', kwargs={'pk': self.devicebay1.pk})
        response = self.client.delete(url, **self.header)

        self.assertHttpStatus(response, status.HTTP_204_NO_CONTENT)
        self.assertEqual(DeviceBay.objects.count(), 2)


class InventoryItemTest(APITestCase):

    def setUp(self):

        super(InventoryItemTest, self).setUp()

        site = Site.objects.create(name='Test Site 1', slug='test-site-1')
        self.manufacturer = Manufacturer.objects.create(name='Test Manufacturer 1', slug='test-manufacturer-1')
        devicetype = DeviceType.objects.create(
            manufacturer=self.manufacturer, model='Test Device Type 1', slug='test-device-type-1'
        )
        devicerole = DeviceRole.objects.create(
            name='Test Device Role 1', slug='test-device-role-1', color='ff0000'
        )
        self.device = Device.objects.create(
            device_type=devicetype, device_role=devicerole, name='Test Device 1', site=site
        )
        self.inventoryitem1 = InventoryItem.objects.create(device=self.device, name='Test Inventory Item 1')
        self.inventoryitem2 = InventoryItem.objects.create(device=self.device, name='Test Inventory Item 2')
        self.inventoryitem3 = InventoryItem.objects.create(device=self.device, name='Test Inventory Item 3')

    def test_get_inventoryitem(self):

        url = reverse('dcim-api:inventoryitem-detail', kwargs={'pk': self.inventoryitem1.pk})
        response = self.client.get(url, **self.header)

        self.assertEqual(response.data['name'], self.inventoryitem1.name)

    def test_list_inventoryitems(self):

        url = reverse('dcim-api:inventoryitem-list')
        response = self.client.get(url, **self.header)

        self.assertEqual(response.data['count'], 3)

    def test_create_inventoryitem(self):

        data = {
            'device': self.device.pk,
            'parent': self.inventoryitem1.pk,
            'name': 'Test Inventory Item 4',
            'manufacturer': self.manufacturer.pk,
        }

        url = reverse('dcim-api:inventoryitem-list')
        response = self.client.post(url, data, format='json', **self.header)

        self.assertHttpStatus(response, status.HTTP_201_CREATED)
        self.assertEqual(InventoryItem.objects.count(), 4)
        inventoryitem4 = InventoryItem.objects.get(pk=response.data['id'])
        self.assertEqual(inventoryitem4.device_id, data['device'])
        self.assertEqual(inventoryitem4.parent_id, data['parent'])
        self.assertEqual(inventoryitem4.name, data['name'])
        self.assertEqual(inventoryitem4.manufacturer_id, data['manufacturer'])

    def test_create_inventoryitem_bulk(self):

        data = [
            {
                'device': self.device.pk,
                'parent': self.inventoryitem1.pk,
                'name': 'Test Inventory Item 4',
                'manufacturer': self.manufacturer.pk,
            },
            {
                'device': self.device.pk,
                'parent': self.inventoryitem1.pk,
                'name': 'Test Inventory Item 5',
                'manufacturer': self.manufacturer.pk,
            },
            {
                'device': self.device.pk,
                'parent': self.inventoryitem1.pk,
                'name': 'Test Inventory Item 6',
                'manufacturer': self.manufacturer.pk,
            },
        ]

        url = reverse('dcim-api:inventoryitem-list')
        response = self.client.post(url, data, format='json', **self.header)

        self.assertHttpStatus(response, status.HTTP_201_CREATED)
        self.assertEqual(InventoryItem.objects.count(), 6)
        self.assertEqual(response.data[0]['name'], data[0]['name'])
        self.assertEqual(response.data[1]['name'], data[1]['name'])
        self.assertEqual(response.data[2]['name'], data[2]['name'])

    def test_update_inventoryitem(self):

        data = {
            'device': self.device.pk,
            'parent': self.inventoryitem1.pk,
            'name': 'Test Inventory Item X',
            'manufacturer': self.manufacturer.pk,
        }

        url = reverse('dcim-api:inventoryitem-detail', kwargs={'pk': self.inventoryitem1.pk})
        response = self.client.put(url, data, format='json', **self.header)

        self.assertHttpStatus(response, status.HTTP_200_OK)
        self.assertEqual(InventoryItem.objects.count(), 3)
        inventoryitem1 = InventoryItem.objects.get(pk=response.data['id'])
        self.assertEqual(inventoryitem1.device_id, data['device'])
        self.assertEqual(inventoryitem1.parent_id, data['parent'])
        self.assertEqual(inventoryitem1.name, data['name'])
        self.assertEqual(inventoryitem1.manufacturer_id, data['manufacturer'])

    def test_delete_inventoryitem(self):

        url = reverse('dcim-api:inventoryitem-detail', kwargs={'pk': self.inventoryitem1.pk})
        response = self.client.delete(url, **self.header)

        self.assertHttpStatus(response, status.HTTP_204_NO_CONTENT)
        self.assertEqual(InventoryItem.objects.count(), 2)


class ConsoleConnectionTest(APITestCase):

    def setUp(self):

        super(ConsoleConnectionTest, self).setUp()

        site = Site.objects.create(name='Test Site 1', slug='test-site-1')
        manufacturer = Manufacturer.objects.create(name='Test Manufacturer 1', slug='test-manufacturer-1')
        devicetype = DeviceType.objects.create(
            manufacturer=manufacturer, model='Test Device Type 1', slug='test-device-type-1'
        )
        devicerole = DeviceRole.objects.create(
            name='Test Device Role 1', slug='test-device-role-1', color='ff0000'
        )
        device1 = Device.objects.create(
            device_type=devicetype, device_role=devicerole, name='Test Device 1', site=site
        )
        device2 = Device.objects.create(
            device_type=devicetype, device_role=devicerole, name='Test Device 2', site=site
        )
        cs_port1 = ConsoleServerPort.objects.create(device=device1, name='Test CS Port 1')
        cs_port2 = ConsoleServerPort.objects.create(device=device1, name='Test CS Port 2')
        cs_port3 = ConsoleServerPort.objects.create(device=device1, name='Test CS Port 3')
        ConsolePort.objects.create(
            device=device2, cs_port=cs_port1, name='Test Console Port 1', connection_status=True
        )
        ConsolePort.objects.create(
            device=device2, cs_port=cs_port2, name='Test Console Port 2', connection_status=True
        )
        ConsolePort.objects.create(
            device=device2, cs_port=cs_port3, name='Test Console Port 3', connection_status=True
        )

    def test_list_consoleconnections(self):

        url = reverse('dcim-api:consoleconnections-list')
        response = self.client.get(url, **self.header)

        self.assertEqual(response.data['count'], 3)


class PowerConnectionTest(APITestCase):

    def setUp(self):

        super(PowerConnectionTest, self).setUp()

        site = Site.objects.create(name='Test Site 1', slug='test-site-1')
        manufacturer = Manufacturer.objects.create(name='Test Manufacturer 1', slug='test-manufacturer-1')
        devicetype = DeviceType.objects.create(
            manufacturer=manufacturer, model='Test Device Type 1', slug='test-device-type-1'
        )
        devicerole = DeviceRole.objects.create(
            name='Test Device Role 1', slug='test-device-role-1', color='ff0000'
        )
        device1 = Device.objects.create(
            device_type=devicetype, device_role=devicerole, name='Test Device 1', site=site
        )
        device2 = Device.objects.create(
            device_type=devicetype, device_role=devicerole, name='Test Device 2', site=site
        )
        power_outlet1 = PowerOutlet.objects.create(device=device1, name='Test Power Outlet 1')
        power_outlet2 = PowerOutlet.objects.create(device=device1, name='Test Power Outlet 2')
        power_outlet3 = PowerOutlet.objects.create(device=device1, name='Test Power Outlet 3')
        PowerPort.objects.create(
            device=device2, power_outlet=power_outlet1, name='Test Power Port 1', connection_status=True
        )
        PowerPort.objects.create(
            device=device2, power_outlet=power_outlet2, name='Test Power Port 2', connection_status=True
        )
        PowerPort.objects.create(
            device=device2, power_outlet=power_outlet3, name='Test Power Port 3', connection_status=True
        )

    def test_list_powerconnections(self):

        url = reverse('dcim-api:powerconnections-list')
        response = self.client.get(url, **self.header)

        self.assertEqual(response.data['count'], 3)


class InterfaceConnectionTest(APITestCase):

    def setUp(self):

        super(InterfaceConnectionTest, self).setUp()

        site = Site.objects.create(name='Test Site 1', slug='test-site-1')
        manufacturer = Manufacturer.objects.create(name='Test Manufacturer 1', slug='test-manufacturer-1')
        devicetype = DeviceType.objects.create(
            manufacturer=manufacturer, model='Test Device Type 1', slug='test-device-type-1'
        )
        devicerole = DeviceRole.objects.create(
            name='Test Device Role 1', slug='test-device-role-1', color='ff0000'
        )
        self.device = Device.objects.create(
            device_type=devicetype, device_role=devicerole, name='Test Device 1', site=site
        )
        self.interface1 = Interface.objects.create(device=self.device, name='Test Interface 1')
        self.interface2 = Interface.objects.create(device=self.device, name='Test Interface 2')
        self.interface3 = Interface.objects.create(device=self.device, name='Test Interface 3')
        self.interface4 = Interface.objects.create(device=self.device, name='Test Interface 4')
        self.interface5 = Interface.objects.create(device=self.device, name='Test Interface 5')
        self.interface6 = Interface.objects.create(device=self.device, name='Test Interface 6')
        self.interface7 = Interface.objects.create(device=self.device, name='Test Interface 7')
        self.interface8 = Interface.objects.create(device=self.device, name='Test Interface 8')
        self.interface9 = Interface.objects.create(device=self.device, name='Test Interface 9')
        self.interface10 = Interface.objects.create(device=self.device, name='Test Interface 10')
        self.interface11 = Interface.objects.create(device=self.device, name='Test Interface 11')
        self.interface12 = Interface.objects.create(device=self.device, name='Test Interface 12')
        self.interfaceconnection1 = InterfaceConnection.objects.create(
            interface_a=self.interface1, interface_b=self.interface2
        )
        self.interfaceconnection2 = InterfaceConnection.objects.create(
            interface_a=self.interface3, interface_b=self.interface4
        )
        self.interfaceconnection3 = InterfaceConnection.objects.create(
            interface_a=self.interface5, interface_b=self.interface6
        )

    def test_get_interfaceconnection(self):

        url = reverse('dcim-api:interfaceconnection-detail', kwargs={'pk': self.interfaceconnection1.pk})
        response = self.client.get(url, **self.header)

        self.assertEqual(response.data['interface_a']['id'], self.interfaceconnection1.interface_a_id)
        self.assertEqual(response.data['interface_b']['id'], self.interfaceconnection1.interface_b_id)

    def test_list_interfaceconnections(self):

        url = reverse('dcim-api:interfaceconnection-list')
        response = self.client.get(url, **self.header)

        self.assertEqual(response.data['count'], 3)

    def test_list_interfaceconnections_brief(self):

        url = reverse('dcim-api:interfaceconnection-list')
        response = self.client.get('{}?brief=1'.format(url), **self.header)

        self.assertEqual(
            sorted(response.data['results'][0]),
            ['connection_status', 'id', 'url']
        )

    def test_create_interfaceconnection(self):

        data = {
            'interface_a': self.interface7.pk,
            'interface_b': self.interface8.pk,
        }

        url = reverse('dcim-api:interfaceconnection-list')
        response = self.client.post(url, data, format='json', **self.header)

        self.assertHttpStatus(response, status.HTTP_201_CREATED)
        self.assertEqual(InterfaceConnection.objects.count(), 4)
        interfaceconnection4 = InterfaceConnection.objects.get(pk=response.data['id'])
        self.assertEqual(interfaceconnection4.interface_a_id, data['interface_a'])
        self.assertEqual(interfaceconnection4.interface_b_id, data['interface_b'])

    def test_create_interfaceconnection_bulk(self):

        data = [
            {
                'interface_a': self.interface7.pk,
                'interface_b': self.interface8.pk,
            },
            {
                'interface_a': self.interface9.pk,
                'interface_b': self.interface10.pk,
            },
            {
                'interface_a': self.interface11.pk,
                'interface_b': self.interface12.pk,
            },
        ]

        url = reverse('dcim-api:interfaceconnection-list')
        response = self.client.post(url, data, format='json', **self.header)

        self.assertHttpStatus(response, status.HTTP_201_CREATED)
        self.assertEqual(InterfaceConnection.objects.count(), 6)
        for i in range(0, 3):
            self.assertEqual(response.data[i]['interface_a']['id'], data[i]['interface_a'])
            self.assertEqual(response.data[i]['interface_b']['id'], data[i]['interface_b'])

    def test_update_interfaceconnection(self):

        new_connection_status = not self.interfaceconnection1.connection_status

        data = {
            'interface_a': self.interface7.pk,
            'interface_b': self.interface8.pk,
            'connection_status': new_connection_status,
        }

        url = reverse('dcim-api:interfaceconnection-detail', kwargs={'pk': self.interfaceconnection1.pk})
        response = self.client.put(url, data, format='json', **self.header)

        self.assertHttpStatus(response, status.HTTP_200_OK)
        self.assertEqual(InterfaceConnection.objects.count(), 3)
        interfaceconnection1 = InterfaceConnection.objects.get(pk=response.data['id'])
        self.assertEqual(interfaceconnection1.interface_a_id, data['interface_a'])
        self.assertEqual(interfaceconnection1.interface_b_id, data['interface_b'])
        self.assertEqual(interfaceconnection1.connection_status, data['connection_status'])

    def test_delete_interfaceconnection(self):

        url = reverse('dcim-api:interfaceconnection-detail', kwargs={'pk': self.interfaceconnection1.pk})
        response = self.client.delete(url, **self.header)

        self.assertHttpStatus(response, status.HTTP_204_NO_CONTENT)
        self.assertEqual(InterfaceConnection.objects.count(), 2)


class ConnectedDeviceTest(APITestCase):

    def setUp(self):

        super(ConnectedDeviceTest, self).setUp()

        self.site1 = Site.objects.create(name='Test Site 1', slug='test-site-1')
        self.site2 = Site.objects.create(name='Test Site 2', slug='test-site-2')
        manufacturer = Manufacturer.objects.create(name='Test Manufacturer 1', slug='test-manufacturer-1')
        self.devicetype1 = DeviceType.objects.create(
            manufacturer=manufacturer, model='Test Device Type 1', slug='test-device-type-1'
        )
        self.devicetype2 = DeviceType.objects.create(
            manufacturer=manufacturer, model='Test Device Type 2', slug='test-device-type-2'
        )
        self.devicerole1 = DeviceRole.objects.create(
            name='Test Device Role 1', slug='test-device-role-1', color='ff0000'
        )
        self.devicerole2 = DeviceRole.objects.create(
            name='Test Device Role 2', slug='test-device-role-2', color='00ff00'
        )
        self.device1 = Device.objects.create(
            device_type=self.devicetype1, device_role=self.devicerole1, name='TestDevice1', site=self.site1
        )
        self.device2 = Device.objects.create(
            device_type=self.devicetype1, device_role=self.devicerole1, name='TestDevice2', site=self.site1
        )
        self.interface1 = Interface.objects.create(device=self.device1, name='eth0')
        self.interface2 = Interface.objects.create(device=self.device2, name='eth0')
        InterfaceConnection.objects.create(interface_a=self.interface1, interface_b=self.interface2)

    def test_get_connected_device(self):

        url = reverse('dcim-api:connected-device-list')
        response = self.client.get(url + '?peer-device=TestDevice2&peer-interface=eth0', **self.header)

        self.assertHttpStatus(response, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], self.device1.name)


class VirtualChassisTest(APITestCase):

    def setUp(self):

        super(VirtualChassisTest, self).setUp()

        site = Site.objects.create(name='Test Site', slug='test-site')
        manufacturer = Manufacturer.objects.create(name='Test Manufacturer', slug='test-manufacturer')
        device_type = DeviceType.objects.create(
            manufacturer=manufacturer, model='Test Device Type', slug='test-device-type'
        )
        device_role = DeviceRole.objects.create(
            name='Test Device Role', slug='test-device-role', color='ff0000'
        )

        # Create 9 member Devices with 12 interfaces each
        self.device1 = Device.objects.create(
            device_type=device_type, device_role=device_role, name='StackSwitch1', site=site
        )
        self.device2 = Device.objects.create(
            device_type=device_type, device_role=device_role, name='StackSwitch2', site=site
        )
        self.device3 = Device.objects.create(
            device_type=device_type, device_role=device_role, name='StackSwitch3', site=site
        )
        self.device4 = Device.objects.create(
            device_type=device_type, device_role=device_role, name='StackSwitch4', site=site
        )
        self.device5 = Device.objects.create(
            device_type=device_type, device_role=device_role, name='StackSwitch5', site=site
        )
        self.device6 = Device.objects.create(
            device_type=device_type, device_role=device_role, name='StackSwitch6', site=site
        )
        self.device7 = Device.objects.create(
            device_type=device_type, device_role=device_role, name='StackSwitch7', site=site
        )
        self.device8 = Device.objects.create(
            device_type=device_type, device_role=device_role, name='StackSwitch8', site=site
        )
        self.device9 = Device.objects.create(
            device_type=device_type, device_role=device_role, name='StackSwitch9', site=site
        )
        for i in range(0, 13):
            Interface.objects.create(device=self.device1, name='1/{}'.format(i), form_factor=IFACE_FF_1GE_FIXED)
        for i in range(0, 13):
            Interface.objects.create(device=self.device2, name='2/{}'.format(i), form_factor=IFACE_FF_1GE_FIXED)
        for i in range(0, 13):
            Interface.objects.create(device=self.device3, name='3/{}'.format(i), form_factor=IFACE_FF_1GE_FIXED)
        for i in range(0, 13):
            Interface.objects.create(device=self.device4, name='1/{}'.format(i), form_factor=IFACE_FF_1GE_FIXED)
        for i in range(0, 13):
            Interface.objects.create(device=self.device5, name='2/{}'.format(i), form_factor=IFACE_FF_1GE_FIXED)
        for i in range(0, 13):
            Interface.objects.create(device=self.device6, name='3/{}'.format(i), form_factor=IFACE_FF_1GE_FIXED)
        for i in range(0, 13):
            Interface.objects.create(device=self.device7, name='1/{}'.format(i), form_factor=IFACE_FF_1GE_FIXED)
        for i in range(0, 13):
            Interface.objects.create(device=self.device8, name='2/{}'.format(i), form_factor=IFACE_FF_1GE_FIXED)
        for i in range(0, 13):
            Interface.objects.create(device=self.device9, name='3/{}'.format(i), form_factor=IFACE_FF_1GE_FIXED)

        # Create two VirtualChassis with three members each
        self.vc1 = VirtualChassis.objects.create(master=self.device1, domain='test-domain-1')
        Device.objects.filter(pk=self.device2.pk).update(virtual_chassis=self.vc1, vc_position=2)
        Device.objects.filter(pk=self.device3.pk).update(virtual_chassis=self.vc1, vc_position=3)
        self.vc2 = VirtualChassis.objects.create(master=self.device4, domain='test-domain-2')
        Device.objects.filter(pk=self.device5.pk).update(virtual_chassis=self.vc2, vc_position=2)
        Device.objects.filter(pk=self.device6.pk).update(virtual_chassis=self.vc2, vc_position=3)

    def test_get_virtualchassis(self):

        url = reverse('dcim-api:virtualchassis-detail', kwargs={'pk': self.vc1.pk})
        response = self.client.get(url, **self.header)

        self.assertEqual(response.data['domain'], self.vc1.domain)

    def test_list_virtualchassis(self):

        url = reverse('dcim-api:virtualchassis-list')
        response = self.client.get(url, **self.header)

        self.assertEqual(response.data['count'], 2)

    def test_list_virtualchassis_brief(self):

        url = reverse('dcim-api:virtualchassis-list')
        response = self.client.get('{}?brief=1'.format(url), **self.header)

        self.assertEqual(
            sorted(response.data['results'][0]),
            ['id', 'url']
        )

    def test_create_virtualchassis(self):

        data = {
            'master': self.device7.pk,
            'domain': 'test-domain-3',
        }

        url = reverse('dcim-api:virtualchassis-list')
        response = self.client.post(url, data, format='json', **self.header)
        self.assertHttpStatus(response, status.HTTP_201_CREATED)
        self.assertEqual(VirtualChassis.objects.count(), 3)
        vc3 = VirtualChassis.objects.get(pk=response.data['id'])
        self.assertEqual(vc3.master.pk, data['master'])
        self.assertEqual(vc3.domain, data['domain'])

        # Verify that the master device was automatically assigned to the VC
        self.assertTrue(Device.objects.filter(pk=vc3.master.pk, virtual_chassis=vc3.pk).exists())

    def test_create_virtualchassis_bulk(self):

        data = [
            {
                'master': self.device7.pk,
                'domain': 'test-domain-3',
            },
            {
                'master': self.device8.pk,
                'domain': 'test-domain-4',
            },
            {
                'master': self.device9.pk,
                'domain': 'test-domain-5',
            },
        ]

        url = reverse('dcim-api:virtualchassis-list')
        response = self.client.post(url, data, format='json', **self.header)
        self.assertHttpStatus(response, status.HTTP_201_CREATED)
        self.assertEqual(VirtualChassis.objects.count(), 5)
        for i in range(0, 3):
            self.assertEqual(response.data[i]['master']['id'], data[i]['master'])
            self.assertEqual(response.data[i]['domain'], data[i]['domain'])

    def test_update_virtualchassis(self):

        data = {
            'master': self.device2.pk,
            'domain': 'test-domain-x',
        }

        url = reverse('dcim-api:virtualchassis-detail', kwargs={'pk': self.vc1.pk})
        response = self.client.put(url, data, format='json', **self.header)

        self.assertHttpStatus(response, status.HTTP_200_OK)
        self.assertEqual(VirtualChassis.objects.count(), 2)
        vc1 = VirtualChassis.objects.get(pk=response.data['id'])
        self.assertEqual(vc1.master.pk, data['master'])
        self.assertEqual(vc1.domain, data['domain'])

    def test_delete_virtualchassis(self):

        url = reverse('dcim-api:virtualchassis-detail', kwargs={'pk': self.vc1.pk})
        response = self.client.delete(url, **self.header)

        self.assertHttpStatus(response, status.HTTP_204_NO_CONTENT)
        self.assertEqual(VirtualChassis.objects.count(), 1)

        # Verify that all VC members have had their VC-related fields nullified
        for d in [self.device1, self.device2, self.device3]:
            self.assertTrue(
                Device.objects.filter(pk=d.pk, virtual_chassis=None, vc_position=None, vc_priority=None)
            )
