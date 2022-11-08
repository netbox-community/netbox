from django.test import TestCase

from circuits.models import Provider, Circuit, CircuitType
from extras.models import Change, Branch
from netbox.staging import checkout


class StagingTestCase(TestCase):

    @classmethod
    def setUpTestData(cls):
        providers = (
            Provider(name='Provider A', slug='provider-a'),
            Provider(name='Provider B', slug='provider-b'),
            Provider(name='Provider C', slug='provider-c'),
        )
        Provider.objects.bulk_create(providers)

        circuit_type = CircuitType.objects.create(name='Circuit Type 1', slug='circuit-type-1')

        Circuit.objects.bulk_create((
            Circuit(provider=providers[0], cid='Circuit A1', type=circuit_type),
            Circuit(provider=providers[0], cid='Circuit A2', type=circuit_type),
            Circuit(provider=providers[0], cid='Circuit A3', type=circuit_type),
            Circuit(provider=providers[1], cid='Circuit B1', type=circuit_type),
            Circuit(provider=providers[1], cid='Circuit B2', type=circuit_type),
            Circuit(provider=providers[1], cid='Circuit B3', type=circuit_type),
            Circuit(provider=providers[2], cid='Circuit C1', type=circuit_type),
            Circuit(provider=providers[2], cid='Circuit C2', type=circuit_type),
            Circuit(provider=providers[2], cid='Circuit C3', type=circuit_type),
        ))

    def test_object_creation(self):
        branch = Branch.objects.create(name='Branch 1')

        with checkout(branch):
            provider = Provider.objects.create(name='Provider D', slug='provider-d')
            Circuit.objects.create(provider=provider, cid='Circuit D1', type=CircuitType.objects.first())

            self.assertEqual(Provider.objects.count(), 4)
            self.assertEqual(Circuit.objects.count(), 10)

        self.assertEqual(Provider.objects.count(), 3)
        self.assertEqual(Circuit.objects.count(), 9)
        self.assertEqual(Change.objects.count(), 2)

    def test_object_modification(self):
        branch = Branch.objects.create(name='Branch 1')

        with checkout(branch):
            provider = Provider.objects.get(name='Provider A')
            provider.name = 'Provider X'
            provider.save()
            circuit = Circuit.objects.get(cid='Circuit A1')
            circuit.cid = 'Circuit X'
            circuit.save()

            self.assertEqual(Provider.objects.count(), 3)
            self.assertEqual(Provider.objects.get(pk=provider.pk).name, 'Provider X')
            self.assertEqual(Circuit.objects.count(), 9)
            self.assertEqual(Circuit.objects.get(pk=circuit.pk).cid, 'Circuit X')

        self.assertEqual(Provider.objects.count(), 3)
        self.assertEqual(Provider.objects.get(pk=provider.pk).name, 'Provider A')
        self.assertEqual(Circuit.objects.count(), 9)
        self.assertEqual(Circuit.objects.get(pk=circuit.pk).cid, 'Circuit A1')
        self.assertEqual(Change.objects.count(), 2)

    def test_object_deletion(self):
        branch = Branch.objects.create(name='Branch 1')

        with checkout(branch):
            provider = Provider.objects.get(name='Provider A')
            provider.circuits.all().delete()
            provider.delete()

            self.assertEqual(Provider.objects.count(), 2)
            self.assertEqual(Circuit.objects.count(), 6)

        self.assertEqual(Provider.objects.count(), 3)
        self.assertEqual(Circuit.objects.count(), 9)
        self.assertEqual(Change.objects.count(), 4)

    def test_create_update_delete_clean(self):
        branch = Branch.objects.create(name='Branch 1')

        with checkout(branch):

            # Create a new object
            provider = Provider.objects.create(name='Provider D', slug='provider-d')
            provider.save()

            # Update it
            provider.comments = 'Another change'
            provider.save()

            # Delete it
            provider.delete()

        self.assertFalse(Change.objects.exists())
