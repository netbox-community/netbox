from __future__ import unicode_literals

from django.urls import reverse
from rest_framework import status

from circuits.constants import CIRCUIT_STATUS_ACTIVE, TERM_SIDE_A, TERM_SIDE_Z
from circuits.models import Circuit, CircuitTermination, CircuitType, Provider
from dcim.models import Site
from extras.constants import GRAPH_TYPE_PROVIDER
from extras.models import Graph
from utilities.testing import APITestCase


class ProviderTest(APITestCase):

    def setUp(self):

        super(ProviderTest, self).setUp()

        self.provider1 = Provider.objects.create(name='Test Provider 1', slug='test-provider-1')
        self.provider2 = Provider.objects.create(name='Test Provider 2', slug='test-provider-2')
        self.provider3 = Provider.objects.create(name='Test Provider 3', slug='test-provider-3')

    def test_get_provider(self):

        url = reverse('circuits-api:provider-detail', kwargs={'pk': self.provider1.pk})
        response = self.client.get(url, **self.header)

        self.assertEqual(response.data['name'], self.provider1.name)

    def test_get_provider_graphs(self):

        self.graph1 = Graph.objects.create(
            type=GRAPH_TYPE_PROVIDER, name='Test Graph 1',
            source='http://example.com/graphs.py?provider={{ obj.slug }}&foo=1'
        )
        self.graph2 = Graph.objects.create(
            type=GRAPH_TYPE_PROVIDER, name='Test Graph 2',
            source='http://example.com/graphs.py?provider={{ obj.slug }}&foo=2'
        )
        self.graph3 = Graph.objects.create(
            type=GRAPH_TYPE_PROVIDER, name='Test Graph 3',
            source='http://example.com/graphs.py?provider={{ obj.slug }}&foo=3'
        )

        url = reverse('circuits-api:provider-graphs', kwargs={'pk': self.provider1.pk})
        response = self.client.get(url, **self.header)

        self.assertEqual(len(response.data), 3)
        self.assertEqual(response.data[0]['embed_url'], 'http://example.com/graphs.py?provider=test-provider-1&foo=1')

    def test_list_providers(self):

        url = reverse('circuits-api:provider-list')
        response = self.client.get(url, **self.header)

        self.assertEqual(response.data['count'], 3)

    def test_list_providers_brief(self):

        url = reverse('circuits-api:provider-list')
        response = self.client.get('{}?brief=1'.format(url), **self.header)

        self.assertEqual(
            sorted(response.data['results'][0]),
            ['id', 'name', 'slug', 'url']
        )

    def test_create_provider(self):

        data = {
            'name': 'Test Provider 4',
            'slug': 'test-provider-4',
        }

        url = reverse('circuits-api:provider-list')
        response = self.client.post(url, data, format='json', **self.header)

        self.assertHttpStatus(response, status.HTTP_201_CREATED)
        self.assertEqual(Provider.objects.count(), 4)
        provider4 = Provider.objects.get(pk=response.data['id'])
        self.assertEqual(provider4.name, data['name'])
        self.assertEqual(provider4.slug, data['slug'])

    def test_create_provider_bulk(self):

        data = [
            {
                'name': 'Test Provider 4',
                'slug': 'test-provider-4',
            },
            {
                'name': 'Test Provider 5',
                'slug': 'test-provider-5',
            },
            {
                'name': 'Test Provider 6',
                'slug': 'test-provider-6',
            },
        ]

        url = reverse('circuits-api:provider-list')
        response = self.client.post(url, data, format='json', **self.header)

        self.assertHttpStatus(response, status.HTTP_201_CREATED)
        self.assertEqual(Provider.objects.count(), 6)
        self.assertEqual(response.data[0]['name'], data[0]['name'])
        self.assertEqual(response.data[1]['name'], data[1]['name'])
        self.assertEqual(response.data[2]['name'], data[2]['name'])

    def test_update_provider(self):

        data = {
            'name': 'Test Provider X',
            'slug': 'test-provider-x',
        }

        url = reverse('circuits-api:provider-detail', kwargs={'pk': self.provider1.pk})
        response = self.client.put(url, data, format='json', **self.header)

        self.assertHttpStatus(response, status.HTTP_200_OK)
        self.assertEqual(Provider.objects.count(), 3)
        provider1 = Provider.objects.get(pk=response.data['id'])
        self.assertEqual(provider1.name, data['name'])
        self.assertEqual(provider1.slug, data['slug'])

    def test_delete_provider(self):

        url = reverse('circuits-api:provider-detail', kwargs={'pk': self.provider1.pk})
        response = self.client.delete(url, **self.header)

        self.assertHttpStatus(response, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Provider.objects.count(), 2)


class CircuitTypeTest(APITestCase):

    def setUp(self):

        super(CircuitTypeTest, self).setUp()

        self.circuittype1 = CircuitType.objects.create(name='Test Circuit Type 1', slug='test-circuit-type-1')
        self.circuittype2 = CircuitType.objects.create(name='Test Circuit Type 2', slug='test-circuit-type-2')
        self.circuittype3 = CircuitType.objects.create(name='Test Circuit Type 3', slug='test-circuit-type-3')

    def test_get_circuittype(self):

        url = reverse('circuits-api:circuittype-detail', kwargs={'pk': self.circuittype1.pk})
        response = self.client.get(url, **self.header)

        self.assertEqual(response.data['name'], self.circuittype1.name)

    def test_list_circuittypes(self):

        url = reverse('circuits-api:circuittype-list')
        response = self.client.get(url, **self.header)

        self.assertEqual(response.data['count'], 3)

    def test_list_circuittypes_brief(self):

        url = reverse('circuits-api:circuittype-list')
        response = self.client.get('{}?brief=1'.format(url), **self.header)

        self.assertEqual(
            sorted(response.data['results'][0]),
            ['id', 'name', 'slug', 'url']
        )

    def test_create_circuittype(self):

        data = {
            'name': 'Test Circuit Type 4',
            'slug': 'test-circuit-type-4',
        }

        url = reverse('circuits-api:circuittype-list')
        response = self.client.post(url, data, format='json', **self.header)

        self.assertHttpStatus(response, status.HTTP_201_CREATED)
        self.assertEqual(CircuitType.objects.count(), 4)
        circuittype4 = CircuitType.objects.get(pk=response.data['id'])
        self.assertEqual(circuittype4.name, data['name'])
        self.assertEqual(circuittype4.slug, data['slug'])

    def test_update_circuittype(self):

        data = {
            'name': 'Test Circuit Type X',
            'slug': 'test-circuit-type-x',
        }

        url = reverse('circuits-api:circuittype-detail', kwargs={'pk': self.circuittype1.pk})
        response = self.client.put(url, data, format='json', **self.header)

        self.assertHttpStatus(response, status.HTTP_200_OK)
        self.assertEqual(CircuitType.objects.count(), 3)
        circuittype1 = CircuitType.objects.get(pk=response.data['id'])
        self.assertEqual(circuittype1.name, data['name'])
        self.assertEqual(circuittype1.slug, data['slug'])

    def test_delete_circuittype(self):

        url = reverse('circuits-api:circuittype-detail', kwargs={'pk': self.circuittype1.pk})
        response = self.client.delete(url, **self.header)

        self.assertHttpStatus(response, status.HTTP_204_NO_CONTENT)
        self.assertEqual(CircuitType.objects.count(), 2)


class CircuitTest(APITestCase):

    def setUp(self):

        super(CircuitTest, self).setUp()

        self.provider1 = Provider.objects.create(name='Test Provider 1', slug='test-provider-1')
        self.provider2 = Provider.objects.create(name='Test Provider 2', slug='test-provider-2')
        self.circuittype1 = CircuitType.objects.create(name='Test Circuit Type 1', slug='test-circuit-type-1')
        self.circuittype2 = CircuitType.objects.create(name='Test Circuit Type 2', slug='test-circuit-type-2')
        self.circuit1 = Circuit.objects.create(cid='TEST0001', provider=self.provider1, type=self.circuittype1)
        self.circuit2 = Circuit.objects.create(cid='TEST0002', provider=self.provider1, type=self.circuittype1)
        self.circuit3 = Circuit.objects.create(cid='TEST0003', provider=self.provider1, type=self.circuittype1)

    def test_get_circuit(self):

        url = reverse('circuits-api:circuit-detail', kwargs={'pk': self.circuit1.pk})
        response = self.client.get(url, **self.header)

        self.assertEqual(response.data['cid'], self.circuit1.cid)

    def test_list_circuits(self):

        url = reverse('circuits-api:circuit-list')
        response = self.client.get(url, **self.header)

        self.assertEqual(response.data['count'], 3)

    def test_list_circuits_brief(self):

        url = reverse('circuits-api:circuit-list')
        response = self.client.get('{}?brief=1'.format(url), **self.header)

        self.assertEqual(
            sorted(response.data['results'][0]),
            ['cid', 'id', 'url']
        )

    def test_create_circuit(self):

        data = {
            'cid': 'TEST0004',
            'provider': self.provider1.pk,
            'type': self.circuittype1.pk,
            'status': CIRCUIT_STATUS_ACTIVE,
        }

        url = reverse('circuits-api:circuit-list')
        response = self.client.post(url, data, format='json', **self.header)

        self.assertHttpStatus(response, status.HTTP_201_CREATED)
        self.assertEqual(Circuit.objects.count(), 4)
        circuit4 = Circuit.objects.get(pk=response.data['id'])
        self.assertEqual(circuit4.cid, data['cid'])
        self.assertEqual(circuit4.provider_id, data['provider'])
        self.assertEqual(circuit4.type_id, data['type'])

    def test_create_circuit_bulk(self):

        data = [
            {
                'cid': 'TEST0004',
                'provider': self.provider1.pk,
                'type': self.circuittype1.pk,
                'status': CIRCUIT_STATUS_ACTIVE,
            },
            {
                'cid': 'TEST0005',
                'provider': self.provider1.pk,
                'type': self.circuittype1.pk,
                'status': CIRCUIT_STATUS_ACTIVE,
            },
            {
                'cid': 'TEST0006',
                'provider': self.provider1.pk,
                'type': self.circuittype1.pk,
                'status': CIRCUIT_STATUS_ACTIVE,
            },
        ]

        url = reverse('circuits-api:circuit-list')
        response = self.client.post(url, data, format='json', **self.header)

        self.assertHttpStatus(response, status.HTTP_201_CREATED)
        self.assertEqual(Circuit.objects.count(), 6)
        self.assertEqual(response.data[0]['cid'], data[0]['cid'])
        self.assertEqual(response.data[1]['cid'], data[1]['cid'])
        self.assertEqual(response.data[2]['cid'], data[2]['cid'])

    def test_update_circuit(self):

        data = {
            'cid': 'TEST000X',
            'provider': self.provider2.pk,
            'type': self.circuittype2.pk,
        }

        url = reverse('circuits-api:circuit-detail', kwargs={'pk': self.circuit1.pk})
        response = self.client.put(url, data, format='json', **self.header)

        self.assertHttpStatus(response, status.HTTP_200_OK)
        self.assertEqual(Circuit.objects.count(), 3)
        circuit1 = Circuit.objects.get(pk=response.data['id'])
        self.assertEqual(circuit1.cid, data['cid'])
        self.assertEqual(circuit1.provider_id, data['provider'])
        self.assertEqual(circuit1.type_id, data['type'])

    def test_delete_circuit(self):

        url = reverse('circuits-api:circuit-detail', kwargs={'pk': self.circuit1.pk})
        response = self.client.delete(url, **self.header)

        self.assertHttpStatus(response, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Circuit.objects.count(), 2)


class CircuitTerminationTest(APITestCase):

    def setUp(self):

        super(CircuitTerminationTest, self).setUp()

        provider = Provider.objects.create(name='Test Provider', slug='test-provider')
        circuittype = CircuitType.objects.create(name='Test Circuit Type', slug='test-circuit-type')
        self.circuit1 = Circuit.objects.create(cid='TEST0001', provider=provider, type=circuittype)
        self.circuit2 = Circuit.objects.create(cid='TEST0002', provider=provider, type=circuittype)
        self.circuit3 = Circuit.objects.create(cid='TEST0003', provider=provider, type=circuittype)
        self.site1 = Site.objects.create(name='Test Site 1', slug='test-site-1')
        self.site2 = Site.objects.create(name='Test Site 2', slug='test-site-2')
        self.circuittermination1 = CircuitTermination.objects.create(
            circuit=self.circuit1, term_side=TERM_SIDE_A, site=self.site1, port_speed=1000000
        )
        self.circuittermination2 = CircuitTermination.objects.create(
            circuit=self.circuit2, term_side=TERM_SIDE_A, site=self.site1, port_speed=1000000
        )
        self.circuittermination3 = CircuitTermination.objects.create(
            circuit=self.circuit3, term_side=TERM_SIDE_A, site=self.site1, port_speed=1000000
        )

    def test_get_circuittermination(self):

        url = reverse('circuits-api:circuittermination-detail', kwargs={'pk': self.circuittermination1.pk})
        response = self.client.get(url, **self.header)

        self.assertEqual(response.data['id'], self.circuittermination1.pk)

    def test_list_circuitterminations(self):

        url = reverse('circuits-api:circuittermination-list')
        response = self.client.get(url, **self.header)

        self.assertEqual(response.data['count'], 3)

    def test_create_circuittermination(self):

        data = {
            'circuit': self.circuit1.pk,
            'term_side': TERM_SIDE_Z,
            'site': self.site2.pk,
            'port_speed': 1000000,
        }

        url = reverse('circuits-api:circuittermination-list')
        response = self.client.post(url, data, format='json', **self.header)

        self.assertHttpStatus(response, status.HTTP_201_CREATED)
        self.assertEqual(CircuitTermination.objects.count(), 4)
        circuittermination4 = CircuitTermination.objects.get(pk=response.data['id'])
        self.assertEqual(circuittermination4.circuit_id, data['circuit'])
        self.assertEqual(circuittermination4.term_side, data['term_side'])
        self.assertEqual(circuittermination4.site_id, data['site'])
        self.assertEqual(circuittermination4.port_speed, data['port_speed'])

    def test_update_circuittermination(self):

        data = {
            'circuit': self.circuit1.pk,
            'term_side': TERM_SIDE_Z,
            'site': self.site2.pk,
            'port_speed': 1000000,
        }

        url = reverse('circuits-api:circuittermination-detail', kwargs={'pk': self.circuittermination1.pk})
        response = self.client.put(url, data, format='json', **self.header)

        self.assertHttpStatus(response, status.HTTP_200_OK)
        self.assertEqual(CircuitTermination.objects.count(), 3)
        circuittermination1 = CircuitTermination.objects.get(pk=response.data['id'])
        self.assertEqual(circuittermination1.circuit_id, data['circuit'])
        self.assertEqual(circuittermination1.term_side, data['term_side'])
        self.assertEqual(circuittermination1.site_id, data['site'])
        self.assertEqual(circuittermination1.port_speed, data['port_speed'])

    def test_delete_circuittermination(self):

        url = reverse('circuits-api:circuittermination-detail', kwargs={'pk': self.circuittermination1.pk})
        response = self.client.delete(url, **self.header)

        self.assertHttpStatus(response, status.HTTP_204_NO_CONTENT)
        self.assertEqual(CircuitTermination.objects.count(), 2)
