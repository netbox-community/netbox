from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import NON_FIELD_ERRORS, ValidationError
from django.test import TestCase

from circuits.models import Circuit, CircuitTermination, CircuitType, Provider, ProviderNetwork
from dcim.models import Location, Region, Site, SiteGroup


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

    def test_termination_required_when_termination_type_is_selected(self):
        """Model rejects type-without-target before generic GFK validation hits termination_id."""
        provider_network_type = ContentType.objects.get_for_model(ProviderNetwork)

        termination = CircuitTermination(
            circuit=self.circuits[0],
            term_side='A',
            termination_type=provider_network_type,
        )

        with self.assertRaises(ValidationError) as cm:
            termination.full_clean()

        errors = cm.exception.message_dict
        self.assertIn(NON_FIELD_ERRORS, errors)
        self.assertIn('Please select a Provider Network.', errors[NON_FIELD_ERRORS])
        self.assertNotIn('termination_id', errors)


class CircuitTerminationDenormalizationTriggerTestCase(TestCase):
    """
    Verify the PostgreSQL triggers (installed by circuits migration 0058) that keep a
    CircuitTermination's denormalized scope columns in sync with its Site/Location.

    These replace the former Python `post_save` handler in netbox.denormalized. Unlike that
    handler, the triggers also fire for bulk QuerySet.update() writes (exercised below).
    """

    @classmethod
    def setUpTestData(cls):
        provider = Provider.objects.create(name='Provider 1', slug='provider-1')
        circuit_type = CircuitType.objects.create(name='Circuit Type 1', slug='circuit-type-1')
        cls.circuit = Circuit.objects.create(cid='Circuit 1', provider=provider, type=circuit_type)

    def test_site_region_group_change_propagates_to_termination(self):
        region_a = Region.objects.create(name='Region A', slug='region-a')
        region_b = Region.objects.create(name='Region B', slug='region-b')
        group_a = SiteGroup.objects.create(name='Group A', slug='group-a')
        group_b = SiteGroup.objects.create(name='Group B', slug='group-b')
        site = Site.objects.create(name='Site', slug='site', region=region_a, group=group_a)

        termination = CircuitTermination.objects.create(
            circuit=self.circuit, term_side='A', termination=site,
        )
        self.assertEqual(termination._region, region_a)
        self.assertEqual(termination._site_group, group_a)

        # Reassign the Site's region/group; the trigger should update the termination.
        site.region = region_b
        site.group = group_b
        site.save()

        termination.refresh_from_db()
        self.assertEqual(termination._region, region_b)
        self.assertEqual(termination._site_group, group_b)

    def test_location_site_change_propagates_to_termination(self):
        region_a = Region.objects.create(name='Region A', slug='region-a')
        region_b = Region.objects.create(name='Region B', slug='region-b')
        group_a = SiteGroup.objects.create(name='Group A', slug='group-a')
        group_b = SiteGroup.objects.create(name='Group B', slug='group-b')
        site_a = Site.objects.create(name='Site A', slug='site-a', region=region_a, group=group_a)
        site_b = Site.objects.create(name='Site B', slug='site-b', region=region_b, group=group_b)
        location = Location.objects.create(name='Loc', slug='loc', site=site_a)

        termination = CircuitTermination.objects.create(
            circuit=self.circuit, term_side='A', termination=location,
        )
        self.assertEqual(termination._site, site_a)
        self.assertEqual(termination._location, location)

        # Move the Location to a different Site; the trigger updates _site and pulls the new
        # site's region/group through in the same statement.
        location.site = site_b
        location.save()

        termination.refresh_from_db()
        self.assertEqual(termination._site, site_b)
        self.assertEqual(termination._region, region_b)
        self.assertEqual(termination._site_group, group_b)

    def test_bulk_update_of_site_propagates_to_termination(self):
        """
        A QuerySet.update() bypasses post_save (the old handler never fired for it); the
        DB trigger fires regardless, which is the behavior this change introduces.
        """
        region_a = Region.objects.create(name='Region A', slug='region-a')
        region_b = Region.objects.create(name='Region B', slug='region-b')
        site = Site.objects.create(name='Site', slug='site', region=region_a)

        termination = CircuitTermination.objects.create(
            circuit=self.circuit, term_side='A', termination=site,
        )
        self.assertEqual(termination._region, region_a)

        Site.objects.filter(pk=site.pk).update(region=region_b)

        termination.refresh_from_db()
        self.assertEqual(termination._region, region_b)
