import urllib.parse

from django.test import Client, TestCase
from django.urls import reverse

from circuits.models import Circuit, CircuitType, Provider
from utilities.testing import create_test_user


class ProviderTestCase(TestCase):

    def setUp(self):
        user = create_test_user(permissions=['circuits.view_provider'])
        self.client = Client()
        self.client.force_login(user)

        Provider.objects.bulk_create([
            Provider(name='Provider 1', slug='provider-1', asn=65001),
            Provider(name='Provider 2', slug='provider-2', asn=65002),
            Provider(name='Provider 3', slug='provider-3', asn=65003),
        ])

    def test_provider_list(self):

        url = reverse('circuits:provider_list')
        params = {
            "q": "test",
        }

        response = self.client.get('{}?{}'.format(url, urllib.parse.urlencode(params)))
        self.assertEqual(response.status_code, 200)

    def test_provider(self):

        provider = Provider.objects.first()
        response = self.client.get(provider.get_absolute_url())
        self.assertEqual(response.status_code, 200)


class CircuitTypeTestCase(TestCase):

    def setUp(self):
        user = create_test_user(permissions=['circuits.view_circuittype'])
        self.client = Client()
        self.client.force_login(user)

        CircuitType.objects.bulk_create([
            CircuitType(name='Circuit Type 1', slug='circuit-type-1'),
            CircuitType(name='Circuit Type 2', slug='circuit-type-2'),
            CircuitType(name='Circuit Type 3', slug='circuit-type-3'),
        ])

    def test_circuittype_list(self):

        url = reverse('circuits:circuittype_list')

        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)


class CircuitTestCase(TestCase):

    def setUp(self):
        user = create_test_user(permissions=['circuits.view_circuit'])
        self.client = Client()
        self.client.force_login(user)

        provider = Provider(name='Provider 1', slug='provider-1', asn=65001)
        provider.save()

        circuittype = CircuitType(name='Circuit Type 1', slug='circuit-type-1')
        circuittype.save()

        Circuit.objects.bulk_create([
            Circuit(cid='Circuit 1', provider=provider, type=circuittype),
            Circuit(cid='Circuit 2', provider=provider, type=circuittype),
            Circuit(cid='Circuit 3', provider=provider, type=circuittype),
        ])

    def test_circuit_list(self):

        url = reverse('circuits:circuit_list')
        params = {
            "provider": Provider.objects.first().slug,
            "type": CircuitType.objects.first().slug,
        }

        response = self.client.get('{}?{}'.format(url, urllib.parse.urlencode(params)))
        self.assertEqual(response.status_code, 200)

    def test_circuit(self):

        circuit = Circuit.objects.first()
        response = self.client.get(circuit.get_absolute_url())
        self.assertEqual(response.status_code, 200)
