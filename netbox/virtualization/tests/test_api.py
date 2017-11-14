from __future__ import unicode_literals

from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from users.models import Token
from utilities.tests import HttpStatusMixin
from virtualization.models import Cluster, ClusterGroup, ClusterType, VirtualMachine


class ClusterTypeTest(HttpStatusMixin, APITestCase):

    def setUp(self):

        user = User.objects.create(username='testuser', is_superuser=True)
        token = Token.objects.create(user=user)
        self.header = {'HTTP_AUTHORIZATION': 'Token {}'.format(token.key)}

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

    def test_create_clustertype(self):

        data = {
            'name': 'Test Cluster Type 4',
            'slug': 'test-cluster-type-4',
        }

        url = reverse('virtualization-api:clustertype-list')
        response = self.client.post(url, data, **self.header)

        self.assertHttpStatus(response, status.HTTP_201_CREATED)
        self.assertEqual(ClusterType.objects.count(), 4)
        clustertype4 = ClusterType.objects.get(pk=response.data['id'])
        self.assertEqual(clustertype4.name, data['name'])
        self.assertEqual(clustertype4.slug, data['slug'])

    def test_update_clustertype(self):

        data = {
            'name': 'Test Cluster Type X',
            'slug': 'test-cluster-type-x',
        }

        url = reverse('virtualization-api:clustertype-detail', kwargs={'pk': self.clustertype1.pk})
        response = self.client.put(url, data, **self.header)

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


class ClusterGroupTest(HttpStatusMixin, APITestCase):

    def setUp(self):

        user = User.objects.create(username='testuser', is_superuser=True)
        token = Token.objects.create(user=user)
        self.header = {'HTTP_AUTHORIZATION': 'Token {}'.format(token.key)}

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

    def test_create_clustergroup(self):

        data = {
            'name': 'Test Cluster Group 4',
            'slug': 'test-cluster-group-4',
        }

        url = reverse('virtualization-api:clustergroup-list')
        response = self.client.post(url, data, **self.header)

        self.assertHttpStatus(response, status.HTTP_201_CREATED)
        self.assertEqual(ClusterGroup.objects.count(), 4)
        clustergroup4 = ClusterGroup.objects.get(pk=response.data['id'])
        self.assertEqual(clustergroup4.name, data['name'])
        self.assertEqual(clustergroup4.slug, data['slug'])

    def test_update_clustergroup(self):

        data = {
            'name': 'Test Cluster Group X',
            'slug': 'test-cluster-group-x',
        }

        url = reverse('virtualization-api:clustergroup-detail', kwargs={'pk': self.clustergroup1.pk})
        response = self.client.put(url, data, **self.header)

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


class ClusterTest(HttpStatusMixin, APITestCase):

    def setUp(self):

        user = User.objects.create(username='testuser', is_superuser=True)
        token = Token.objects.create(user=user)
        self.header = {'HTTP_AUTHORIZATION': 'Token {}'.format(token.key)}

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

    def test_create_cluster(self):

        data = {
            'name': 'Test Cluster 4',
            'type': ClusterType.objects.first().pk,
            'group': ClusterGroup.objects.first().pk,
        }

        url = reverse('virtualization-api:cluster-list')
        response = self.client.post(url, data, **self.header)

        self.assertHttpStatus(response, status.HTTP_201_CREATED)
        self.assertEqual(Cluster.objects.count(), 4)
        cluster4 = Cluster.objects.get(pk=response.data['id'])
        self.assertEqual(cluster4.name, data['name'])
        self.assertEqual(cluster4.type.pk, data['type'])
        self.assertEqual(cluster4.group.pk, data['group'])

    def test_update_cluster(self):

        cluster_type2 = ClusterType.objects.create(name='Test Cluster Type 2', slug='test-cluster-type-2')
        cluster_group2 = ClusterGroup.objects.create(name='Test Cluster Group 2', slug='test-cluster-group-2')
        data = {
            'name': 'Test Cluster X',
            'type': cluster_type2.pk,
            'group': cluster_group2.pk,
        }

        url = reverse('virtualization-api:cluster-detail', kwargs={'pk': self.cluster1.pk})
        response = self.client.put(url, data, **self.header)

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


class VirtualMachineTest(HttpStatusMixin, APITestCase):

    def setUp(self):

        user = User.objects.create(username='testuser', is_superuser=True)
        token = Token.objects.create(user=user)
        self.header = {'HTTP_AUTHORIZATION': 'Token {}'.format(token.key)}

        cluster_type = ClusterType.objects.create(name='Test Cluster Type 1', slug='test-cluster-type-1')
        cluster_group = ClusterGroup.objects.create(name='Test Cluster Group 1', slug='test-cluster-group-1')
        cluster = Cluster.objects.create(name='Test Cluster 1', type=cluster_type, group=cluster_group)

        self.virtualmachine1 = VirtualMachine.objects.create(name='Test Virtual Machine 1', cluster=cluster)
        self.virtualmachine2 = VirtualMachine.objects.create(name='Test Virtual Machine 2', cluster=cluster)
        self.virtualmachine3 = VirtualMachine.objects.create(name='Test Virtual Machine 3', cluster=cluster)

    def test_get_virtualmachine(self):

        url = reverse('virtualization-api:virtualmachine-detail', kwargs={'pk': self.virtualmachine1.pk})
        response = self.client.get(url, **self.header)

        self.assertEqual(response.data['name'], self.virtualmachine1.name)

    def test_list_virtualmachines(self):

        url = reverse('virtualization-api:virtualmachine-list')
        response = self.client.get(url, **self.header)

        self.assertEqual(response.data['count'], 3)

    def test_create_virtualmachine(self):

        data = {
            'name': 'Test Virtual Machine 4',
            'cluster': Cluster.objects.first().pk,
        }

        url = reverse('virtualization-api:virtualmachine-list')
        response = self.client.post(url, data, **self.header)

        self.assertHttpStatus(response, status.HTTP_201_CREATED)
        self.assertEqual(VirtualMachine.objects.count(), 4)
        virtualmachine4 = VirtualMachine.objects.get(pk=response.data['id'])
        self.assertEqual(virtualmachine4.name, data['name'])
        self.assertEqual(virtualmachine4.cluster.pk, data['cluster'])

    def test_update_virtualmachine(self):

        cluster2 = Cluster.objects.create(
            name='Test Cluster 2',
            type=ClusterType.objects.first(),
            group=ClusterGroup.objects.first()
        )
        data = {
            'name': 'Test Virtual Machine X',
            'cluster': cluster2.pk,
        }

        url = reverse('virtualization-api:virtualmachine-detail', kwargs={'pk': self.virtualmachine1.pk})
        response = self.client.put(url, data, **self.header)

        self.assertHttpStatus(response, status.HTTP_200_OK)
        self.assertEqual(VirtualMachine.objects.count(), 3)
        virtualmachine1 = VirtualMachine.objects.get(pk=response.data['id'])
        self.assertEqual(virtualmachine1.name, data['name'])
        self.assertEqual(virtualmachine1.cluster.pk, data['cluster'])

    def test_delete_virtualmachine(self):

        url = reverse('virtualization-api:virtualmachine-detail', kwargs={'pk': self.virtualmachine1.pk})
        response = self.client.delete(url, **self.header)

        self.assertHttpStatus(response, status.HTTP_204_NO_CONTENT)
        self.assertEqual(VirtualMachine.objects.count(), 2)
