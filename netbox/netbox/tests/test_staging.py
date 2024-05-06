from django.db.models.signals import post_save
from django.test import TransactionTestCase

from circuits.models import Provider, Circuit, CircuitType
from extras.choices import ChangeActionChoices
from extras.models import Branch, StagedChange, Tag
from ipam.models import ASN, RIR
from netbox.search.backends import search_backend
from netbox.staging import checkout
from utilities.testing import create_tags


class StagingTestCase(TransactionTestCase):

    def setUp(self):
        # Disconnect search backend to avoid issues with cached ObjectTypes being deleted
        # from the database upon transaction rollback
        post_save.disconnect(search_backend.caching_handler)

        create_tags('Alpha', 'Bravo', 'Charlie')

        rir = RIR.objects.create(name='RIR 1', slug='rir-1')
        asns = (
            ASN(asn=65001, rir=rir),
            ASN(asn=65002, rir=rir),
            ASN(asn=65003, rir=rir),
        )
        ASN.objects.bulk_create(asns)

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
        tags = Tag.objects.all()
        asns = ASN.objects.all()

        with checkout(branch):
            provider = Provider.objects.create(name='Provider D', slug='provider-d')
            provider.asns.set(asns)
            circuit = Circuit.objects.create(provider=provider, cid='Circuit D1', type=CircuitType.objects.first())
            circuit.tags.set(tags)

            # Sanity-checking
            self.assertEqual(Provider.objects.count(), 4)
            self.assertListEqual(list(provider.asns.all()), list(asns))
            self.assertEqual(Circuit.objects.count(), 10)
            self.assertListEqual(list(circuit.tags.all()), list(tags))

        # Verify that changes have been rolled back after exiting the context
        self.assertEqual(Provider.objects.count(), 3)
        self.assertEqual(Circuit.objects.count(), 9)
        self.assertEqual(StagedChange.objects.count(), 5)

        # Verify that changes are replayed upon entering the context
        with checkout(branch):
            self.assertEqual(Provider.objects.count(), 4)
            self.assertEqual(Circuit.objects.count(), 10)
            provider = Provider.objects.get(name='Provider D')
            self.assertListEqual(list(provider.asns.all()), list(asns))
            circuit = Circuit.objects.get(cid='Circuit D1')
            self.assertListEqual(list(circuit.tags.all()), list(tags))

        # Verify that changes are applied and deleted upon branch merge
        branch.merge()
        self.assertEqual(Provider.objects.count(), 4)
        self.assertEqual(Circuit.objects.count(), 10)
        provider = Provider.objects.get(name='Provider D')
        self.assertListEqual(list(provider.asns.all()), list(asns))
        circuit = Circuit.objects.get(cid='Circuit D1')
        self.assertListEqual(list(circuit.tags.all()), list(tags))
        self.assertEqual(StagedChange.objects.count(), 0)

    def test_object_modification(self):
        branch = Branch.objects.create(name='Branch 1')
        tags = Tag.objects.all()
        asns = ASN.objects.all()

        with checkout(branch):
            provider = Provider.objects.get(name='Provider A')
            provider.name = 'Provider X'
            provider.save()
            provider.asns.set(asns)
            circuit = Circuit.objects.get(cid='Circuit A1')
            circuit.cid = 'Circuit X'
            circuit.save()
            circuit.tags.set(tags)

            # Sanity-checking
            self.assertEqual(Provider.objects.count(), 3)
            self.assertEqual(Provider.objects.get(pk=provider.pk).name, 'Provider X')
            self.assertListEqual(list(provider.asns.all()), list(asns))
            self.assertEqual(Circuit.objects.count(), 9)
            self.assertEqual(Circuit.objects.get(pk=circuit.pk).cid, 'Circuit X')
            self.assertListEqual(list(circuit.tags.all()), list(tags))

        # Verify that changes have been rolled back after exiting the context
        self.assertEqual(Provider.objects.count(), 3)
        self.assertEqual(Provider.objects.get(pk=provider.pk).name, 'Provider A')
        provider = Provider.objects.get(pk=provider.pk)
        self.assertListEqual(list(provider.asns.all()), [])
        self.assertEqual(Circuit.objects.count(), 9)
        circuit = Circuit.objects.get(pk=circuit.pk)
        self.assertEqual(circuit.cid, 'Circuit A1')
        self.assertListEqual(list(circuit.tags.all()), [])
        self.assertEqual(StagedChange.objects.count(), 5)

        # Verify that changes are replayed upon entering the context
        with checkout(branch):
            self.assertEqual(Provider.objects.count(), 3)
            self.assertEqual(Provider.objects.get(pk=provider.pk).name, 'Provider X')
            provider = Provider.objects.get(pk=provider.pk)
            self.assertListEqual(list(provider.asns.all()), list(asns))
            self.assertEqual(Circuit.objects.count(), 9)
            circuit = Circuit.objects.get(pk=circuit.pk)
            self.assertEqual(circuit.cid, 'Circuit X')
            self.assertListEqual(list(circuit.tags.all()), list(tags))

        # Verify that changes are applied and deleted upon branch merge
        branch.merge()
        self.assertEqual(Provider.objects.count(), 3)
        self.assertEqual(Provider.objects.get(pk=provider.pk).name, 'Provider X')
        provider = Provider.objects.get(pk=provider.pk)
        self.assertListEqual(list(provider.asns.all()), list(asns))
        self.assertEqual(Circuit.objects.count(), 9)
        circuit = Circuit.objects.get(pk=circuit.pk)
        self.assertEqual(circuit.cid, 'Circuit X')
        self.assertListEqual(list(circuit.tags.all()), list(tags))
        self.assertEqual(StagedChange.objects.count(), 0)

    def test_object_deletion(self):
        branch = Branch.objects.create(name='Branch 1')

        with checkout(branch):
            provider = Provider.objects.get(name='Provider A')
            provider.circuits.all().delete()
            provider.delete()

            # Sanity-checking
            self.assertEqual(Provider.objects.count(), 2)
            self.assertEqual(Circuit.objects.count(), 6)

        # Verify that changes have been rolled back after exiting the context
        self.assertEqual(Provider.objects.count(), 3)
        self.assertEqual(Circuit.objects.count(), 9)
        self.assertEqual(StagedChange.objects.count(), 4)

        # Verify that changes are replayed upon entering the context
        with checkout(branch):
            self.assertEqual(Provider.objects.count(), 2)
            self.assertEqual(Circuit.objects.count(), 6)

        # Verify that changes are applied and deleted upon branch merge
        branch.merge()
        self.assertEqual(Provider.objects.count(), 2)
        self.assertEqual(Circuit.objects.count(), 6)
        self.assertEqual(StagedChange.objects.count(), 0)

    def test_exit_enter_context(self):
        branch = Branch.objects.create(name='Branch 1')

        with checkout(branch):

            # Create a new object
            provider = Provider.objects.create(name='Provider D', slug='provider-d')
            provider.save()

        # Check that a create Change was recorded
        self.assertEqual(StagedChange.objects.count(), 1)
        change = StagedChange.objects.first()
        self.assertEqual(change.action, ChangeActionChoices.ACTION_CREATE)
        self.assertEqual(change.data['name'], provider.name)

        with checkout(branch):

            # Update the staged object
            provider = Provider.objects.get(name='Provider D')
            provider.comments = 'New comments'
            provider.save()

        # Check that a second Change object has been created for the object
        self.assertEqual(StagedChange.objects.count(), 2)
        change = StagedChange.objects.last()
        self.assertEqual(change.action, ChangeActionChoices.ACTION_UPDATE)
        self.assertEqual(change.data['name'], provider.name)
        self.assertEqual(change.data['comments'], provider.comments)

        with checkout(branch):

            # Delete the staged object
            provider = Provider.objects.get(name='Provider D')
            provider.delete()

        # Check that a third Change has recorded the object's deletion
        self.assertEqual(StagedChange.objects.count(), 3)
        change = StagedChange.objects.last()
        self.assertEqual(change.action, ChangeActionChoices.ACTION_DELETE)
        self.assertIsNone(change.data)
