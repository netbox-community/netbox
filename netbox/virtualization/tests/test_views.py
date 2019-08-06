import urllib.parse

from django.test import Client, TestCase
from django.urls import reverse

from utilities.testing import create_test_user
from virtualization.models import Cluster, ClusterGroup, ClusterType, VirtualMachine


class ClusterGroupTestCase(TestCase):

    def setUp(self):
        user = create_test_user(permissions=['virtualization.view_clustergroup'])
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


class ClusterTypeTestCase(TestCase):

    def setUp(self):
        user = create_test_user(permissions=['virtualization.view_clustertype'])
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


class ClusterTestCase(TestCase):

    def setUp(self):
        user = create_test_user(permissions=['virtualization.view_cluster'])
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


class VirtualMachineTestCase(TestCase):

    def setUp(self):
        user = create_test_user(permissions=['virtualization.view_virtualmachine'])
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
