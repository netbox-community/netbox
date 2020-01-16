import urllib.parse

from django.test import Client, TestCase
from django.urls import reverse

from utilities.testing import create_test_user
from virtualization.models import Cluster, ClusterGroup, ClusterType, VirtualMachine


class ClusterGroupTestCase(TestCase):

    def setUp(self):
        user = create_test_user(
            permissions=[
                'virtualization.view_clustergroup',
                'virtualization.add_clustergroup',
            ]
        )
        self.client = Client()
        self.client.force_login(user)

        ClusterGroup.objects.bulk_create([
            ClusterGroup(name='Cluster Group 1', slug='cluster-group-1'),
            ClusterGroup(name='Cluster Group 2', slug='cluster-group-2'),
            ClusterGroup(name='Cluster Group 3', slug='cluster-group-3'),
        ])

    def test_clustergroup_list(self):

        url = reverse('virtualization:clustergroup_list')

        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_clustergroup_import(self):

        csv_data = (
            "name,slug",
            "Cluster Group 4,cluster-group-4",
            "Cluster Group 5,cluster-group-5",
            "Cluster Group 6,cluster-group-6",
        )

        response = self.client.post(reverse('virtualization:clustergroup_import'), {'csv': '\n'.join(csv_data)})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(ClusterGroup.objects.count(), 6)


class ClusterTypeTestCase(TestCase):

    def setUp(self):
        user = create_test_user(
            permissions=[
                'virtualization.view_clustertype',
                'virtualization.add_clustertype',
            ]
        )
        self.client = Client()
        self.client.force_login(user)

        ClusterType.objects.bulk_create([
            ClusterType(name='Cluster Type 1', slug='cluster-type-1'),
            ClusterType(name='Cluster Type 2', slug='cluster-type-2'),
            ClusterType(name='Cluster Type 3', slug='cluster-type-3'),
        ])

    def test_clustertype_list(self):

        url = reverse('virtualization:clustertype_list')

        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_clustertype_import(self):

        csv_data = (
            "name,slug",
            "Cluster Type 4,cluster-type-4",
            "Cluster Type 5,cluster-type-5",
            "Cluster Type 6,cluster-type-6",
        )

        response = self.client.post(reverse('virtualization:clustertype_import'), {'csv': '\n'.join(csv_data)})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(ClusterType.objects.count(), 6)


class ClusterTestCase(TestCase):

    def setUp(self):
        user = create_test_user(
            permissions=[
                'virtualization.view_cluster',
                'virtualization.add_cluster',
            ]
        )
        self.client = Client()
        self.client.force_login(user)

        clustergroup = ClusterGroup(name='Cluster Group 1', slug='cluster-group-1')
        clustergroup.save()

        clustertype = ClusterType(name='Cluster Type 1', slug='cluster-type-1')
        clustertype.save()

        Cluster.objects.bulk_create([
            Cluster(name='Cluster 1', group=clustergroup, type=clustertype),
            Cluster(name='Cluster 2', group=clustergroup, type=clustertype),
            Cluster(name='Cluster 3', group=clustergroup, type=clustertype),
        ])

    def test_cluster_list(self):

        url = reverse('virtualization:cluster_list')
        params = {
            "group": ClusterGroup.objects.first().slug,
            "type": ClusterType.objects.first().slug,
        }

        response = self.client.get('{}?{}'.format(url, urllib.parse.urlencode(params)))
        self.assertEqual(response.status_code, 200)

    def test_cluster(self):

        cluster = Cluster.objects.first()
        response = self.client.get(cluster.get_absolute_url())
        self.assertEqual(response.status_code, 200)

    def test_cluster_import(self):

        csv_data = (
            "name,type",
            "Cluster 4,Cluster Type 1",
            "Cluster 5,Cluster Type 1",
            "Cluster 6,Cluster Type 1",
        )

        response = self.client.post(reverse('virtualization:cluster_import'), {'csv': '\n'.join(csv_data)})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Cluster.objects.count(), 6)


class VirtualMachineTestCase(TestCase):

    def setUp(self):
        user = create_test_user(
            permissions=[
                'virtualization.view_virtualmachine',
                'virtualization.add_virtualmachine',
            ]
        )
        self.client = Client()
        self.client.force_login(user)

        clustertype = ClusterType(name='Cluster Type 1', slug='cluster-type-1')
        clustertype.save()

        cluster = Cluster(name='Cluster 1', type=clustertype)
        cluster.save()

        VirtualMachine.objects.bulk_create([
            VirtualMachine(name='Virtual Machine 1', cluster=cluster),
            VirtualMachine(name='Virtual Machine 2', cluster=cluster),
            VirtualMachine(name='Virtual Machine 3', cluster=cluster),
        ])

    def test_virtualmachine_list(self):

        url = reverse('virtualization:virtualmachine_list')
        params = {
            "cluster_id": Cluster.objects.first().pk,
        }

        response = self.client.get('{}?{}'.format(url, urllib.parse.urlencode(params)))
        self.assertEqual(response.status_code, 200)

    def test_virtualmachine(self):

        virtualmachine = VirtualMachine.objects.first()
        response = self.client.get(virtualmachine.get_absolute_url())
        self.assertEqual(response.status_code, 200)

    def test_virtualmachine_import(self):

        csv_data = (
            "name,cluster",
            "Virtual Machine 4,Cluster 1",
            "Virtual Machine 5,Cluster 1",
            "Virtual Machine 6,Cluster 1",
        )

        response = self.client.post(reverse('virtualization:virtualmachine_import'), {'csv': '\n'.join(csv_data)})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(VirtualMachine.objects.count(), 6)
