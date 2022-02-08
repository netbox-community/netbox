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
    brief_fields = ['cluster_count', 'display', 'id', 'name', 'slug', 'url']
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
    bulk_update_data = {
        'description': 'New description',
    }

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
    brief_fields = ['cluster_count', 'display', 'id', 'name', 'slug', 'url']
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
    bulk_update_data = {
        'description': 'New description',
    }

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
    brief_fields = ['display', 'id', 'name', 'url', 'virtualmachine_count']
    bulk_update_data = {
        'comments': 'New comment',
    }

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
    brief_fields = ['display', 'id', 'name', 'url']
    bulk_update_data = {
        'status': 'staged',
    }

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


class VMInterfaceTest(APIViewTestCases.APIViewTestCase):
    model = VMInterface
    brief_fields = ['display', 'id', 'name', 'url', 'virtual_machine']
    bulk_update_data = {
        'description': 'New description',
    }

    @classmethod
    def setUpTestData(cls):

        clustertype = ClusterType.objects.create(name='Test Cluster Type 1', slug='test-cluster-type-1')
        cluster = Cluster.objects.create(name='Test Cluster 1', type=clustertype)
        virtualmachine = VirtualMachine.objects.create(cluster=cluster, name='Test VM 1')

        interfaces = (
            VMInterface(virtual_machine=virtualmachine, name='Interface 1'),
            VMInterface(virtual_machine=virtualmachine, name='Interface 2'),
            VMInterface(virtual_machine=virtualmachine, name='Interface 3'),
        )
        VMInterface.objects.bulk_create(interfaces)

        vlans = (
            VLAN(name='VLAN 1', vid=1),
            VLAN(name='VLAN 2', vid=2),
            VLAN(name='VLAN 3', vid=3),
        )
        VLAN.objects.bulk_create(vlans)

        cls.create_data = [
            {
                'virtual_machine': virtualmachine.pk,
                'name': 'Interface 4',
                'mode': InterfaceModeChoices.MODE_TAGGED,
                'tagged_vlans': [vlans[0].pk, vlans[1].pk],
                'untagged_vlan': vlans[2].pk,
            },
            {
                'virtual_machine': virtualmachine.pk,
                'name': 'Interface 5',
                'mode': InterfaceModeChoices.MODE_TAGGED,
                'tagged_vlans': [vlans[0].pk, vlans[1].pk],
                'untagged_vlan': vlans[2].pk,
            },
            {
                'virtual_machine': virtualmachine.pk,
                'name': 'Interface 6',
                'parent': interfaces[0].pk,
                'mode': InterfaceModeChoices.MODE_TAGGED,
                'tagged_vlans': [vlans[0].pk, vlans[1].pk],
                'untagged_vlan': vlans[2].pk,
            },
        ]
