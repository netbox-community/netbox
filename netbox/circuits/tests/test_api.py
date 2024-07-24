from django.urls import reverse

from circuits.choices import *
from circuits.models import *
from dcim.models import Site
from ipam.models import ASN, RIR
from utilities.testing import APITestCase, APIViewTestCases


class AppTest(APITestCase):

    def test_root(self):
        url = reverse('circuits-api:api-root')
        response = self.client.get('{}?format=api'.format(url), **self.header)

        self.assertEqual(response.status_code, 200)


class ProviderTest(APIViewTestCases.APIViewTestCase):
    model = Provider
    brief_fields = ['circuit_count', 'description', 'display', 'id', 'name', 'slug', 'url']
    bulk_update_data = {
        'comments': 'New comments',
    }

    @classmethod
    def setUpTestData(cls):

        rir = RIR.objects.create(name='RFC 6996', is_private=True)
        asns = [
            ASN(asn=65000 + i, rir=rir) for i in range(8)
        ]
        ASN.objects.bulk_create(asns)

        providers = (
            Provider(name='Provider 1', slug='provider-1'),
            Provider(name='Provider 2', slug='provider-2'),
            Provider(name='Provider 3', slug='provider-3'),
        )
        Provider.objects.bulk_create(providers)

        cls.create_data = [
            {
                'name': 'Provider 4',
                'slug': 'provider-4',
                'asns': [asns[0].pk, asns[1].pk],
            },
            {
                'name': 'Provider 5',
                'slug': 'provider-5',
                'asns': [asns[2].pk, asns[3].pk],
            },
            {
                'name': 'Provider 6',
                'slug': 'provider-6',
                'asns': [asns[4].pk, asns[5].pk],
            },
        ]


class CircuitTypeTest(APIViewTestCases.APIViewTestCase):
    model = CircuitType
    brief_fields = ['circuit_count', 'description', 'display', 'id', 'name', 'slug', 'url']
    create_data = (
        {
            'name': 'Circuit Type 4',
            'slug': 'circuit-type-4',
        },
        {
            'name': 'Circuit Type 5',
            'slug': 'circuit-type-5',
        },
        {
            'name': 'Circuit Type 6',
            'slug': 'circuit-type-6',
        },
    )
    bulk_update_data = {
        'description': 'New description',
    }

    @classmethod
    def setUpTestData(cls):

        circuit_types = (
            CircuitType(name='Circuit Type 1', slug='circuit-type-1'),
            CircuitType(name='Circuit Type 2', slug='circuit-type-2'),
            CircuitType(name='Circuit Type 3', slug='circuit-type-3'),
        )
        CircuitType.objects.bulk_create(circuit_types)


class CircuitTest(APIViewTestCases.APIViewTestCase):
    model = Circuit
    brief_fields = ['cid', 'description', 'display', 'id', 'url']
    bulk_update_data = {
        'status': 'planned',
    }

    @classmethod
    def setUpTestData(cls):

        providers = (
            Provider(name='Provider 1', slug='provider-1'),
            Provider(name='Provider 2', slug='provider-2'),
        )
        Provider.objects.bulk_create(providers)

        provider_accounts = (
            ProviderAccount(name='Provider Account 1', provider=providers[0], account='1234'),
            ProviderAccount(name='Provider Account 2', provider=providers[1], account='2345'),
        )
        ProviderAccount.objects.bulk_create(provider_accounts)

        circuit_types = (
            CircuitType(name='Circuit Type 1', slug='circuit-type-1'),
            CircuitType(name='Circuit Type 2', slug='circuit-type-2'),
        )
        CircuitType.objects.bulk_create(circuit_types)

        circuits = (
            Circuit(cid='Circuit 1', provider=providers[0], provider_account=provider_accounts[0], type=circuit_types[0]),
            Circuit(cid='Circuit 2', provider=providers[0], provider_account=provider_accounts[0], type=circuit_types[0]),
            Circuit(cid='Circuit 3', provider=providers[0], provider_account=provider_accounts[0], type=circuit_types[0]),
        )
        Circuit.objects.bulk_create(circuits)

        cls.create_data = [
            {
                'cid': 'Circuit 4',
                'provider': providers[1].pk,
                'provider_account': provider_accounts[1].pk,
                'type': circuit_types[1].pk,
            },
            {
                'cid': 'Circuit 5',
                'provider': providers[1].pk,
                'provider_account': provider_accounts[1].pk,
                'type': circuit_types[1].pk,
            },
            {
                'cid': 'Circuit 6',
                'provider': providers[1].pk,
                # Omit provider account to test uniqueness constraint
                'type': circuit_types[1].pk,
            },
        ]


class CircuitTerminationTest(APIViewTestCases.APIViewTestCase):
    model = CircuitTermination
    brief_fields = ['_occupied', 'cable', 'circuit', 'description', 'display', 'id', 'term_side', 'url']

    @classmethod
    def setUpTestData(cls):
        SIDE_A = CircuitTerminationSideChoices.SIDE_A
        SIDE_Z = CircuitTerminationSideChoices.SIDE_Z

        provider = Provider.objects.create(name='Provider 1', slug='provider-1')
        circuit_type = CircuitType.objects.create(name='Circuit Type 1', slug='circuit-type-1')

        sites = (
            Site(name='Site 1', slug='site-1'),
            Site(name='Site 2', slug='site-2'),
        )
        Site.objects.bulk_create(sites)

        provider_networks = (
            ProviderNetwork(provider=provider, name='Provider Network 1'),
            ProviderNetwork(provider=provider, name='Provider Network 2'),
        )
        ProviderNetwork.objects.bulk_create(provider_networks)

        circuits = (
            Circuit(cid='Circuit 1', provider=provider, type=circuit_type),
            Circuit(cid='Circuit 2', provider=provider, type=circuit_type),
            Circuit(cid='Circuit 3', provider=provider, type=circuit_type),
        )
        Circuit.objects.bulk_create(circuits)

        circuit_terminations = (
            CircuitTermination(circuit=circuits[0], term_side=SIDE_A, site=sites[0]),
            CircuitTermination(circuit=circuits[0], term_side=SIDE_Z, provider_network=provider_networks[0]),
            CircuitTermination(circuit=circuits[1], term_side=SIDE_A, site=sites[1]),
            CircuitTermination(circuit=circuits[1], term_side=SIDE_Z, provider_network=provider_networks[1]),
        )
        CircuitTermination.objects.bulk_create(circuit_terminations)

        cls.create_data = [
            {
                'circuit': circuits[2].pk,
                'term_side': SIDE_A,
                'site': sites[0].pk,
                'port_speed': 200000,
            },
            {
                'circuit': circuits[2].pk,
                'term_side': SIDE_Z,
                'provider_network': provider_networks[0].pk,
                'port_speed': 200000,
            },
        ]

        cls.bulk_update_data = {
            'port_speed': 123456
        }


class CircuitGroupTest(APIViewTestCases.APIViewTestCase):
    model = CircuitGroup
    brief_fields = ['display', 'id', 'name', 'url']
    bulk_update_data = {
        'description': 'New description',
    }

    @classmethod
    def setUpTestData(cls):
        circuit_groups = (
            CircuitGroup(name="Circuit Group 1", slug='circuit-group-1'),
            CircuitGroup(name="Circuit Group 2", slug='circuit-group-2'),
            CircuitGroup(name="Circuit Group 3", slug='circuit-group-3'),
        )
        CircuitGroup.objects.bulk_create(circuit_groups)

        cls.create_data = [
            {
                'name': 'Circuit Group 4',
                'slug': 'circuit-group-4',
            },
            {
                'name': 'Circuit Group 5',
                'slug': 'circuit-group-5',
            },
            {
                'name': 'Circuit Group 6',
                'slug': 'circuit-group-6',
            },
        ]


class ProviderAccountTest(APIViewTestCases.APIViewTestCase):
    model = ProviderAccount
    brief_fields = ['account', 'description', 'display', 'id', 'name', 'url']

    @classmethod
    def setUpTestData(cls):
        providers = (
            Provider(name='Provider 1', slug='provider-1'),
            Provider(name='Provider 2', slug='provider-2'),
        )
        Provider.objects.bulk_create(providers)

        provider_accounts = (
            ProviderAccount(name='Provider Account 1', provider=providers[0], account='1234'),
            ProviderAccount(name='Provider Account 2', provider=providers[0], account='2345'),
            ProviderAccount(name='Provider Account 3', provider=providers[0], account='3456'),
        )
        ProviderAccount.objects.bulk_create(provider_accounts)

        cls.create_data = [
            {
                'name': 'Provider Account 4',
                'provider': providers[0].pk,
                'account': '4567',
            },
            {
                'name': 'Provider Account 5',
                'provider': providers[0].pk,
                'account': '5678',
            },
            {
                # Omit name to test uniqueness constraint
                'provider': providers[0].pk,
                'account': '6789',
            },
        ]

        cls.bulk_update_data = {
            'provider': providers[1].pk,
            'description': 'New description',
        }


class CircuitGroupAssignmentTest(APIViewTestCases.APIViewTestCase):
    model = CircuitGroupAssignment
    brief_fields = ['circuit', 'display', 'group', 'id', 'priority', 'url']
    bulk_update_data = {
        'priority': CircuitPriorityChoices.PRIORITY_INACTIVE,
    }

    @classmethod
    def setUpTestData(cls):

        circuit_groups = (
            CircuitGroup(name='Circuit Group 1', slug='circuit-group-1'),
            CircuitGroup(name='Circuit Group 2', slug='circuit-group-2'),
            CircuitGroup(name='Circuit Group 3', slug='circuit-group-3'),
            CircuitGroup(name='Circuit Group 4', slug='circuit-group-4'),
            CircuitGroup(name='Circuit Group 5', slug='circuit-group-5'),
            CircuitGroup(name='Circuit Group 6', slug='circuit-group-6'),
        )
        CircuitGroup.objects.bulk_create(circuit_groups)

        provider = Provider.objects.create(name='Provider 1', slug='provider-1')
        circuittype = CircuitType.objects.create(name='Circuit Type 1', slug='circuit-type-1')

        circuits = (
            Circuit(cid='Circuit 1', provider=provider, type=circuittype),
            Circuit(cid='Circuit 2', provider=provider, type=circuittype),
            Circuit(cid='Circuit 3', provider=provider, type=circuittype),
            Circuit(cid='Circuit 4', provider=provider, type=circuittype),
            Circuit(cid='Circuit 5', provider=provider, type=circuittype),
            Circuit(cid='Circuit 6', provider=provider, type=circuittype),
        )
        Circuit.objects.bulk_create(circuits)

        assignments = (
            CircuitGroupAssignment(
                group=circuit_groups[0],
                circuit=circuits[0],
                priority=CircuitPriorityChoices.PRIORITY_PRIMARY
            ),
            CircuitGroupAssignment(
                group=circuit_groups[1],
                circuit=circuits[1],
                priority=CircuitPriorityChoices.PRIORITY_SECONDARY
            ),
            CircuitGroupAssignment(
                group=circuit_groups[2],
                circuit=circuits[2],
                priority=CircuitPriorityChoices.PRIORITY_TERTIARY
            ),
        )
        CircuitGroupAssignment.objects.bulk_create(assignments)

        cls.create_data = [
            {
                'group': circuit_groups[3].pk,
                'circuit': circuits[3].pk,
                'priority': CircuitPriorityChoices.PRIORITY_PRIMARY,
            },
            {
                'group': circuit_groups[4].pk,
                'circuit': circuits[4].pk,
                'priority': CircuitPriorityChoices.PRIORITY_SECONDARY,
            },
            {
                'group': circuit_groups[5].pk,
                'circuit': circuits[5].pk,
                'priority': CircuitPriorityChoices.PRIORITY_TERTIARY,
            },
        ]


class ProviderNetworkTest(APIViewTestCases.APIViewTestCase):
    model = ProviderNetwork
    brief_fields = ['description', 'display', 'id', 'name', 'url']

    @classmethod
    def setUpTestData(cls):
        providers = (
            Provider(name='Provider 1', slug='provider-1'),
            Provider(name='Provider 2', slug='provider-2'),
        )
        Provider.objects.bulk_create(providers)

        provider_networks = (
            ProviderNetwork(name='Provider Network 1', provider=providers[0]),
            ProviderNetwork(name='Provider Network 2', provider=providers[0]),
            ProviderNetwork(name='Provider Network 3', provider=providers[0]),
        )
        ProviderNetwork.objects.bulk_create(provider_networks)

        cls.create_data = [
            {
                'name': 'Provider Network 4',
                'provider': providers[0].pk,
            },
            {
                'name': 'Provider Network 5',
                'provider': providers[0].pk,
            },
            {
                'name': 'Provider Network 6',
                'provider': providers[0].pk,
            },
        ]

        cls.bulk_update_data = {
            'provider': providers[1].pk,
            'description': 'New description',
        }
