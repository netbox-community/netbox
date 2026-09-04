import uuid

from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import NON_FIELD_ERRORS, ValidationError
from django.test import RequestFactory, TestCase, tag

from circuits.models import Circuit, CircuitTermination, CircuitType, Provider, ProviderNetwork
from core.choices import ObjectChangeActionChoices
from core.models import ObjectChange
from dcim.models import Location, Region, Site, SiteGroup
from netbox.context_managers import event_tracking
from users.models import User


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

    def test_circuit_termination_circuit_change_with_generator_update_fields(self):
        """
        A one-shot iterable passed as update_fields must still reach the database, so the
        circuit change is persisted and both caches are updated.
        """
        termination = CircuitTermination.objects.create(
            circuit=self.circuits[0],
            term_side='A',
            termination=self.sites[0],
        )

        termination.circuit = self.circuits[1]
        termination.save(update_fields=(field for field in ('circuit',)))

        termination.refresh_from_db()
        self.circuits[0].refresh_from_db()
        self.circuits[1].refresh_from_db()

        self.assertEqual(termination.circuit, self.circuits[1])
        self.assertIsNone(self.circuits[0].termination_a)
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


class CircuitTerminationChangeLoggingTestCase(TestCase):
    """
    The Circuit.termination_a/termination_z pointers are maintained by CircuitTermination.save().
    They were previously written with a queryset update(), which emits no post_save and therefore
    no ObjectChange, so consumers which replay the changelog never saw the association. (#23134)
    """
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(username='testuser', password='pw')

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

    def _tracked(self, func):
        request = RequestFactory().get('/')
        request.id = uuid.uuid4()
        request.user = self.user
        with event_tracking(request):
            return func()

    def _circuit_changes(self, circuit):
        return ObjectChange.objects.filter(
            changed_object_type=ContentType.objects.get_for_model(Circuit),
            changed_object_id=circuit.pk,
            action=ObjectChangeActionChoices.ACTION_UPDATE,
        ).order_by('pk')

    @tag('regression')  # Ref: #23134
    def test_creation_records_circuit_update(self):
        termination = self._tracked(lambda: CircuitTermination.objects.create(
            circuit=self.circuits[0], term_side='A', termination=self.sites[0],
        ))

        changes = self._circuit_changes(self.circuits[0])
        self.assertEqual(changes.count(), 1)
        self.assertIsNone(changes[0].prechange_data['termination_a'])
        self.assertEqual(changes[0].postchange_data['termination_a'], termination.pk)

    @tag('regression')  # Ref: #23134
    def test_second_termination_snapshots_current_state(self):
        # The A pointer is already committed when the Z termination is created; its prechange
        # snapshot must reflect that rather than a Circuit cached before the A write.
        termination_a = self._tracked(lambda: CircuitTermination.objects.create(
            circuit=self.circuits[0], term_side='A', termination=self.sites[0],
        ))
        ObjectChange.objects.all().delete()

        termination_z = self._tracked(lambda: CircuitTermination.objects.create(
            circuit=self.circuits[0], term_side='Z', termination=self.sites[1],
        ))

        changes = self._circuit_changes(self.circuits[0])
        self.assertEqual(changes.count(), 1)
        self.assertEqual(changes[0].prechange_data['termination_a'], termination_a.pk)
        self.assertIsNone(changes[0].prechange_data['termination_z'])
        self.assertEqual(changes[0].postchange_data['termination_a'], termination_a.pk)
        self.assertEqual(changes[0].postchange_data['termination_z'], termination_z.pk)

    @tag('regression')  # Ref: #23134
    def test_circuit_change_records_both_circuits(self):
        termination = self._tracked(lambda: CircuitTermination.objects.create(
            circuit=self.circuits[0], term_side='A', termination=self.sites[0],
        ))
        ObjectChange.objects.all().delete()

        def _move():
            termination.circuit = self.circuits[1]
            termination.save()

        self._tracked(_move)

        # The old circuit's pointer is cleared...
        old_changes = self._circuit_changes(self.circuits[0])
        self.assertEqual(old_changes.count(), 1)
        self.assertEqual(old_changes[0].prechange_data['termination_a'], termination.pk)
        self.assertIsNone(old_changes[0].postchange_data['termination_a'])

        # ...and the new circuit's pointer is set.
        new_changes = self._circuit_changes(self.circuits[1])
        self.assertEqual(new_changes.count(), 1)
        self.assertIsNone(new_changes[0].prechange_data['termination_a'])
        self.assertEqual(new_changes[0].postchange_data['termination_a'], termination.pk)

    @tag('regression')  # Ref: #23134
    def test_term_side_change_records_single_circuit_update(self):
        termination = self._tracked(lambda: CircuitTermination.objects.create(
            circuit=self.circuits[0], term_side='A', termination=self.sites[0],
        ))
        ObjectChange.objects.all().delete()

        def _flip():
            termination.term_side = 'Z'
            termination.save()

        self._tracked(_flip)

        # Both pointers move within one circuit, so the clear and the set are coalesced into one
        # write rather than passing through a state with neither side set.
        changes = self._circuit_changes(self.circuits[0])
        self.assertEqual(changes.count(), 1)
        self.assertEqual(changes[0].prechange_data['termination_a'], termination.pk)
        self.assertIsNone(changes[0].prechange_data['termination_z'])
        self.assertIsNone(changes[0].postchange_data['termination_a'])
        self.assertEqual(changes[0].postchange_data['termination_z'], termination.pk)

    @tag('regression')  # Ref: #23134
    def test_redundant_pointer_write_is_skipped(self):
        # bulk_create() bypasses save(), so the circuit's pointer is never written. Moving the
        # termination afterwards reaches the clear path with the pointer already null.
        CircuitTermination.objects.bulk_create([
            CircuitTermination(circuit=self.circuits[0], term_side='A', termination=self.sites[0]),
        ])
        termination = CircuitTermination.objects.get(circuit=self.circuits[0], term_side='A')

        def _move():
            termination.circuit = self.circuits[1]
            termination.save()

        old_circuit_last_updated = Circuit.objects.get(pk=self.circuits[0].pk).last_updated

        self._tracked(_move)

        # The old circuit's pointer was already null, so it is not written to at all...
        self.assertFalse(self._circuit_changes(self.circuits[0]).exists())
        self.assertEqual(
            Circuit.objects.get(pk=self.circuits[0].pk).last_updated, old_circuit_last_updated
        )

        # ...while the new circuit's pointer is set as usual.
        new_changes = self._circuit_changes(self.circuits[1])
        self.assertEqual(new_changes.count(), 1)
        self.assertEqual(new_changes[0].postchange_data['termination_a'], termination.pk)

    @tag('regression')  # Ref: #23134
    def test_noop_resave_records_no_circuit_update(self):
        termination = self._tracked(lambda: CircuitTermination.objects.create(
            circuit=self.circuits[0], term_side='A', termination=self.sites[0],
        ))
        ObjectChange.objects.all().delete()

        self._tracked(termination.save)

        self.assertFalse(self._circuit_changes(self.circuits[0]).exists())

    @tag('regression')  # Ref: #23134
    def test_circuit_change_via_update_fields_records_circuit_update(self):
        # save(update_fields=...) takes its own branch when deciding whether the circuit or
        # term_side is being persisted; the pointer writes must be recorded there too.
        termination = self._tracked(lambda: CircuitTermination.objects.create(
            circuit=self.circuits[0], term_side='A', termination=self.sites[0],
        ))
        ObjectChange.objects.all().delete()

        def _move():
            termination.circuit = self.circuits[1]
            termination.save(update_fields=('circuit',))

        self._tracked(_move)

        old_changes = self._circuit_changes(self.circuits[0])
        self.assertEqual(old_changes.count(), 1)
        self.assertIsNone(old_changes[0].postchange_data['termination_a'])

        new_changes = self._circuit_changes(self.circuits[1])
        self.assertEqual(new_changes.count(), 1)
        self.assertEqual(new_changes[0].postchange_data['termination_a'], termination.pk)

    def test_deletion_clears_pointer_without_recording_a_change(self):
        # Deleting a termination clears the pointer via on_delete=SET_NULL, which emits no
        # post_save and so is not change-logged. handle_deleted_object() does not cover it
        # either: termination_a/termination_z declare related_name='+', so they are hidden
        # relations and absent from CircuitTermination._meta.related_objects. The changelog is
        # therefore still asymmetric here; documented rather than fixed, as replaying the
        # termination's DELETE re-applies SET_NULL on the target side.
        termination = self._tracked(lambda: CircuitTermination.objects.create(
            circuit=self.circuits[0], term_side='A', termination=self.sites[0],
        ))
        ObjectChange.objects.all().delete()

        self._tracked(termination.delete)

        self.circuits[0].refresh_from_db()
        self.assertIsNone(self.circuits[0].termination_a_id)
        self.assertFalse(self._circuit_changes(self.circuits[0]).exists())
