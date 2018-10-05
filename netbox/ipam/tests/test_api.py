from __future__ import unicode_literals

from django.urls import reverse
from netaddr import IPNetwork
from rest_framework import status

from dcim.models import Device, DeviceRole, DeviceType, Manufacturer, Site
from ipam.constants import IP_PROTOCOL_TCP, IP_PROTOCOL_UDP
from ipam.models import Aggregate, IPAddress, Prefix, RIR, Role, Service, VLAN, VLANGroup, VRF
from utilities.testing import APITestCase


class VRFTest(APITestCase):

    def setUp(self):

        super(VRFTest, self).setUp()

        self.vrf1 = VRF.objects.create(name='Test VRF 1', rd='65000:1')
        self.vrf2 = VRF.objects.create(name='Test VRF 2', rd='65000:2')
        self.vrf3 = VRF.objects.create(name='Test VRF 3', rd='65000:3')

    def test_get_vrf(self):

        url = reverse('ipam-api:vrf-detail', kwargs={'pk': self.vrf1.pk})
        response = self.client.get(url, **self.header)

        self.assertEqual(response.data['name'], self.vrf1.name)

    def test_list_vrfs(self):

        url = reverse('ipam-api:vrf-list')
        response = self.client.get(url, **self.header)

        self.assertEqual(response.data['count'], 3)

    def test_list_vrfs_brief(self):

        url = reverse('ipam-api:vrf-list')
        response = self.client.get('{}?brief=1'.format(url), **self.header)

        self.assertEqual(
            sorted(response.data['results'][0]),
            ['id', 'name', 'rd', 'url']
        )

    def test_create_vrf(self):

        data = {
            'name': 'Test VRF 4',
            'rd': '65000:4',
        }

        url = reverse('ipam-api:vrf-list')
        response = self.client.post(url, data, format='json', **self.header)

        self.assertHttpStatus(response, status.HTTP_201_CREATED)
        self.assertEqual(VRF.objects.count(), 4)
        vrf4 = VRF.objects.get(pk=response.data['id'])
        self.assertEqual(vrf4.name, data['name'])
        self.assertEqual(vrf4.rd, data['rd'])

    def test_create_vrf_bulk(self):

        data = [
            {
                'name': 'Test VRF 4',
                'rd': '65000:4',
            },
            {
                'name': 'Test VRF 5',
                'rd': '65000:5',
            },
            {
                'name': 'Test VRF 6',
                'rd': '65000:6',
            },
        ]

        url = reverse('ipam-api:vrf-list')
        response = self.client.post(url, data, format='json', **self.header)

        self.assertHttpStatus(response, status.HTTP_201_CREATED)
        self.assertEqual(VRF.objects.count(), 6)
        self.assertEqual(response.data[0]['name'], data[0]['name'])
        self.assertEqual(response.data[1]['name'], data[1]['name'])
        self.assertEqual(response.data[2]['name'], data[2]['name'])

    def test_update_vrf(self):

        data = {
            'name': 'Test VRF X',
            'rd': '65000:99',
        }

        url = reverse('ipam-api:vrf-detail', kwargs={'pk': self.vrf1.pk})
        response = self.client.put(url, data, format='json', **self.header)

        self.assertHttpStatus(response, status.HTTP_200_OK)
        self.assertEqual(VRF.objects.count(), 3)
        vrf1 = VRF.objects.get(pk=response.data['id'])
        self.assertEqual(vrf1.name, data['name'])
        self.assertEqual(vrf1.rd, data['rd'])

    def test_delete_vrf(self):

        url = reverse('ipam-api:vrf-detail', kwargs={'pk': self.vrf1.pk})
        response = self.client.delete(url, **self.header)

        self.assertHttpStatus(response, status.HTTP_204_NO_CONTENT)
        self.assertEqual(VRF.objects.count(), 2)


class RIRTest(APITestCase):

    def setUp(self):

        super(RIRTest, self).setUp()

        self.rir1 = RIR.objects.create(name='Test RIR 1', slug='test-rir-1')
        self.rir2 = RIR.objects.create(name='Test RIR 2', slug='test-rir-2')
        self.rir3 = RIR.objects.create(name='Test RIR 3', slug='test-rir-3')

    def test_get_rir(self):

        url = reverse('ipam-api:rir-detail', kwargs={'pk': self.rir1.pk})
        response = self.client.get(url, **self.header)

        self.assertEqual(response.data['name'], self.rir1.name)

    def test_list_rirs(self):

        url = reverse('ipam-api:rir-list')
        response = self.client.get(url, **self.header)

        self.assertEqual(response.data['count'], 3)

    def test_list_rirs_brief(self):

        url = reverse('ipam-api:rir-list')
        response = self.client.get('{}?brief=1'.format(url), **self.header)

        self.assertEqual(
            sorted(response.data['results'][0]),
            ['id', 'name', 'slug', 'url']
        )

    def test_create_rir(self):

        data = {
            'name': 'Test RIR 4',
            'slug': 'test-rir-4',
        }

        url = reverse('ipam-api:rir-list')
        response = self.client.post(url, data, format='json', **self.header)

        self.assertHttpStatus(response, status.HTTP_201_CREATED)
        self.assertEqual(RIR.objects.count(), 4)
        rir4 = RIR.objects.get(pk=response.data['id'])
        self.assertEqual(rir4.name, data['name'])
        self.assertEqual(rir4.slug, data['slug'])

    def test_create_rir_bulk(self):

        data = [
            {
                'name': 'Test RIR 4',
                'slug': 'test-rir-4',
            },
            {
                'name': 'Test RIR 5',
                'slug': 'test-rir-5',
            },
            {
                'name': 'Test RIR 6',
                'slug': 'test-rir-6',
            },
        ]

        url = reverse('ipam-api:rir-list')
        response = self.client.post(url, data, format='json', **self.header)

        self.assertHttpStatus(response, status.HTTP_201_CREATED)
        self.assertEqual(RIR.objects.count(), 6)
        self.assertEqual(response.data[0]['name'], data[0]['name'])
        self.assertEqual(response.data[1]['name'], data[1]['name'])
        self.assertEqual(response.data[2]['name'], data[2]['name'])

    def test_update_rir(self):

        data = {
            'name': 'Test RIR X',
            'slug': 'test-rir-x',
        }

        url = reverse('ipam-api:rir-detail', kwargs={'pk': self.rir1.pk})
        response = self.client.put(url, data, format='json', **self.header)

        self.assertHttpStatus(response, status.HTTP_200_OK)
        self.assertEqual(RIR.objects.count(), 3)
        rir1 = RIR.objects.get(pk=response.data['id'])
        self.assertEqual(rir1.name, data['name'])
        self.assertEqual(rir1.slug, data['slug'])

    def test_delete_rir(self):

        url = reverse('ipam-api:rir-detail', kwargs={'pk': self.rir1.pk})
        response = self.client.delete(url, **self.header)

        self.assertHttpStatus(response, status.HTTP_204_NO_CONTENT)
        self.assertEqual(RIR.objects.count(), 2)


class AggregateTest(APITestCase):

    def setUp(self):

        super(AggregateTest, self).setUp()

        self.rir1 = RIR.objects.create(name='Test RIR 1', slug='test-rir-1')
        self.rir2 = RIR.objects.create(name='Test RIR 2', slug='test-rir-2')
        self.aggregate1 = Aggregate.objects.create(prefix=IPNetwork('10.0.0.0/8'), rir=self.rir1)
        self.aggregate2 = Aggregate.objects.create(prefix=IPNetwork('172.16.0.0/12'), rir=self.rir1)
        self.aggregate3 = Aggregate.objects.create(prefix=IPNetwork('192.168.0.0/16'), rir=self.rir1)

    def test_get_aggregate(self):

        url = reverse('ipam-api:aggregate-detail', kwargs={'pk': self.aggregate1.pk})
        response = self.client.get(url, **self.header)

        self.assertEqual(response.data['prefix'], str(self.aggregate1.prefix))

    def test_list_aggregates(self):

        url = reverse('ipam-api:aggregate-list')
        response = self.client.get(url, **self.header)

        self.assertEqual(response.data['count'], 3)

    def test_list_aggregates_brief(self):

        url = reverse('ipam-api:aggregate-list')
        response = self.client.get('{}?brief=1'.format(url), **self.header)

        self.assertEqual(
            sorted(response.data['results'][0]),
            ['family', 'id', 'prefix', 'url']
        )

    def test_create_aggregate(self):

        data = {
            'prefix': '192.0.2.0/24',
            'rir': self.rir1.pk,
        }

        url = reverse('ipam-api:aggregate-list')
        response = self.client.post(url, data, format='json', **self.header)

        self.assertHttpStatus(response, status.HTTP_201_CREATED)
        self.assertEqual(Aggregate.objects.count(), 4)
        aggregate4 = Aggregate.objects.get(pk=response.data['id'])
        self.assertEqual(str(aggregate4.prefix), data['prefix'])
        self.assertEqual(aggregate4.rir_id, data['rir'])

    def test_create_aggregate_bulk(self):

        data = [
            {
                'prefix': '100.0.0.0/8',
                'rir': self.rir1.pk,
            },
            {
                'prefix': '101.0.0.0/8',
                'rir': self.rir1.pk,
            },
            {
                'prefix': '102.0.0.0/8',
                'rir': self.rir1.pk,
            },
        ]

        url = reverse('ipam-api:aggregate-list')
        response = self.client.post(url, data, format='json', **self.header)

        self.assertHttpStatus(response, status.HTTP_201_CREATED)
        self.assertEqual(Aggregate.objects.count(), 6)
        self.assertEqual(response.data[0]['prefix'], data[0]['prefix'])
        self.assertEqual(response.data[1]['prefix'], data[1]['prefix'])
        self.assertEqual(response.data[2]['prefix'], data[2]['prefix'])

    def test_update_aggregate(self):

        data = {
            'prefix': '11.0.0.0/8',
            'rir': self.rir2.pk,
        }

        url = reverse('ipam-api:aggregate-detail', kwargs={'pk': self.aggregate1.pk})
        response = self.client.put(url, data, format='json', **self.header)

        self.assertHttpStatus(response, status.HTTP_200_OK)
        self.assertEqual(Aggregate.objects.count(), 3)
        aggregate1 = Aggregate.objects.get(pk=response.data['id'])
        self.assertEqual(str(aggregate1.prefix), data['prefix'])
        self.assertEqual(aggregate1.rir_id, data['rir'])

    def test_delete_aggregate(self):

        url = reverse('ipam-api:aggregate-detail', kwargs={'pk': self.aggregate1.pk})
        response = self.client.delete(url, **self.header)

        self.assertHttpStatus(response, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Aggregate.objects.count(), 2)


class RoleTest(APITestCase):

    def setUp(self):

        super(RoleTest, self).setUp()

        self.role1 = Role.objects.create(name='Test Role 1', slug='test-role-1')
        self.role2 = Role.objects.create(name='Test Role 2', slug='test-role-2')
        self.role3 = Role.objects.create(name='Test Role 3', slug='test-role-3')

    def test_get_role(self):

        url = reverse('ipam-api:role-detail', kwargs={'pk': self.role1.pk})
        response = self.client.get(url, **self.header)

        self.assertEqual(response.data['name'], self.role1.name)

    def test_list_roles(self):

        url = reverse('ipam-api:role-list')
        response = self.client.get(url, **self.header)

        self.assertEqual(response.data['count'], 3)

    def test_list_roles_brief(self):

        url = reverse('ipam-api:role-list')
        response = self.client.get('{}?brief=1'.format(url), **self.header)

        self.assertEqual(
            sorted(response.data['results'][0]),
            ['id', 'name', 'slug', 'url']
        )

    def test_create_role(self):

        data = {
            'name': 'Test Role 4',
            'slug': 'test-role-4',
        }

        url = reverse('ipam-api:role-list')
        response = self.client.post(url, data, format='json', **self.header)

        self.assertHttpStatus(response, status.HTTP_201_CREATED)
        self.assertEqual(Role.objects.count(), 4)
        role4 = Role.objects.get(pk=response.data['id'])
        self.assertEqual(role4.name, data['name'])
        self.assertEqual(role4.slug, data['slug'])

    def test_create_role_bulk(self):

        data = [
            {
                'name': 'Test Role 4',
                'slug': 'test-role-4',
            },
            {
                'name': 'Test Role 5',
                'slug': 'test-role-5',
            },
            {
                'name': 'Test Role 6',
                'slug': 'test-role-6',
            },
        ]

        url = reverse('ipam-api:role-list')
        response = self.client.post(url, data, format='json', **self.header)

        self.assertHttpStatus(response, status.HTTP_201_CREATED)
        self.assertEqual(Role.objects.count(), 6)
        self.assertEqual(response.data[0]['name'], data[0]['name'])
        self.assertEqual(response.data[1]['name'], data[1]['name'])
        self.assertEqual(response.data[2]['name'], data[2]['name'])

    def test_update_role(self):

        data = {
            'name': 'Test Role X',
            'slug': 'test-role-x',
        }

        url = reverse('ipam-api:role-detail', kwargs={'pk': self.role1.pk})
        response = self.client.put(url, data, format='json', **self.header)

        self.assertHttpStatus(response, status.HTTP_200_OK)
        self.assertEqual(Role.objects.count(), 3)
        role1 = Role.objects.get(pk=response.data['id'])
        self.assertEqual(role1.name, data['name'])
        self.assertEqual(role1.slug, data['slug'])

    def test_delete_role(self):

        url = reverse('ipam-api:role-detail', kwargs={'pk': self.role1.pk})
        response = self.client.delete(url, **self.header)

        self.assertHttpStatus(response, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Role.objects.count(), 2)


class PrefixTest(APITestCase):

    def setUp(self):

        super(PrefixTest, self).setUp()

        self.site1 = Site.objects.create(name='Test Site 1', slug='test-site-1')
        self.vrf1 = VRF.objects.create(name='Test VRF 1', rd='65000:1')
        self.vlan1 = VLAN.objects.create(vid=1, name='Test VLAN 1')
        self.role1 = Role.objects.create(name='Test Role 1', slug='test-role-1')
        self.prefix1 = Prefix.objects.create(prefix=IPNetwork('192.168.1.0/24'))
        self.prefix2 = Prefix.objects.create(prefix=IPNetwork('192.168.2.0/24'))
        self.prefix3 = Prefix.objects.create(prefix=IPNetwork('192.168.3.0/24'))

    def test_get_prefix(self):

        url = reverse('ipam-api:prefix-detail', kwargs={'pk': self.prefix1.pk})
        response = self.client.get(url, **self.header)

        self.assertEqual(response.data['prefix'], str(self.prefix1.prefix))

    def test_list_prefixes(self):

        url = reverse('ipam-api:prefix-list')
        response = self.client.get(url, **self.header)

        self.assertEqual(response.data['count'], 3)

    def test_list_prefixes_brief(self):

        url = reverse('ipam-api:prefix-list')
        response = self.client.get('{}?brief=1'.format(url), **self.header)

        self.assertEqual(
            sorted(response.data['results'][0]),
            ['family', 'id', 'prefix', 'url']
        )

    def test_create_prefix(self):

        data = {
            'prefix': '192.168.4.0/24',
            'site': self.site1.pk,
            'vrf': self.vrf1.pk,
            'vlan': self.vlan1.pk,
            'role': self.role1.pk,
        }

        url = reverse('ipam-api:prefix-list')
        response = self.client.post(url, data, format='json', **self.header)

        self.assertHttpStatus(response, status.HTTP_201_CREATED)
        self.assertEqual(Prefix.objects.count(), 4)
        prefix4 = Prefix.objects.get(pk=response.data['id'])
        self.assertEqual(str(prefix4.prefix), data['prefix'])
        self.assertEqual(prefix4.site_id, data['site'])
        self.assertEqual(prefix4.vrf_id, data['vrf'])
        self.assertEqual(prefix4.vlan_id, data['vlan'])
        self.assertEqual(prefix4.role_id, data['role'])

    def test_create_prefix_bulk(self):

        data = [
            {
                'prefix': '10.0.1.0/24',
            },
            {
                'prefix': '10.0.2.0/24',
            },
            {
                'prefix': '10.0.3.0/24',
            },
        ]

        url = reverse('ipam-api:prefix-list')
        response = self.client.post(url, data, format='json', **self.header)

        self.assertHttpStatus(response, status.HTTP_201_CREATED)
        self.assertEqual(Prefix.objects.count(), 6)
        self.assertEqual(response.data[0]['prefix'], data[0]['prefix'])
        self.assertEqual(response.data[1]['prefix'], data[1]['prefix'])
        self.assertEqual(response.data[2]['prefix'], data[2]['prefix'])

    def test_update_prefix(self):

        data = {
            'prefix': '192.168.99.0/24',
            'site': self.site1.pk,
            'vrf': self.vrf1.pk,
            'vlan': self.vlan1.pk,
            'role': self.role1.pk,
        }

        url = reverse('ipam-api:prefix-detail', kwargs={'pk': self.prefix1.pk})
        response = self.client.put(url, data, format='json', **self.header)

        self.assertHttpStatus(response, status.HTTP_200_OK)
        self.assertEqual(Prefix.objects.count(), 3)
        prefix1 = Prefix.objects.get(pk=response.data['id'])
        self.assertEqual(str(prefix1.prefix), data['prefix'])
        self.assertEqual(prefix1.site_id, data['site'])
        self.assertEqual(prefix1.vrf_id, data['vrf'])
        self.assertEqual(prefix1.vlan_id, data['vlan'])
        self.assertEqual(prefix1.role_id, data['role'])

    def test_delete_prefix(self):

        url = reverse('ipam-api:prefix-detail', kwargs={'pk': self.prefix1.pk})
        response = self.client.delete(url, **self.header)

        self.assertHttpStatus(response, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Prefix.objects.count(), 2)

    def test_list_available_prefixes(self):

        prefix = Prefix.objects.create(prefix=IPNetwork('192.0.2.0/24'))
        Prefix.objects.create(prefix=IPNetwork('192.0.2.64/26'))
        Prefix.objects.create(prefix=IPNetwork('192.0.2.192/27'))
        url = reverse('ipam-api:prefix-available-prefixes', kwargs={'pk': prefix.pk})

        # Retrieve all available IPs
        response = self.client.get(url, **self.header)
        available_prefixes = ['192.0.2.0/26', '192.0.2.128/26', '192.0.2.224/27']
        for i, p in enumerate(response.data):
            self.assertEqual(p['prefix'], available_prefixes[i])

    def test_create_single_available_prefix(self):

        vrf = VRF.objects.create(name='Test VRF 1', rd='1234')
        prefix = Prefix.objects.create(prefix=IPNetwork('192.0.2.0/28'), vrf=vrf, is_pool=True)
        url = reverse('ipam-api:prefix-available-prefixes', kwargs={'pk': prefix.pk})

        # Create four available prefixes with individual requests
        prefixes_to_be_created = [
            '192.0.2.0/30',
            '192.0.2.4/30',
            '192.0.2.8/30',
            '192.0.2.12/30',
        ]
        for i in range(4):
            data = {
                'prefix_length': 30,
                'description': 'Test Prefix {}'.format(i + 1)
            }
            response = self.client.post(url, data, format='json', **self.header)
            self.assertHttpStatus(response, status.HTTP_201_CREATED)
            self.assertEqual(response.data['prefix'], prefixes_to_be_created[i])
            self.assertEqual(response.data['vrf']['id'], vrf.pk)
            self.assertEqual(response.data['description'], data['description'])

        # Try to create one more prefix
        response = self.client.post(url, {'prefix_length': 30}, **self.header)
        self.assertHttpStatus(response, status.HTTP_400_BAD_REQUEST)
        self.assertIn('detail', response.data)

    def test_create_multiple_available_prefixes(self):

        prefix = Prefix.objects.create(prefix=IPNetwork('192.0.2.0/28'), is_pool=True)
        url = reverse('ipam-api:prefix-available-prefixes', kwargs={'pk': prefix.pk})

        # Try to create five /30s (only four are available)
        data = [
            {'prefix_length': 30, 'description': 'Test Prefix 1'},
            {'prefix_length': 30, 'description': 'Test Prefix 2'},
            {'prefix_length': 30, 'description': 'Test Prefix 3'},
            {'prefix_length': 30, 'description': 'Test Prefix 4'},
            {'prefix_length': 30, 'description': 'Test Prefix 5'},
        ]
        response = self.client.post(url, data, format='json', **self.header)
        self.assertHttpStatus(response, status.HTTP_400_BAD_REQUEST)
        self.assertIn('detail', response.data)

        # Verify that no prefixes were created (the entire /28 is still available)
        response = self.client.get(url, **self.header)
        self.assertEqual(response.data[0]['prefix'], '192.0.2.0/28')

        # Create four /30s in a single request
        response = self.client.post(url, data[:4], format='json', **self.header)
        self.assertHttpStatus(response, status.HTTP_201_CREATED)
        self.assertEqual(len(response.data), 4)

    def test_list_available_ips(self):

        prefix = Prefix.objects.create(prefix=IPNetwork('192.0.2.0/29'), is_pool=True)
        url = reverse('ipam-api:prefix-available-ips', kwargs={'pk': prefix.pk})

        # Retrieve all available IPs
        response = self.client.get(url, **self.header)
        self.assertEqual(len(response.data), 8)  # 8 because prefix.is_pool = True

        # Change the prefix to not be a pool and try again
        prefix.is_pool = False
        prefix.save()
        response = self.client.get(url, **self.header)
        self.assertEqual(len(response.data), 6)  # 8 - 2 because prefix.is_pool = False

    def test_create_single_available_ip(self):

        vrf = VRF.objects.create(name='Test VRF 1', rd='1234')
        prefix = Prefix.objects.create(prefix=IPNetwork('192.0.2.0/30'), vrf=vrf, is_pool=True)
        url = reverse('ipam-api:prefix-available-ips', kwargs={'pk': prefix.pk})

        # Create all four available IPs with individual requests
        for i in range(1, 5):
            data = {
                'description': 'Test IP {}'.format(i)
            }
            response = self.client.post(url, data, format='json', **self.header)
            self.assertHttpStatus(response, status.HTTP_201_CREATED)
            self.assertEqual(response.data['vrf']['id'], vrf.pk)
            self.assertEqual(response.data['description'], data['description'])

        # Try to create one more IP
        response = self.client.post(url, {}, **self.header)
        self.assertHttpStatus(response, status.HTTP_400_BAD_REQUEST)
        self.assertIn('detail', response.data)

    def test_create_multiple_available_ips(self):

        prefix = Prefix.objects.create(prefix=IPNetwork('192.0.2.0/29'), is_pool=True)
        url = reverse('ipam-api:prefix-available-ips', kwargs={'pk': prefix.pk})

        # Try to create nine IPs (only eight are available)
        data = [{'description': 'Test IP {}'.format(i)} for i in range(1, 10)]  # 9 IPs
        response = self.client.post(url, data, format='json', **self.header)
        self.assertHttpStatus(response, status.HTTP_400_BAD_REQUEST)
        self.assertIn('detail', response.data)

        # Verify that no IPs were created (eight are still available)
        response = self.client.get(url, **self.header)
        self.assertEqual(len(response.data), 8)

        # Create all eight available IPs in a single request
        data = [{'description': 'Test IP {}'.format(i)} for i in range(1, 9)]  # 8 IPs
        response = self.client.post(url, data, format='json', **self.header)
        self.assertHttpStatus(response, status.HTTP_201_CREATED)
        self.assertEqual(len(response.data), 8)


class IPAddressTest(APITestCase):

    def setUp(self):

        super(IPAddressTest, self).setUp()

        self.vrf1 = VRF.objects.create(name='Test VRF 1', rd='65000:1')
        self.ipaddress1 = IPAddress.objects.create(address=IPNetwork('192.168.0.1/24'))
        self.ipaddress2 = IPAddress.objects.create(address=IPNetwork('192.168.0.2/24'))
        self.ipaddress3 = IPAddress.objects.create(address=IPNetwork('192.168.0.3/24'))

    def test_get_ipaddress(self):

        url = reverse('ipam-api:ipaddress-detail', kwargs={'pk': self.ipaddress1.pk})
        response = self.client.get(url, **self.header)

        self.assertEqual(response.data['address'], str(self.ipaddress1.address))

    def test_list_ipaddresss(self):

        url = reverse('ipam-api:ipaddress-list')
        response = self.client.get(url, **self.header)

        self.assertEqual(response.data['count'], 3)

    def test_list_ipaddresses_brief(self):

        url = reverse('ipam-api:ipaddress-list')
        response = self.client.get('{}?brief=1'.format(url), **self.header)

        self.assertEqual(
            sorted(response.data['results'][0]),
            ['address', 'family', 'id', 'url']
        )

    def test_create_ipaddress(self):

        data = {
            'address': '192.168.0.4/24',
            'vrf': self.vrf1.pk,
        }

        url = reverse('ipam-api:ipaddress-list')
        response = self.client.post(url, data, format='json', **self.header)

        self.assertHttpStatus(response, status.HTTP_201_CREATED)
        self.assertEqual(IPAddress.objects.count(), 4)
        ipaddress4 = IPAddress.objects.get(pk=response.data['id'])
        self.assertEqual(str(ipaddress4.address), data['address'])
        self.assertEqual(ipaddress4.vrf_id, data['vrf'])

    def test_create_ipaddress_bulk(self):

        data = [
            {
                'address': '192.168.0.4/24',
            },
            {
                'address': '192.168.0.5/24',
            },
            {
                'address': '192.168.0.6/24',
            },
        ]

        url = reverse('ipam-api:ipaddress-list')
        response = self.client.post(url, data, format='json', **self.header)

        self.assertHttpStatus(response, status.HTTP_201_CREATED)
        self.assertEqual(IPAddress.objects.count(), 6)
        self.assertEqual(response.data[0]['address'], data[0]['address'])
        self.assertEqual(response.data[1]['address'], data[1]['address'])
        self.assertEqual(response.data[2]['address'], data[2]['address'])

    def test_update_ipaddress(self):

        data = {
            'address': '192.168.0.99/24',
            'vrf': self.vrf1.pk,
        }

        url = reverse('ipam-api:ipaddress-detail', kwargs={'pk': self.ipaddress1.pk})
        response = self.client.put(url, data, format='json', **self.header)

        self.assertHttpStatus(response, status.HTTP_200_OK)
        self.assertEqual(IPAddress.objects.count(), 3)
        ipaddress1 = IPAddress.objects.get(pk=response.data['id'])
        self.assertEqual(str(ipaddress1.address), data['address'])
        self.assertEqual(ipaddress1.vrf_id, data['vrf'])

    def test_delete_ipaddress(self):

        url = reverse('ipam-api:ipaddress-detail', kwargs={'pk': self.ipaddress1.pk})
        response = self.client.delete(url, **self.header)

        self.assertHttpStatus(response, status.HTTP_204_NO_CONTENT)
        self.assertEqual(IPAddress.objects.count(), 2)


class VLANGroupTest(APITestCase):

    def setUp(self):

        super(VLANGroupTest, self).setUp()

        self.vlangroup1 = VLANGroup.objects.create(name='Test VLAN Group 1', slug='test-vlan-group-1')
        self.vlangroup2 = VLANGroup.objects.create(name='Test VLAN Group 2', slug='test-vlan-group-2')
        self.vlangroup3 = VLANGroup.objects.create(name='Test VLAN Group 3', slug='test-vlan-group-3')

    def test_get_vlangroup(self):

        url = reverse('ipam-api:vlangroup-detail', kwargs={'pk': self.vlangroup1.pk})
        response = self.client.get(url, **self.header)

        self.assertEqual(response.data['name'], self.vlangroup1.name)

    def test_list_vlangroups(self):

        url = reverse('ipam-api:vlangroup-list')
        response = self.client.get(url, **self.header)

        self.assertEqual(response.data['count'], 3)

    def test_list_vlangroups_brief(self):

        url = reverse('ipam-api:vlangroup-list')
        response = self.client.get('{}?brief=1'.format(url), **self.header)

        self.assertEqual(
            sorted(response.data['results'][0]),
            ['id', 'name', 'slug', 'url']
        )

    def test_create_vlangroup(self):

        data = {
            'name': 'Test VLAN Group 4',
            'slug': 'test-vlan-group-4',
        }

        url = reverse('ipam-api:vlangroup-list')
        response = self.client.post(url, data, format='json', **self.header)

        self.assertHttpStatus(response, status.HTTP_201_CREATED)
        self.assertEqual(VLANGroup.objects.count(), 4)
        vlangroup4 = VLANGroup.objects.get(pk=response.data['id'])
        self.assertEqual(vlangroup4.name, data['name'])
        self.assertEqual(vlangroup4.slug, data['slug'])

    def test_create_vlangroup_bulk(self):

        data = [
            {
                'name': 'Test VLAN Group 4',
                'slug': 'test-vlan-group-4',
            },
            {
                'name': 'Test VLAN Group 5',
                'slug': 'test-vlan-group-5',
            },
            {
                'name': 'Test VLAN Group 6',
                'slug': 'test-vlan-group-6',
            },
        ]

        url = reverse('ipam-api:vlangroup-list')
        response = self.client.post(url, data, format='json', **self.header)

        self.assertHttpStatus(response, status.HTTP_201_CREATED)
        self.assertEqual(VLANGroup.objects.count(), 6)
        self.assertEqual(response.data[0]['name'], data[0]['name'])
        self.assertEqual(response.data[1]['name'], data[1]['name'])
        self.assertEqual(response.data[2]['name'], data[2]['name'])

    def test_update_vlangroup(self):

        data = {
            'name': 'Test VLAN Group X',
            'slug': 'test-vlan-group-x',
        }

        url = reverse('ipam-api:vlangroup-detail', kwargs={'pk': self.vlangroup1.pk})
        response = self.client.put(url, data, format='json', **self.header)

        self.assertHttpStatus(response, status.HTTP_200_OK)
        self.assertEqual(VLANGroup.objects.count(), 3)
        vlangroup1 = VLANGroup.objects.get(pk=response.data['id'])
        self.assertEqual(vlangroup1.name, data['name'])
        self.assertEqual(vlangroup1.slug, data['slug'])

    def test_delete_vlangroup(self):

        url = reverse('ipam-api:vlangroup-detail', kwargs={'pk': self.vlangroup1.pk})
        response = self.client.delete(url, **self.header)

        self.assertHttpStatus(response, status.HTTP_204_NO_CONTENT)
        self.assertEqual(VLANGroup.objects.count(), 2)


class VLANTest(APITestCase):

    def setUp(self):

        super(VLANTest, self).setUp()

        self.vlan1 = VLAN.objects.create(vid=1, name='Test VLAN 1')
        self.vlan2 = VLAN.objects.create(vid=2, name='Test VLAN 2')
        self.vlan3 = VLAN.objects.create(vid=3, name='Test VLAN 3')

    def test_get_vlan(self):

        url = reverse('ipam-api:vlan-detail', kwargs={'pk': self.vlan1.pk})
        response = self.client.get(url, **self.header)

        self.assertEqual(response.data['name'], self.vlan1.name)

    def test_list_vlans(self):

        url = reverse('ipam-api:vlan-list')
        response = self.client.get(url, **self.header)

        self.assertEqual(response.data['count'], 3)

    def test_list_vlans_brief(self):

        url = reverse('ipam-api:vlan-list')
        response = self.client.get('{}?brief=1'.format(url), **self.header)

        self.assertEqual(
            sorted(response.data['results'][0]),
            ['display_name', 'id', 'name', 'url', 'vid']
        )

    def test_create_vlan(self):

        data = {
            'vid': 4,
            'name': 'Test VLAN 4',
        }

        url = reverse('ipam-api:vlan-list')
        response = self.client.post(url, data, format='json', **self.header)

        self.assertHttpStatus(response, status.HTTP_201_CREATED)
        self.assertEqual(VLAN.objects.count(), 4)
        vlan4 = VLAN.objects.get(pk=response.data['id'])
        self.assertEqual(vlan4.vid, data['vid'])
        self.assertEqual(vlan4.name, data['name'])

    def test_create_vlan_bulk(self):

        data = [
            {
                'vid': 4,
                'name': 'Test VLAN 4',
            },
            {
                'vid': 5,
                'name': 'Test VLAN 5',
            },
            {
                'vid': 6,
                'name': 'Test VLAN 6',
            },
        ]

        url = reverse('ipam-api:vlan-list')
        response = self.client.post(url, data, format='json', **self.header)

        self.assertHttpStatus(response, status.HTTP_201_CREATED)
        self.assertEqual(VLAN.objects.count(), 6)
        self.assertEqual(response.data[0]['name'], data[0]['name'])
        self.assertEqual(response.data[1]['name'], data[1]['name'])
        self.assertEqual(response.data[2]['name'], data[2]['name'])

    def test_update_vlan(self):

        data = {
            'vid': 99,
            'name': 'Test VLAN X',
        }

        url = reverse('ipam-api:vlan-detail', kwargs={'pk': self.vlan1.pk})
        response = self.client.put(url, data, format='json', **self.header)

        self.assertHttpStatus(response, status.HTTP_200_OK)
        self.assertEqual(VLAN.objects.count(), 3)
        vlan1 = VLAN.objects.get(pk=response.data['id'])
        self.assertEqual(vlan1.vid, data['vid'])
        self.assertEqual(vlan1.name, data['name'])

    def test_delete_vlan(self):

        url = reverse('ipam-api:vlan-detail', kwargs={'pk': self.vlan1.pk})
        response = self.client.delete(url, **self.header)

        self.assertHttpStatus(response, status.HTTP_204_NO_CONTENT)
        self.assertEqual(VLAN.objects.count(), 2)


class ServiceTest(APITestCase):

    def setUp(self):

        super(ServiceTest, self).setUp()

        site = Site.objects.create(name='Test Site 1', slug='test-site-1')
        manufacturer = Manufacturer.objects.create(name='Test Manufacturer 1', slug='test-manufacturer-1')
        devicetype = DeviceType.objects.create(manufacturer=manufacturer, model='Test Device Type 1')
        devicerole = DeviceRole.objects.create(name='Test Device Role 1', slug='test-device-role-1')
        self.device1 = Device.objects.create(
            name='Test Device 1', site=site, device_type=devicetype, device_role=devicerole
        )
        self.device2 = Device.objects.create(
            name='Test Device 2', site=site, device_type=devicetype, device_role=devicerole
        )
        self.service1 = Service.objects.create(
            device=self.device1, name='Test Service 1', protocol=IP_PROTOCOL_TCP, port=1
        )
        self.service1 = Service.objects.create(
            device=self.device1, name='Test Service 2', protocol=IP_PROTOCOL_TCP, port=2
        )
        self.service1 = Service.objects.create(
            device=self.device1, name='Test Service 3', protocol=IP_PROTOCOL_TCP, port=3
        )

    def test_get_service(self):

        url = reverse('ipam-api:service-detail', kwargs={'pk': self.service1.pk})
        response = self.client.get(url, **self.header)

        self.assertEqual(response.data['name'], self.service1.name)

    def test_list_services(self):

        url = reverse('ipam-api:service-list')
        response = self.client.get(url, **self.header)

        self.assertEqual(response.data['count'], 3)

    def test_create_service(self):

        data = {
            'device': self.device1.pk,
            'name': 'Test Service 4',
            'protocol': IP_PROTOCOL_TCP,
            'port': 4,
        }

        url = reverse('ipam-api:service-list')
        response = self.client.post(url, data, format='json', **self.header)

        self.assertHttpStatus(response, status.HTTP_201_CREATED)
        self.assertEqual(Service.objects.count(), 4)
        service4 = Service.objects.get(pk=response.data['id'])
        self.assertEqual(service4.device_id, data['device'])
        self.assertEqual(service4.name, data['name'])
        self.assertEqual(service4.protocol, data['protocol'])
        self.assertEqual(service4.port, data['port'])

    def test_create_service_bulk(self):

        data = [
            {
                'device': self.device1.pk,
                'name': 'Test Service 4',
                'protocol': IP_PROTOCOL_TCP,
                'port': 4,
            },
            {
                'device': self.device1.pk,
                'name': 'Test Service 5',
                'protocol': IP_PROTOCOL_TCP,
                'port': 5,
            },
            {
                'device': self.device1.pk,
                'name': 'Test Service 6',
                'protocol': IP_PROTOCOL_TCP,
                'port': 6,
            },
        ]

        url = reverse('ipam-api:service-list')
        response = self.client.post(url, data, format='json', **self.header)

        self.assertHttpStatus(response, status.HTTP_201_CREATED)
        self.assertEqual(Service.objects.count(), 6)
        self.assertEqual(response.data[0]['name'], data[0]['name'])
        self.assertEqual(response.data[1]['name'], data[1]['name'])
        self.assertEqual(response.data[2]['name'], data[2]['name'])

    def test_update_service(self):

        data = {
            'device': self.device2.pk,
            'name': 'Test Service X',
            'protocol': IP_PROTOCOL_UDP,
            'port': 99,
        }

        url = reverse('ipam-api:service-detail', kwargs={'pk': self.service1.pk})
        response = self.client.put(url, data, format='json', **self.header)

        self.assertHttpStatus(response, status.HTTP_200_OK)
        self.assertEqual(Service.objects.count(), 3)
        service1 = Service.objects.get(pk=response.data['id'])
        self.assertEqual(service1.device_id, data['device'])
        self.assertEqual(service1.name, data['name'])
        self.assertEqual(service1.protocol, data['protocol'])
        self.assertEqual(service1.port, data['port'])

    def test_delete_service(self):

        url = reverse('ipam-api:service-detail', kwargs={'pk': self.service1.pk})
        response = self.client.delete(url, **self.header)

        self.assertHttpStatus(response, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Service.objects.count(), 2)
