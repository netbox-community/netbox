from __future__ import unicode_literals

from django.urls import reverse
from netaddr import IPNetwork
from rest_framework import status

from dcim.constants import IFACE_FF_VIRTUAL, IFACE_MODE_TAGGED
from dcim.models import Interface
from ipam.models import IPAddress, VLAN
from utilities.testing import APITestCase
from virtualization.models import Cluster, ClusterGroup, ClusterType, VirtualMachine


class ClusterTypeTest(APITestCase):

    def setUp(self):

        super(ClusterTypeTest, self).setUp()

        self.clustertype1 = ClusterType.objects.create(name='Test Cluster Type 1', slug='test-cluster-type-1')
        self.clustertype2 = ClusterType.objects.create(name='Test Cluster Type 2', slug='test-cluster-type-2')
        self.clustertype3 = ClusterType.objects.create(name='Test Cluster Type 3', slug='test-cluster-type-3')

    def test_get_clustertype(self):

        url = reverse('virtualization-api:clustertype-detail', kwargs={'pk': self.clustertype1.pk})
        response = self.client.get(url, **self.header)

        self.assertEqual(response.data['name'], self.clustertype1.name)

    def test_list_clustertypes(self):

        url = reverse('virtualization-api:clustertype-list')
        response = self.client.get(url, **self.header)

        self.assertEqual(response.data['count'], 3)

    def test_list_clustertypes_brief(self):

        url = reverse('virtualization-api:clustertype-list')
        response = self.client.get('{}?brief=1'.format(url), **self.header)

        self.assertEqual(
            sorted(response.data['results'][0]),
            ['id', 'name', 'slug', 'url']
        )

    def test_create_clustertype(self):

        data = {
            'name': 'Test Cluster Type 4',
            'slug': 'test-cluster-type-4',
        }

        url = reverse('virtualization-api:clustertype-list')
        response = self.client.post(url, data, format='json', **self.header)

        self.assertHttpStatus(response, status.HTTP_201_CREATED)
        self.assertEqual(ClusterType.objects.count(), 4)
        clustertype4 = ClusterType.objects.get(pk=response.data['id'])
        self.assertEqual(clustertype4.name, data['name'])
        self.assertEqual(clustertype4.slug, data['slug'])

    def test_create_clustertype_bulk(self):

        data = [
            {
                'name': 'Test Cluster Type 4',
                'slug': 'test-cluster-type-4',
            },
            {
                'name': 'Test Cluster Type 5',
                'slug': 'test-cluster-type-5',
            },
            {
                'name': 'Test Cluster Type 6',
                'slug': 'test-cluster-type-6',
            },
        ]

        url = reverse('virtualization-api:clustertype-list')
        response = self.client.post(url, data, format='json', **self.header)

        self.assertHttpStatus(response, status.HTTP_201_CREATED)
        self.assertEqual(ClusterType.objects.count(), 6)
        self.assertEqual(response.data[0]['name'], data[0]['name'])
        self.assertEqual(response.data[1]['name'], data[1]['name'])
        self.assertEqual(response.data[2]['name'], data[2]['name'])

    def test_update_clustertype(self):

        data = {
            'name': 'Test Cluster Type X',
            'slug': 'test-cluster-type-x',
        }

        url = reverse('virtualization-api:clustertype-detail', kwargs={'pk': self.clustertype1.pk})
        response = self.client.put(url, data, format='json', **self.header)

        self.assertHttpStatus(response, status.HTTP_200_OK)
        self.assertEqual(ClusterType.objects.count(), 3)
        clustertype1 = ClusterType.objects.get(pk=response.data['id'])
        self.assertEqual(clustertype1.name, data['name'])
        self.assertEqual(clustertype1.slug, data['slug'])

    def test_delete_clustertype(self):

        url = reverse('virtualization-api:clustertype-detail', kwargs={'pk': self.clustertype1.pk})
        response = self.client.delete(url, **self.header)

        self.assertHttpStatus(response, status.HTTP_204_NO_CONTENT)
        self.assertEqual(ClusterType.objects.count(), 2)


class ClusterGroupTest(APITestCase):

    def setUp(self):

        super(ClusterGroupTest, self).setUp()

        self.clustergroup1 = ClusterGroup.objects.create(name='Test Cluster Group 1', slug='test-cluster-group-1')
        self.clustergroup2 = ClusterGroup.objects.create(name='Test Cluster Group 2', slug='test-cluster-group-2')
        self.clustergroup3 = ClusterGroup.objects.create(name='Test Cluster Group 3', slug='test-cluster-group-3')

    def test_get_clustergroup(self):

        url = reverse('virtualization-api:clustergroup-detail', kwargs={'pk': self.clustergroup1.pk})
        response = self.client.get(url, **self.header)

        self.assertEqual(response.data['name'], self.clustergroup1.name)

    def test_list_clustergroups(self):

        url = reverse('virtualization-api:clustergroup-list')
        response = self.client.get(url, **self.header)

        self.assertEqual(response.data['count'], 3)

    def test_list_clustergroups_brief(self):

        url = reverse('virtualization-api:clustergroup-list')
        response = self.client.get('{}?brief=1'.format(url), **self.header)

        self.assertEqual(
            sorted(response.data['results'][0]),
            ['id', 'name', 'slug', 'url']
        )

    def test_create_clustergroup(self):

        data = {
            'name': 'Test Cluster Group 4',
            'slug': 'test-cluster-group-4',
        }

        url = reverse('virtualization-api:clustergroup-list')
        response = self.client.post(url, data, format='json', **self.header)

        self.assertHttpStatus(response, status.HTTP_201_CREATED)
        self.assertEqual(ClusterGroup.objects.count(), 4)
        clustergroup4 = ClusterGroup.objects.get(pk=response.data['id'])
        self.assertEqual(clustergroup4.name, data['name'])
        self.assertEqual(clustergroup4.slug, data['slug'])

    def test_create_clustergroup_bulk(self):

        data = [
            {
                'name': 'Test Cluster Group 4',
                'slug': 'test-cluster-group-4',
            },
            {
                'name': 'Test Cluster Group 5',
                'slug': 'test-cluster-group-5',
            },
            {
                'name': 'Test Cluster Group 6',
                'slug': 'test-cluster-group-6',
            },
        ]

        url = reverse('virtualization-api:clustergroup-list')
        response = self.client.post(url, data, format='json', **self.header)

        self.assertHttpStatus(response, status.HTTP_201_CREATED)
        self.assertEqual(ClusterGroup.objects.count(), 6)
        self.assertEqual(response.data[0]['name'], data[0]['name'])
        self.assertEqual(response.data[1]['name'], data[1]['name'])
        self.assertEqual(response.data[2]['name'], data[2]['name'])

    def test_update_clustergroup(self):

        data = {
            'name': 'Test Cluster Group X',
            'slug': 'test-cluster-group-x',
        }

        url = reverse('virtualization-api:clustergroup-detail', kwargs={'pk': self.clustergroup1.pk})
        response = self.client.put(url, data, format='json', **self.header)

        self.assertHttpStatus(response, status.HTTP_200_OK)
        self.assertEqual(ClusterGroup.objects.count(), 3)
        clustergroup1 = ClusterGroup.objects.get(pk=response.data['id'])
        self.assertEqual(clustergroup1.name, data['name'])
        self.assertEqual(clustergroup1.slug, data['slug'])

    def test_delete_clustergroup(self):

        url = reverse('virtualization-api:clustergroup-detail', kwargs={'pk': self.clustergroup1.pk})
        response = self.client.delete(url, **self.header)

        self.assertHttpStatus(response, status.HTTP_204_NO_CONTENT)
        self.assertEqual(ClusterGroup.objects.count(), 2)


class ClusterTest(APITestCase):

    def setUp(self):

        super(ClusterTest, self).setUp()

        cluster_type = ClusterType.objects.create(name='Test Cluster Type 1', slug='test-cluster-type-1')
        cluster_group = ClusterGroup.objects.create(name='Test Cluster Group 1', slug='test-cluster-group-1')

        self.cluster1 = Cluster.objects.create(name='Test Cluster 1', type=cluster_type, group=cluster_group)
        self.cluster2 = Cluster.objects.create(name='Test Cluster 2', type=cluster_type, group=cluster_group)
        self.cluster3 = Cluster.objects.create(name='Test Cluster 3', type=cluster_type, group=cluster_group)

    def test_get_cluster(self):

        url = reverse('virtualization-api:cluster-detail', kwargs={'pk': self.cluster1.pk})
        response = self.client.get(url, **self.header)

        self.assertEqual(response.data['name'], self.cluster1.name)

    def test_list_clusters(self):

        url = reverse('virtualization-api:cluster-list')
        response = self.client.get(url, **self.header)

        self.assertEqual(response.data['count'], 3)

    def test_list_clusters_brief(self):

        url = reverse('virtualization-api:cluster-list')
        response = self.client.get('{}?brief=1'.format(url), **self.header)

        self.assertEqual(
            sorted(response.data['results'][0]),
            ['id', 'name', 'url']
        )

    def test_create_cluster(self):

        data = {
            'name': 'Test Cluster 4',
            'type': ClusterType.objects.first().pk,
            'group': ClusterGroup.objects.first().pk,
        }

        url = reverse('virtualization-api:cluster-list')
        response = self.client.post(url, data, format='json', **self.header)

        self.assertHttpStatus(response, status.HTTP_201_CREATED)
        self.assertEqual(Cluster.objects.count(), 4)
        cluster4 = Cluster.objects.get(pk=response.data['id'])
        self.assertEqual(cluster4.name, data['name'])
        self.assertEqual(cluster4.type.pk, data['type'])
        self.assertEqual(cluster4.group.pk, data['group'])

    def test_create_cluster_bulk(self):

        data = [
            {
                'name': 'Test Cluster 4',
                'type': ClusterType.objects.first().pk,
                'group': ClusterGroup.objects.first().pk,
            },
            {
                'name': 'Test Cluster 5',
                'type': ClusterType.objects.first().pk,
                'group': ClusterGroup.objects.first().pk,
            },
            {
                'name': 'Test Cluster 6',
                'type': ClusterType.objects.first().pk,
                'group': ClusterGroup.objects.first().pk,
            },
        ]

        url = reverse('virtualization-api:cluster-list')
        response = self.client.post(url, data, format='json', **self.header)

        self.assertHttpStatus(response, status.HTTP_201_CREATED)
        self.assertEqual(Cluster.objects.count(), 6)
        self.assertEqual(response.data[0]['name'], data[0]['name'])
        self.assertEqual(response.data[1]['name'], data[1]['name'])
        self.assertEqual(response.data[2]['name'], data[2]['name'])

    def test_update_cluster(self):

        cluster_type2 = ClusterType.objects.create(name='Test Cluster Type 2', slug='test-cluster-type-2')
        cluster_group2 = ClusterGroup.objects.create(name='Test Cluster Group 2', slug='test-cluster-group-2')
        data = {
            'name': 'Test Cluster X',
            'type': cluster_type2.pk,
            'group': cluster_group2.pk,
        }

        url = reverse('virtualization-api:cluster-detail', kwargs={'pk': self.cluster1.pk})
        response = self.client.put(url, data, format='json', **self.header)

        self.assertHttpStatus(response, status.HTTP_200_OK)
        self.assertEqual(Cluster.objects.count(), 3)
        cluster1 = Cluster.objects.get(pk=response.data['id'])
        self.assertEqual(cluster1.name, data['name'])
        self.assertEqual(cluster1.type.pk, data['type'])
        self.assertEqual(cluster1.group.pk, data['group'])

    def test_delete_cluster(self):

        url = reverse('virtualization-api:cluster-detail', kwargs={'pk': self.cluster1.pk})
        response = self.client.delete(url, **self.header)

        self.assertHttpStatus(response, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Cluster.objects.count(), 2)


class VirtualMachineTest(APITestCase):

    def setUp(self):

        super(VirtualMachineTest, self).setUp()

        cluster_type = ClusterType.objects.create(name='Test Cluster Type 1', slug='test-cluster-type-1')
        cluster_group = ClusterGroup.objects.create(name='Test Cluster Group 1', slug='test-cluster-group-1')
        self.cluster1 = Cluster.objects.create(name='Test Cluster 1', type=cluster_type, group=cluster_group)

        self.virtualmachine1 = VirtualMachine.objects.create(name='Test Virtual Machine 1', cluster=self.cluster1)
        self.virtualmachine2 = VirtualMachine.objects.create(name='Test Virtual Machine 2', cluster=self.cluster1)
        self.virtualmachine3 = VirtualMachine.objects.create(name='Test Virtual Machine 3', cluster=self.cluster1)

    def test_get_virtualmachine(self):

        url = reverse('virtualization-api:virtualmachine-detail', kwargs={'pk': self.virtualmachine1.pk})
        response = self.client.get(url, **self.header)

        self.assertEqual(response.data['name'], self.virtualmachine1.name)

    def test_list_virtualmachines(self):

        url = reverse('virtualization-api:virtualmachine-list')
        response = self.client.get(url, **self.header)

        self.assertEqual(response.data['count'], 3)

    def test_list_virtualmachines_brief(self):

        url = reverse('virtualization-api:virtualmachine-list')
        response = self.client.get('{}?brief=1'.format(url), **self.header)

        self.assertEqual(
            sorted(response.data['results'][0]),
            ['id', 'name', 'url']
        )

    def test_create_virtualmachine(self):

        data = {
            'name': 'Test Virtual Machine 4',
            'cluster': self.cluster1.pk,
        }

        url = reverse('virtualization-api:virtualmachine-list')
        response = self.client.post(url, data, format='json', **self.header)

        self.assertHttpStatus(response, status.HTTP_201_CREATED)
        self.assertEqual(VirtualMachine.objects.count(), 4)
        virtualmachine4 = VirtualMachine.objects.get(pk=response.data['id'])
        self.assertEqual(virtualmachine4.name, data['name'])
        self.assertEqual(virtualmachine4.cluster.pk, data['cluster'])

    def test_create_virtualmachine_without_cluster(self):

        data = {
            'name': 'Test Virtual Machine 4',
        }

        url = reverse('virtualization-api:virtualmachine-list')
        response = self.client.post(url, data, format='json', **self.header)

        self.assertHttpStatus(response, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(VirtualMachine.objects.count(), 3)

    def test_create_virtualmachine_bulk(self):

        data = [
            {
                'name': 'Test Virtual Machine 4',
                'cluster': self.cluster1.pk,
            },
            {
                'name': 'Test Virtual Machine 5',
                'cluster': self.cluster1.pk,
            },
            {
                'name': 'Test Virtual Machine 6',
                'cluster': self.cluster1.pk,
            },
        ]

        url = reverse('virtualization-api:virtualmachine-list')
        response = self.client.post(url, data, format='json', **self.header)

        self.assertHttpStatus(response, status.HTTP_201_CREATED)
        self.assertEqual(VirtualMachine.objects.count(), 6)
        self.assertEqual(response.data[0]['name'], data[0]['name'])
        self.assertEqual(response.data[1]['name'], data[1]['name'])
        self.assertEqual(response.data[2]['name'], data[2]['name'])

    def test_update_virtualmachine(self):

        interface = Interface.objects.create(name='Test Interface 1', virtual_machine=self.virtualmachine1)
        ip4_address = IPAddress.objects.create(address=IPNetwork('192.0.2.1/24'), interface=interface)
        ip6_address = IPAddress.objects.create(address=IPNetwork('2001:db8::1/64'), interface=interface)

        cluster2 = Cluster.objects.create(
            name='Test Cluster 2',
            type=ClusterType.objects.first(),
            group=ClusterGroup.objects.first()
        )
        data = {
            'name': 'Test Virtual Machine X',
            'cluster': cluster2.pk,
            'primary_ip4': ip4_address.pk,
            'primary_ip6': ip6_address.pk,
        }

        url = reverse('virtualization-api:virtualmachine-detail', kwargs={'pk': self.virtualmachine1.pk})
        response = self.client.put(url, data, format='json', **self.header)

        self.assertHttpStatus(response, status.HTTP_200_OK)
        self.assertEqual(VirtualMachine.objects.count(), 3)
        virtualmachine1 = VirtualMachine.objects.get(pk=response.data['id'])
        self.assertEqual(virtualmachine1.name, data['name'])
        self.assertEqual(virtualmachine1.cluster.pk, data['cluster'])
        self.assertEqual(virtualmachine1.primary_ip4.pk, data['primary_ip4'])
        self.assertEqual(virtualmachine1.primary_ip6.pk, data['primary_ip6'])

    def test_delete_virtualmachine(self):

        url = reverse('virtualization-api:virtualmachine-detail', kwargs={'pk': self.virtualmachine1.pk})
        response = self.client.delete(url, **self.header)

        self.assertHttpStatus(response, status.HTTP_204_NO_CONTENT)
        self.assertEqual(VirtualMachine.objects.count(), 2)


class InterfaceTest(APITestCase):

    def setUp(self):

        super(InterfaceTest, self).setUp()

        clustertype = ClusterType.objects.create(name='Test Cluster Type 1', slug='test-cluster-type-1')
        cluster = Cluster.objects.create(name='Test Cluster 1', type=clustertype)
        self.virtualmachine = VirtualMachine.objects.create(cluster=cluster, name='Test VM 1')
        self.interface1 = Interface.objects.create(
            virtual_machine=self.virtualmachine,
            name='Test Interface 1',
            form_factor=IFACE_FF_VIRTUAL
        )
        self.interface2 = Interface.objects.create(
            virtual_machine=self.virtualmachine,
            name='Test Interface 2',
            form_factor=IFACE_FF_VIRTUAL
        )
        self.interface3 = Interface.objects.create(
            virtual_machine=self.virtualmachine,
            name='Test Interface 3',
            form_factor=IFACE_FF_VIRTUAL
        )

        self.vlan1 = VLAN.objects.create(name="Test VLAN 1", vid=1)
        self.vlan2 = VLAN.objects.create(name="Test VLAN 2", vid=2)
        self.vlan3 = VLAN.objects.create(name="Test VLAN 3", vid=3)

    def test_get_interface(self):

        url = reverse('virtualization-api:interface-detail', kwargs={'pk': self.interface1.pk})
        response = self.client.get(url, **self.header)

        self.assertEqual(response.data['name'], self.interface1.name)

    def test_list_interfaces(self):

        url = reverse('virtualization-api:interface-list')
        response = self.client.get(url, **self.header)

        self.assertEqual(response.data['count'], 3)

    def test_list_interfaces_brief(self):

        url = reverse('virtualization-api:interface-list')
        response = self.client.get('{}?brief=1'.format(url), **self.header)

        self.assertEqual(
            sorted(response.data['results'][0]),
            ['id', 'name', 'url', 'virtual_machine']
        )

    def test_create_interface(self):

        data = {
            'virtual_machine': self.virtualmachine.pk,
            'name': 'Test Interface 4',
        }

        url = reverse('virtualization-api:interface-list')
        response = self.client.post(url, data, format='json', **self.header)

        self.assertHttpStatus(response, status.HTTP_201_CREATED)
        self.assertEqual(Interface.objects.count(), 4)
        interface4 = Interface.objects.get(pk=response.data['id'])
        self.assertEqual(interface4.virtual_machine_id, data['virtual_machine'])
        self.assertEqual(interface4.name, data['name'])

    def test_create_interface_with_802_1q(self):

        data = {
            'virtual_machine': self.virtualmachine.pk,
            'name': 'Test Interface 4',
            'mode': IFACE_MODE_TAGGED,
            'untagged_vlan': self.vlan3.id,
            'tagged_vlans': [self.vlan1.id, self.vlan2.id],
        }

        url = reverse('virtualization-api:interface-list')
        response = self.client.post(url, data, format='json', **self.header)

        self.assertHttpStatus(response, status.HTTP_201_CREATED)
        self.assertEqual(Interface.objects.count(), 4)
        self.assertEqual(response.data['virtual_machine']['id'], data['virtual_machine'])
        self.assertEqual(response.data['name'], data['name'])
        self.assertEqual(response.data['untagged_vlan']['id'], data['untagged_vlan'])
        self.assertEqual([v['id'] for v in response.data['tagged_vlans']], data['tagged_vlans'])

    def test_create_interface_bulk(self):

        data = [
            {
                'virtual_machine': self.virtualmachine.pk,
                'name': 'Test Interface 4',
            },
            {
                'virtual_machine': self.virtualmachine.pk,
                'name': 'Test Interface 5',
            },
            {
                'virtual_machine': self.virtualmachine.pk,
                'name': 'Test Interface 6',
            },
        ]

        url = reverse('virtualization-api:interface-list')
        response = self.client.post(url, data, format='json', **self.header)

        self.assertHttpStatus(response, status.HTTP_201_CREATED)
        self.assertEqual(Interface.objects.count(), 6)
        self.assertEqual(response.data[0]['name'], data[0]['name'])
        self.assertEqual(response.data[1]['name'], data[1]['name'])
        self.assertEqual(response.data[2]['name'], data[2]['name'])

    def test_create_interface_802_1q_bulk(self):

        data = [
            {
                'virtual_machine': self.virtualmachine.pk,
                'name': 'Test Interface 4',
                'mode': IFACE_MODE_TAGGED,
                'untagged_vlan': self.vlan2.id,
                'tagged_vlans': [self.vlan1.id],
            },
            {
                'virtual_machine': self.virtualmachine.pk,
                'name': 'Test Interface 5',
                'mode': IFACE_MODE_TAGGED,
                'untagged_vlan': self.vlan2.id,
                'tagged_vlans': [self.vlan1.id],
            },
            {
                'virtual_machine': self.virtualmachine.pk,
                'name': 'Test Interface 6',
                'mode': IFACE_MODE_TAGGED,
                'untagged_vlan': self.vlan2.id,
                'tagged_vlans': [self.vlan1.id],
            },
        ]

        url = reverse('virtualization-api:interface-list')
        response = self.client.post(url, data, format='json', **self.header)

        self.assertHttpStatus(response, status.HTTP_201_CREATED)
        self.assertEqual(Interface.objects.count(), 6)
        for i in range(0, 3):
            self.assertEqual(response.data[i]['name'], data[i]['name'])
            self.assertEqual([v['id'] for v in response.data[i]['tagged_vlans']], data[i]['tagged_vlans'])
            self.assertEqual(response.data[i]['untagged_vlan']['id'], data[i]['untagged_vlan'])

    def test_update_interface(self):

        data = {
            'virtual_machine': self.virtualmachine.pk,
            'name': 'Test Interface X',
        }

        url = reverse('virtualization-api:interface-detail', kwargs={'pk': self.interface1.pk})
        response = self.client.put(url, data, format='json', **self.header)

        self.assertHttpStatus(response, status.HTTP_200_OK)
        self.assertEqual(Interface.objects.count(), 3)
        interface1 = Interface.objects.get(pk=response.data['id'])
        self.assertEqual(interface1.name, data['name'])

    def test_delete_interface(self):

        url = reverse('dcim-api:interface-detail', kwargs={'pk': self.interface1.pk})
        response = self.client.delete(url, **self.header)

        self.assertHttpStatus(response, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Interface.objects.count(), 2)
