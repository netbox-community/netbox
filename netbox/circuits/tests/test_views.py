import datetime

from django.test import override_settings
from django.urls import reverse

from circuits.choices import *
from circuits.models import *
from dcim.models import Cable, Interface, Site
from utilities.testing import ViewTestCases, create_tags, create_test_device


class ProviderTestCase(ViewTestCases.PrimaryObjectViewTestCase):
    model = Provider

    @classmethod
    def setUpTestData(cls):

        Provider.objects.bulk_create([
            Provider(name='Provider 1', slug='provider-1', asn=65001),
            Provider(name='Provider 2', slug='provider-2', asn=65002),
            Provider(name='Provider 3', slug='provider-3', asn=65003),
        ])

        tags = create_tags('Alpha', 'Bravo', 'Charlie')

        cls.form_data = {
            'name': 'Provider X',
            'slug': 'provider-x',
            'asn': 65123,
            'account': '1234',
            'portal_url': 'http://example.com/portal',
            'noc_contact': 'noc@example.com',
            'admin_contact': 'admin@example.com',
            'comments': 'Another provider',
            'tags': [t.pk for t in tags],
        }

        cls.csv_data = (
            "name,slug",
            "Provider 4,provider-4",
            "Provider 5,provider-5",
            "Provider 6,provider-6",
        )

        cls.bulk_edit_data = {
            'asn': 65009,
            'account': '5678',
            'portal_url': 'http://example.com/portal2',
            'noc_contact': 'noc2@example.com',
            'admin_contact': 'admin2@example.com',
            'comments': 'New comments',
        }


class CircuitTypeTestCase(ViewTestCases.OrganizationalObjectViewTestCase):
    model = CircuitType

    @classmethod
    def setUpTestData(cls):

        CircuitType.objects.bulk_create([
            CircuitType(name='Circuit Type 1', slug='circuit-type-1'),
            CircuitType(name='Circuit Type 2', slug='circuit-type-2'),
            CircuitType(name='Circuit Type 3', slug='circuit-type-3'),
        ])

        cls.form_data = {
            'name': 'Circuit Type X',
            'slug': 'circuit-type-x',
            'description': 'A new circuit type',
        }

        cls.csv_data = (
            "name,slug",
            "Circuit Type 4,circuit-type-4",
            "Circuit Type 5,circuit-type-5",
            "Circuit Type 6,circuit-type-6",
        )

        cls.bulk_edit_data = {
            'description': 'Foo',
        }


class CircuitTestCase(ViewTestCases.PrimaryObjectViewTestCase):
    model = Circuit

    @classmethod
    def setUpTestData(cls):

        providers = (
            Provider(name='Provider 1', slug='provider-1', asn=65001),
            Provider(name='Provider 2', slug='provider-2', asn=65002),
        )
        Provider.objects.bulk_create(providers)

        circuittypes = (
            CircuitType(name='Circuit Type 1', slug='circuit-type-1'),
            CircuitType(name='Circuit Type 2', slug='circuit-type-2'),
        )
        CircuitType.objects.bulk_create(circuittypes)

        Circuit.objects.bulk_create([
            Circuit(cid='Circuit 1', provider=providers[0], type=circuittypes[0]),
            Circuit(cid='Circuit 2', provider=providers[0], type=circuittypes[0]),
            Circuit(cid='Circuit 3', provider=providers[0], type=circuittypes[0]),
        ])

        tags = create_tags('Alpha', 'Bravo', 'Charlie')

        cls.form_data = {
            'cid': 'Circuit X',
            'provider': providers[1].pk,
            'type': circuittypes[1].pk,
            'status': CircuitStatusChoices.STATUS_DECOMMISSIONED,
            'tenant': None,
            'install_date': datetime.date(2020, 1, 1),
            'commit_rate': 1000,
            'description': 'A new circuit',
            'comments': 'Some comments',
            'tags': [t.pk for t in tags],
        }

        cls.csv_data = (
            "cid,provider,type,status",
            "Circuit 4,Provider 1,Circuit Type 1,active",
            "Circuit 5,Provider 1,Circuit Type 1,active",
            "Circuit 6,Provider 1,Circuit Type 1,active",
        )

        cls.bulk_edit_data = {
            'provider': providers[1].pk,
            'type': circuittypes[1].pk,
            'status': CircuitStatusChoices.STATUS_DECOMMISSIONED,
            'tenant': None,
            'commit_rate': 2000,
            'description': 'New description',
            'comments': 'New comments',
        }


class ProviderNetworkTestCase(ViewTestCases.PrimaryObjectViewTestCase):
    model = ProviderNetwork

    @classmethod
    def setUpTestData(cls):

        providers = (
            Provider(name='Provider 1', slug='provider-1'),
            Provider(name='Provider 2', slug='provider-2'),
        )
        Provider.objects.bulk_create(providers)

        ProviderNetwork.objects.bulk_create([
            ProviderNetwork(name='Provider Network 1', provider=providers[0]),
            ProviderNetwork(name='Provider Network 2', provider=providers[0]),
            ProviderNetwork(name='Provider Network 3', provider=providers[0]),
        ])

        tags = create_tags('Alpha', 'Bravo', 'Charlie')

        cls.form_data = {
            'name': 'Provider Network X',
            'provider': providers[1].pk,
            'description': 'A new provider network',
            'comments': 'Longer description goes here',
            'tags': [t.pk for t in tags],
        }

        cls.csv_data = (
            "name,provider,description",
            "Provider Network 4,Provider 1,Foo",
            "Provider Network 5,Provider 1,Bar",
            "Provider Network 6,Provider 1,Baz",
        )

        cls.bulk_edit_data = {
            'provider': providers[1].pk,
            'description': 'New description',
            'comments': 'New comments',
        }


class CircuitTerminationTestCase(
    ViewTestCases.EditObjectViewTestCase,
    ViewTestCases.DeleteObjectViewTestCase,
):
    model = CircuitTermination

    @classmethod
    def setUpTestData(cls):

        sites = (
            Site(name='Site 1', slug='site-1'),
            Site(name='Site 2', slug='site-2'),
            Site(name='Site 3', slug='site-3'),
        )
        Site.objects.bulk_create(sites)
        provider = Provider.objects.create(name='Provider 1', slug='provider-1')
        circuittype = CircuitType.objects.create(name='Circuit Type 1', slug='circuit-type-1')

        circuits = (
            Circuit(cid='Circuit 1', provider=provider, type=circuittype),
            Circuit(cid='Circuit 2', provider=provider, type=circuittype),
            Circuit(cid='Circuit 3', provider=provider, type=circuittype),
        )
        Circuit.objects.bulk_create(circuits)

        circuit_terminations = (
            CircuitTermination(circuit=circuits[0], term_side='A', site=sites[0]),
            CircuitTermination(circuit=circuits[0], term_side='Z', site=sites[1]),
            CircuitTermination(circuit=circuits[1], term_side='A', site=sites[0]),
            CircuitTermination(circuit=circuits[1], term_side='Z', site=sites[1]),
        )
        CircuitTermination.objects.bulk_create(circuit_terminations)

        cls.form_data = {
            'term_side': 'A',
            'site': sites[2].pk,
            'description': 'New description',
        }

    @override_settings(EXEMPT_VIEW_PERMISSIONS=['*'])
    def test_trace(self):
        device = create_test_device('Device 1')

        circuittermination = CircuitTermination.objects.first()
        interface = Interface.objects.create(
            device=device,
            name='Interface 1'
        )
        Cable(termination_a=circuittermination, termination_b=interface).save()

        response = self.client.get(reverse('circuits:circuittermination_trace', kwargs={'pk': circuittermination.pk}))
        self.assertHttpStatus(response, 200)
