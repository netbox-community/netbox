import datetime

from circuits.choices import *
from circuits.models import Circuit, CircuitType, Provider
from utilities.testing import ViewTestCases


class ProviderTestCase(ViewTestCases.PrimaryObjectViewTestCase):
    model = Provider

    @classmethod
    def setUpTestData(cls):

        Provider.objects.bulk_create([
            Provider(name='Provider 1', slug='provider-1', asn=65001),
            Provider(name='Provider 2', slug='provider-2', asn=65002),
            Provider(name='Provider 3', slug='provider-3', asn=65003),
        ])

        tags = cls.create_tags('Alpha', 'Bravo', 'Charlie')

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

        tags = cls.create_tags('Alpha', 'Bravo', 'Charlie')

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
            "cid,provider,type",
            "Circuit 4,Provider 1,Circuit Type 1",
            "Circuit 5,Provider 1,Circuit Type 1",
            "Circuit 6,Provider 1,Circuit Type 1",
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
