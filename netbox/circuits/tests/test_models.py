from django.test import TestCase

from circuits.models import Circuit, CircuitTermination, CircuitType, Provider, ProviderNetwork
from dcim.models import Site


class CircuitTerminationTestCase(TestCase):

    @classmethod
    def setUpTestData(cls):
        provider = Provider.objects.create(name='Provider 1', slug='provider-1')
        circuit_type = CircuitType.objects.create(name='Circuit Type 1', slug='circuit-type-1')

        cls.sites = (
            Site.objects.create(name='Site 1', slug='site-1'),
            Site.objects.create(name='Site 2', slug='site-2'),
        )

        cls.circuits = (
            Circuit.objects.create(cid='Circuit 1', provider=provider, type=circuit_type),
            Circuit.objects.create(cid='Circuit 2', provider=provider, type=circuit_type),
        )

        cls.provider_network = ProviderNetwork.objects.create(name='Provider Network 1', provider=provider)

    def test_circuit_termination_creation_populates_circuit_cache(self):
        """
        When a CircuitTermination is created, the parent Circuit's termination_a or termination_z
        cache field should be populated.
        """
        # Create A termination
        termination_a = CircuitTermination.objects.create(
            circuit=self.circuits[0],
            term_side='A',
            termination=self.sites[0],
        )
        self.circuits[0].refresh_from_db()
        self.assertEqual(self.circuits[0].termination_a, termination_a)
        self.assertIsNone(self.circuits[0].termination_z)

        # Create Z termination
        termination_z = CircuitTermination.objects.create(
            circuit=self.circuits[0],
            term_side='Z',
            termination=self.sites[1],
        )
        self.circuits[0].refresh_from_db()
        self.assertEqual(self.circuits[0].termination_a, termination_a)
        self.assertEqual(self.circuits[0].termination_z, termination_z)

    def test_circuit_termination_circuit_change_clears_old_cache(self):
        """
        When a CircuitTermination's circuit is changed, the old Circuit's cache should be cleared
        and the new Circuit's cache should be populated.
        """
        # Create termination on self.circuits[0]
        termination = CircuitTermination.objects.create(
            circuit=self.circuits[0],
            term_side='A',
            termination=self.sites[0],
        )
        self.circuits[0].refresh_from_db()
        self.assertEqual(self.circuits[0].termination_a, termination)

        # Move termination to self.circuits[1]
        termination.circuit = self.circuits[1]
        termination.save()

        self.circuits[0].refresh_from_db()
        self.circuits[1].refresh_from_db()

        # Old circuit's cache should be cleared
        self.assertIsNone(self.circuits[0].termination_a)
        # New circuit's cache should be populated
        self.assertEqual(self.circuits[1].termination_a, termination)

    def test_circuit_termination_term_side_change_clears_old_cache(self):
        """
        When a CircuitTermination's term_side is changed, the old side's cache should be cleared
        and the new side's cache should be populated.
        """
        # Create A termination
        termination = CircuitTermination.objects.create(
            circuit=self.circuits[0],
            term_side='A',
            termination=self.sites[0],
        )
        self.circuits[0].refresh_from_db()
        self.assertEqual(self.circuits[0].termination_a, termination)
        self.assertIsNone(self.circuits[0].termination_z)

        # Change from A to Z
        termination.term_side = 'Z'
        termination.save()

        self.circuits[0].refresh_from_db()

        # A side should be cleared, Z side should be populated
        self.assertIsNone(self.circuits[0].termination_a)
        self.assertEqual(self.circuits[0].termination_z, termination)

    def test_circuit_termination_circuit_and_term_side_change(self):
        """
        When both circuit and term_side are changed, the old Circuit's old side cache should be
        cleared and the new Circuit's new side cache should be populated.
        """
        # Create A termination on self.circuits[0]
        termination = CircuitTermination.objects.create(
            circuit=self.circuits[0],
            term_side='A',
            termination=self.sites[0],
        )
        self.circuits[0].refresh_from_db()
        self.assertEqual(self.circuits[0].termination_a, termination)

        # Change to self.circuits[1] Z side
        termination.circuit = self.circuits[1]
        termination.term_side = 'Z'
        termination.save()

        self.circuits[0].refresh_from_db()
        self.circuits[1].refresh_from_db()

        # Old circuit's A side should be cleared
        self.assertIsNone(self.circuits[0].termination_a)
        self.assertIsNone(self.circuits[0].termination_z)
        # New circuit's Z side should be populated
        self.assertIsNone(self.circuits[1].termination_a)
        self.assertEqual(self.circuits[1].termination_z, termination)

    def test_circuit_termination_deletion_clears_cache(self):
        """
        When a CircuitTermination is deleted, the parent Circuit's cache should be cleared.
        """
        termination = CircuitTermination.objects.create(
            circuit=self.circuits[0],
            term_side='A',
            termination=self.sites[0],
        )
        self.circuits[0].refresh_from_db()
        self.assertEqual(self.circuits[0].termination_a, termination)

        # Delete the termination
        termination.delete()
        self.circuits[0].refresh_from_db()

        # Cache should be cleared (SET_NULL behavior)
        self.assertIsNone(self.circuits[0].termination_a)
