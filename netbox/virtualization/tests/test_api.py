from django.urls import reverse
from rest_framework import status

from dcim.choices import InterfaceModeChoices
from ipam.models import VLAN
from utilities.testing import APITestCase, APIViewTestCases
from virtualization.models import Cluster, ClusterGroup, ClusterType, VirtualMachine, VMInterface


class AppTest(APITestCase):

    def test_root(self):

        url = reverse('virtualization-api:api-root')
        response = self.client.get('{}?format=api'.format(url), **self.header)

        self.assertEqual(response.status_code, 200)


class ClusterTypeTest(APIViewTestCases.APIViewTestCase):
    model = ClusterType
    brief_fields = ['cluster_count', 'id', 'name', 'slug', 'url']
    create_data = [
        {
            'name': 'Cluster Type 4',
            'slug': 'cluster-type-4',
        },
        {
            'name': 'Cluster Type 5',
            'slug': 'cluster-type-5',
        },
        {
            'name': 'Cluster Type 6',
            'slug': 'cluster-type-6',
        },
    ]

    @classmethod
    def setUpTestData(cls):

        cluster_types = (
            ClusterType(name='Cluster Type 1', slug='cluster-type-1'),
            ClusterType(name='Cluster Type 2', slug='cluster-type-2'),
            ClusterType(name='Cluster Type 3', slug='cluster-type-3'),
        )
        ClusterType.objects.bulk_create(cluster_types)


class ClusterGroupTest(APIViewTestCases.APIViewTestCase):
    model = ClusterGroup
    brief_fields = ['cluster_count', 'id', 'name', 'slug', 'url']
    create_data = [
        {
            'name': 'Cluster Group 4',
            'slug': 'cluster-type-4',
        },
        {
            'name': 'Cluster Group 5',
            'slug': 'cluster-type-5',
        },
        {
            'name': 'Cluster Group 6',
            'slug': 'cluster-type-6',
        },
    ]

    @classmethod
    def setUpTestData(cls):

        cluster_Groups = (
            ClusterGroup(name='Cluster Group 1', slug='cluster-type-1'),
            ClusterGroup(name='Cluster Group 2', slug='cluster-type-2'),
            ClusterGroup(name='Cluster Group 3', slug='cluster-type-3'),
        )
        ClusterGroup.objects.bulk_create(cluster_Groups)


class ClusterTest(APIViewTestCases.APIViewTestCase):
    model = Cluster
    brief_fields = ['id', 'name', 'url', 'virtualmachine_count']

    @classmethod
    def setUpTestData(cls):

        cluster_types = (
            ClusterType(name='Cluster Type 1', slug='cluster-type-1'),
            ClusterType(name='Cluster Type 2', slug='cluster-type-2'),
        )
        ClusterType.objects.bulk_create(cluster_types)

        cluster_groups = (
            ClusterGroup(name='Cluster Group 1', slug='cluster-group-1'),
            ClusterGroup(name='Cluster Group 2', slug='cluster-group-2'),
        )
        ClusterGroup.objects.bulk_create(cluster_groups)

        clusters = (
            Cluster(name='Cluster 1', type=cluster_types[0], group=cluster_groups[0]),
            Cluster(name='Cluster 2', type=cluster_types[0], group=cluster_groups[0]),
            Cluster(name='Cluster 3', type=cluster_types[0], group=cluster_groups[0]),
        )
        Cluster.objects.bulk_create(clusters)

        cls.create_data = [
            {
                'name': 'Cluster 4',
                'type': cluster_types[1].pk,
                'group': cluster_groups[1].pk,
            },
            {
                'name': 'Cluster 5',
                'type': cluster_types[1].pk,
                'group': cluster_groups[1].pk,
            },
            {
                'name': 'Cluster 6',
                'type': cluster_types[1].pk,
                'group': cluster_groups[1].pk,
            },
        ]


class VirtualMachineTest(APIViewTestCases.APIViewTestCase):
    model = VirtualMachine
    brief_fields = ['id', 'name', 'url']

    @classmethod
    def setUpTestData(cls):
        clustertype = ClusterType.objects.create(name='Cluster Type 1', slug='cluster-type-1')
        clustergroup = ClusterGroup.objects.create(name='Cluster Group 1', slug='cluster-group-1')

        clusters = (
            Cluster(name='Cluster 1', type=clustertype, group=clustergroup),
            Cluster(name='Cluster 2', type=clustertype, group=clustergroup),
        )
        Cluster.objects.bulk_create(clusters)

        virtual_machines = (
            VirtualMachine(name='Virtual Machine 1', cluster=clusters[0], local_context_data={'A': 1}),
            VirtualMachine(name='Virtual Machine 2', cluster=clusters[0], local_context_data={'B': 2}),
            VirtualMachine(name='Virtual Machine 3', cluster=clusters[0], local_context_data={'C': 3}),
        )
        VirtualMachine.objects.bulk_create(virtual_machines)

        cls.create_data = [
            {
                'name': 'Virtual Machine 4',
                'cluster': clusters[1].pk,
            },
            {
                'name': 'Virtual Machine 5',
                'cluster': clusters[1].pk,
            },
            {
                'name': 'Virtual Machine 6',
                'cluster': clusters[1].pk,
            },
        ]

    def test_config_context_included_by_default_in_list_view(self):
        """
        Check that config context data is included by default in the virtual machines list.
        """
        virtualmachine = VirtualMachine.objects.first()
        url = '{}?id={}'.format(reverse('virtualization-api:virtualmachine-list'), virtualmachine.pk)
        self.add_permissions('virtualization.view_virtualmachine')

        response = self.client.get(url, **self.header)
        self.assertEqual(response.data['results'][0].get('config_context', {}).get('A'), 1)

    def test_config_context_excluded(self):
        """
        Check that config context data can be excluded by passing ?exclude=config_context.
        """
        url = reverse('virtualization-api:virtualmachine-list') + '?exclude=config_context'
        self.add_permissions('virtualization.view_virtualmachine')

        response = self.client.get(url, **self.header)
        self.assertFalse('config_context' in response.data['results'][0])

    def test_unique_name_per_cluster_constraint(self):
        """
        Check that creating a virtual machine with a duplicate name fails.
        """
        data = {
            'name': 'Virtual Machine 1',
            'cluster': Cluster.objects.first().pk,
        }
        url = reverse('virtualization-api:virtualmachine-list')
        self.add_permissions('virtualization.add_virtualmachine')

        response = self.client.post(url, data, format='json', **self.header)
        self.assertHttpStatus(response, status.HTTP_400_BAD_REQUEST)


# TODO: Standardize InterfaceTest (pending #4721)
class InterfaceTest(APITestCase):

    def setUp(self):

        super().setUp()

        clustertype = ClusterType.objects.create(name='Test Cluster Type 1', slug='test-cluster-type-1')
        cluster = Cluster.objects.create(name='Test Cluster 1', type=clustertype)
        self.virtualmachine = VirtualMachine.objects.create(cluster=cluster, name='Test VM 1')
        self.interface1 = VMInterface.objects.create(
            virtual_machine=self.virtualmachine,
            name='Test Interface 1'
        )
        self.interface2 = VMInterface.objects.create(
            virtual_machine=self.virtualmachine,
            name='Test Interface 2'
        )
        self.interface3 = VMInterface.objects.create(
            virtual_machine=self.virtualmachine,
            name='Test Interface 3'
        )

        self.vlan1 = VLAN.objects.create(name="Test VLAN 1", vid=1)
        self.vlan2 = VLAN.objects.create(name="Test VLAN 2", vid=2)
        self.vlan3 = VLAN.objects.create(name="Test VLAN 3", vid=3)

    def test_get_interface(self):
        url = reverse('virtualization-api:interface-detail', kwargs={'pk': self.interface1.pk})
        self.add_permissions('virtualization.view_interface')

        response = self.client.get(url, **self.header)
        self.assertEqual(response.data['name'], self.interface1.name)

    def test_list_interfaces(self):
        url = reverse('virtualization-api:interface-list')
        self.add_permissions('virtualization.view_interface')

        response = self.client.get(url, **self.header)
        self.assertEqual(response.data['count'], 3)

    def test_list_interfaces_brief(self):
        url = reverse('virtualization-api:interface-list')
        self.add_permissions('virtualization.view_interface')

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
        self.add_permissions('virtualization.add_interface')

        response = self.client.post(url, data, format='json', **self.header)
        self.assertHttpStatus(response, status.HTTP_201_CREATED)
        self.assertEqual(VMInterface.objects.count(), 4)
        interface4 = VMInterface.objects.get(pk=response.data['id'])
        self.assertEqual(interface4.virtual_machine_id, data['virtual_machine'])
        self.assertEqual(interface4.name, data['name'])

    def test_create_interface_with_802_1q(self):
        data = {
            'virtual_machine': self.virtualmachine.pk,
            'name': 'Test Interface 4',
            'mode': InterfaceModeChoices.MODE_TAGGED,
            'untagged_vlan': self.vlan3.id,
            'tagged_vlans': [self.vlan1.id, self.vlan2.id],
        }
        url = reverse('virtualization-api:interface-list')
        self.add_permissions('virtualization.add_interface')

        response = self.client.post(url, data, format='json', **self.header)
        self.assertHttpStatus(response, status.HTTP_201_CREATED)
        self.assertEqual(VMInterface.objects.count(), 4)
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
        self.add_permissions('virtualization.add_interface')

        response = self.client.post(url, data, format='json', **self.header)
        self.assertHttpStatus(response, status.HTTP_201_CREATED)
        self.assertEqual(VMInterface.objects.count(), 6)
        self.assertEqual(response.data[0]['name'], data[0]['name'])
        self.assertEqual(response.data[1]['name'], data[1]['name'])
        self.assertEqual(response.data[2]['name'], data[2]['name'])

    def test_create_interface_802_1q_bulk(self):
        data = [
            {
                'virtual_machine': self.virtualmachine.pk,
                'name': 'Test Interface 4',
                'mode': InterfaceModeChoices.MODE_TAGGED,
                'untagged_vlan': self.vlan2.id,
                'tagged_vlans': [self.vlan1.id],
            },
            {
                'virtual_machine': self.virtualmachine.pk,
                'name': 'Test Interface 5',
                'mode': InterfaceModeChoices.MODE_TAGGED,
                'untagged_vlan': self.vlan2.id,
                'tagged_vlans': [self.vlan1.id],
            },
            {
                'virtual_machine': self.virtualmachine.pk,
                'name': 'Test Interface 6',
                'mode': InterfaceModeChoices.MODE_TAGGED,
                'untagged_vlan': self.vlan2.id,
                'tagged_vlans': [self.vlan1.id],
            },
        ]
        url = reverse('virtualization-api:interface-list')
        self.add_permissions('virtualization.add_interface')

        response = self.client.post(url, data, format='json', **self.header)
        self.assertHttpStatus(response, status.HTTP_201_CREATED)
        self.assertEqual(VMInterface.objects.count(), 6)
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
        self.add_permissions('virtualization.change_interface')

        response = self.client.put(url, data, format='json', **self.header)
        self.assertHttpStatus(response, status.HTTP_200_OK)
        self.assertEqual(VMInterface.objects.count(), 3)
        interface1 = VMInterface.objects.get(pk=response.data['id'])
        self.assertEqual(interface1.name, data['name'])

    def test_delete_interface(self):
        url = reverse('virtualization-api:interface-detail', kwargs={'pk': self.interface1.pk})
        self.add_permissions('virtualization.delete_interface')

        response = self.client.delete(url, **self.header)
        self.assertHttpStatus(response, status.HTTP_204_NO_CONTENT)
        self.assertEqual(VMInterface.objects.count(), 2)
