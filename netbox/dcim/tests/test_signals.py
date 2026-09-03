from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from django.apps import apps
from django.contrib.contenttypes.models import ContentType
from django.db import connection, transaction
from django.test import SimpleTestCase, TestCase, TransactionTestCase, override_settings
from django.test.utils import CaptureQueriesContext

from circuits.models import Circuit, CircuitTermination, CircuitType, Provider
from dcim import signals
from dcim.choices import CableEndChoices, CableProfileChoices, LinkStatusChoices
from dcim.models import (
    Cable,
    CablePath,
    CableTermination,
    Device,
    DeviceRole,
    DeviceType,
    FrontPort,
    Interface,
    Location,
    MACAddress,
    Manufacturer,
    PortMapping,
    PowerPanel,
    Rack,
    RearPort,
    Region,
    Site,
    SiteGroup,
    VirtualChassis,
)
from dcim.models.device_components import ComponentModel
from dcim.models.mixins import CachedScopeMixin
from ipam.models import Prefix
from netbox.plugins import PluginConfig
from utilities.testing import PinnedConnectionRouter
from virtualization.models import Cluster, ClusterType
from wireless.models import WirelessLAN


class ScopePropagationCaptureMixin:
    """
    Helper for asserting whether a save propagated to the tables its post_save handler
    rewrites.

    Only the tables the handler itself rewrites are listed. The device components and
    cable terminations are refreshed by database triggers, which issue their UPDATEs
    inside the database where no query capture can see them. Neither is the saved
    object's own table, which carries the save's own UPDATE.
    """
    propagation_tables = frozenset()

    def capture_propagation_updates(self, obj, raw=False, update_fields=None):
        with CaptureQueriesContext(connection) as ctx:
            if raw:
                obj.save_base(raw=True)
            elif update_fields is not None:
                obj.save(update_fields=update_fields)
            else:
                obj.save()

        return {
            table for table in self.propagation_tables
            for q in ctx.captured_queries
            # The config-context cache invalidation in extras.signals writes to dcim_device on
            # an upstream save too, so matching the table alone would report a propagation that
            # never ran. It is identifiable by the column it nulls.
            if q['sql'].startswith(f'UPDATE "{table}"') and '_config_context_data' not in q['sql']
        }


class LocationSiteChangeSignalTestCase(ScopePropagationCaptureMixin, TestCase):
    """
    Verify dcim.signals.handle_location_site_change propagates a Location's new Site to
    every descendant Location, Rack, Device, PowerPanel, and component when the parent
    Location's site assignment changes.
    """
    propagation_tables = frozenset({'dcim_rack', 'dcim_device', 'dcim_powerpanel'})

    @classmethod
    def setUpTestData(cls):
        cls.site_a = Site.objects.create(name='Site A', slug='site-a')
        cls.site_b = Site.objects.create(name='Site B', slug='site-b')
        manufacturer = Manufacturer.objects.create(name='Manufacturer', slug='manufacturer')
        cls.device_type = DeviceType.objects.create(manufacturer=manufacturer, model='Device Type')
        cls.device_role = DeviceRole.objects.create(name='Device Role', slug='device-role')

    def test_changing_location_site_propagates_to_children(self):
        parent_location = Location.objects.create(name='Parent', slug='parent', site=self.site_a)
        child_location = Location.objects.create(name='Child', slug='child', site=self.site_a, parent=parent_location)
        rack = Rack.objects.create(name='Rack', site=self.site_a, location=parent_location)
        device = Device.objects.create(
            name='Device',
            site=self.site_a,
            location=parent_location,
            device_type=self.device_type,
            role=self.device_role,
        )
        interface = Interface.objects.create(device=device, name='Interface 1')
        power_panel = PowerPanel.objects.create(name='Panel', site=self.site_a, location=parent_location)

        parent_location.site = self.site_b
        parent_location.save()

        child_location.refresh_from_db()
        rack.refresh_from_db()
        device.refresh_from_db()
        interface.refresh_from_db()
        power_panel.refresh_from_db()
        self.assertEqual(child_location.site, self.site_b)
        self.assertEqual(rack.site, self.site_b)
        self.assertEqual(device.site, self.site_b)
        self.assertEqual(interface._site, self.site_b)
        self.assertEqual(power_panel.site, self.site_b)

    def test_changing_location_site_updates_circuittermination_caches(self):
        # CircuitTermination caches its scope ancestry under termination_type/termination_id
        # rather than under CachedScopeMixin's scope field, and is kept current by the
        # denormalization trigger sourced from dcim_location. Both the
        # moved Location's own terminations and those of its descendants must be repaired
        # here, region and site group included. Origin and destination Sites are given
        # distinct regions and groups so a value left stale is distinguishable from one that
        # was never set.
        origin_region = Region.objects.create(name='Region C', slug='region-c')
        origin_group = SiteGroup.objects.create(name='Group C', slug='group-c')
        origin = Site.objects.create(
            name='Site C', slug='site-c', region=origin_region, group=origin_group
        )
        region = Region.objects.create(name='Region D', slug='region-d')
        group = SiteGroup.objects.create(name='Group D', slug='group-d')
        site = Site.objects.create(name='Site D', slug='site-d', region=region, group=group)
        parent_location = Location.objects.create(name='Parent', slug='parent', site=origin)
        child_location = Location.objects.create(name='Child', slug='child', site=origin, parent=parent_location)
        provider = Provider.objects.create(name='Provider', slug='provider')
        circuit_type = CircuitType.objects.create(name='Circuit Type', slug='circuit-type')
        circuit = Circuit.objects.create(cid='Circuit 1', provider=provider, type=circuit_type)
        termination_a = CircuitTermination.objects.create(
            circuit=circuit, term_side='A', termination=parent_location
        )
        termination_z = CircuitTermination.objects.create(
            circuit=circuit, term_side='Z', termination=child_location
        )
        for termination in (termination_a, termination_z):
            self.assertEqual(termination._site, origin)
            self.assertEqual(termination._region, origin_region)
            self.assertEqual(termination._site_group, origin_group)

        parent_location.site = site
        parent_location.save()

        for termination, location in ((termination_a, parent_location), (termination_z, child_location)):
            termination.refresh_from_db()
            self.assertEqual(termination._location, location)
            self.assertEqual(termination._site, site)
            self.assertEqual(termination._region, region)
            self.assertEqual(termination._site_group, group)

    def test_creating_location_does_not_attempt_to_propagate(self):
        # Should not raise — newly-created locations have no descendants.
        Location.objects.create(name='New', slug='new', site=self.site_a)

    def _seed_location_with_children(self):
        location = Location.objects.create(name='Parent', slug='parent', site=self.site_a)
        device = Device.objects.create(
            name='Device',
            site=self.site_a,
            location=location,
            device_type=self.device_type,
            role=self.device_role,
        )
        Interface.objects.create(device=device, name='Interface 1')
        Rack.objects.create(name='Rack', site=self.site_a, location=location)
        PowerPanel.objects.create(name='Panel', site=self.site_a, location=location)
        return location

    def test_unchanged_site_skips_propagation(self):
        # Every value the handler writes is derived from the Location's site assignment, so a
        # save which leaves it alone has nothing to propagate and must not rewrite a single
        # descendant row. Rewriting them is not merely wasted work: PostgreSQL writes a new
        # tuple version for every row an UPDATE matches, and holds a row lock on each for the
        # remainder of the transaction.
        location = self._seed_location_with_children()
        location.description = 'updated'

        self.assertEqual(self.capture_propagation_updates(location), set())

    def test_changed_site_propagates(self):
        # Counterpart to the test above, which would pass vacuously if these UPDATEs stopped
        # being issued (or their tables were renamed) rather than merely being skipped.
        location = self._seed_location_with_children()
        location.site = self.site_b

        self.assertEqual(self.capture_propagation_updates(location), self.propagation_tables)

    def test_raw_save_skips_propagation(self):
        # raw=True is set only by Django's loaddata pathway, whose fixture already carries the
        # denormalized values for every object it loads, so the propagation would rewrite each
        # matched row with what it already holds.
        location = self._seed_location_with_children()
        location.site = self.site_b

        self.assertEqual(self.capture_propagation_updates(location, raw=True), set())

    def test_stale_partial_save_does_not_propagate_an_unwritten_site(self):
        # A save passing update_fields writes only the fields it names, so an omitted field
        # keeps whatever the database holds no matter what the instance carries. This instance
        # was loaded before the move below, so its in-memory site is one the database no longer
        # holds and this save does not write: propagating it would push every descendant back
        # to a site the Location itself has left.
        location = self._seed_location_with_children()
        stale = Location.objects.get(pk=location.pk)
        self.assertEqual(stale.site, self.site_a)

        location.site = self.site_b
        location.save()

        stale.description = 'updated'
        self.assertEqual(
            self.capture_propagation_updates(stale, update_fields=['description']), set()
        )

        # Nothing beneath the Location was dragged back to site_a.
        self.assertEqual(Rack.objects.get(location=location).site, self.site_b)
        device = Device.objects.get(location=location)
        self.assertEqual(device.site, self.site_b)
        self.assertEqual(Interface.objects.get(device=device)._site, self.site_b)

    def test_partial_save_naming_the_field_still_propagates(self):
        # The converse of the test above: a save which really did write the site must still
        # propagate. update_fields may name a foreign key by its field name...
        location = self._seed_location_with_children()
        location.site = self.site_b

        self.assertEqual(
            self.capture_propagation_updates(location, update_fields=['site']),
            self.propagation_tables,
        )

    def test_partial_save_naming_the_attname_still_propagates(self):
        # ...or by its attname, which Django accepts equally. Deciding whether a guarded field
        # was written has to recognise both spellings, or a real move named this way would be
        # mistaken for an unwritten field and silently skipped.
        location = self._seed_location_with_children()
        location.site = self.site_b

        self.assertEqual(
            self.capture_propagation_updates(location, update_fields=['site_id']),
            self.propagation_tables,
        )

    def test_raw_save_does_not_reuse_a_previous_saves_stash(self):
        # A raw save takes no stash of its own, so it must clear the one left by the previous
        # save of the same instance: comparing against a snapshot of the database as it stood
        # before an earlier write can report the propagated fields as unchanged when they are
        # not. The raw guard above means no handler consults the stash on this save, making the
        # clearing defensive — but it keeps the invariant that a stash never outlives its save,
        # so a later reader cannot be handed a stale one.
        location = self._seed_location_with_children()
        location.save()
        self.assertIsNotNone(location._presave_scope_fields)

        location.save_base(raw=True)

        self.assertIsNone(location._presave_scope_fields)


class LocationSiteChangeAutocommitTestCase(TransactionTestCase):
    """
    Exercise the autocommit save path, which TestCase cannot reach (it wraps every test in a
    transaction). Outside an atomic block the pre-save read and the save's UPDATE run in
    separate transactions, so the skip guard is disabled there: the stash is cleared and the
    propagation runs unconditionally.

    Note: TransactionTestCase teardown flushes all tables, which removes rows seeded by data
    migrations from a --keepdb database (e.g. the dcim.0206 ModuleTypeProfiles). A fresh test
    database restores them.
    """

    def test_autocommit_noop_save_always_propagates(self):
        site = Site.objects.create(name='Site', slug='site')
        other_site = Site.objects.create(name='Other Site', slug='other-site')
        manufacturer = Manufacturer.objects.create(name='Manufacturer', slug='manufacturer')
        device_type = DeviceType.objects.create(manufacturer=manufacturer, model='Device Type')
        device_role = DeviceRole.objects.create(name='Device Role', slug='device-role')
        location = Location.objects.create(name='Loc', slug='loc', site=site)
        device = Device.objects.create(
            name='Device', site=site, location=location, device_type=device_type, role=device_role
        )
        interface = Interface.objects.create(device=device, name='Interface 1')

        # A transactional save first, so the instance carries a stash. The subsequent
        # autocommit save must clear it rather than compare against a previous save's values.
        with transaction.atomic():
            location.save()

        # Poison a propagated column via a signal-less update; an unconditional propagation
        # repairs it, and the components follow via the trigger on dcim_device.
        Device.objects.filter(pk=device.pk).update(site=other_site)
        Interface.objects.filter(pk=interface.pk).update(_site=other_site)

        location.save()  # Autocommit: no stash, unconditional propagation

        device.refresh_from_db()
        interface.refresh_from_db()
        self.assertEqual(device.site, site)
        self.assertEqual(interface._site, site)


class RackSiteChangeSignalTestCase(ScopePropagationCaptureMixin, TestCase):
    """
    Verify dcim.signals.handle_rack_site_change propagates a Rack's site/location to its
    Devices and their components when the Rack is moved, and only then.
    """
    propagation_tables = frozenset({'dcim_device'})

    @classmethod
    def setUpTestData(cls):
        cls.site_a = Site.objects.create(name='Site A', slug='site-a')
        cls.site_b = Site.objects.create(name='Site B', slug='site-b')
        cls.location_b = Location.objects.create(name='Loc B', slug='loc-b', site=cls.site_b)
        manufacturer = Manufacturer.objects.create(name='Manufacturer', slug='manufacturer')
        cls.device_type = DeviceType.objects.create(manufacturer=manufacturer, model='Device Type')
        cls.device_role = DeviceRole.objects.create(name='Device Role', slug='device-role')

    def test_changing_rack_site_propagates_to_devices_and_components(self):
        rack = Rack.objects.create(name='Rack', site=self.site_a)
        device = Device.objects.create(
            name='Device',
            site=self.site_a,
            rack=rack,
            device_type=self.device_type,
            role=self.device_role,
        )
        interface = Interface.objects.create(device=device, name='Interface 1')

        rack.site = self.site_b
        rack.location = self.location_b
        rack.save()

        device.refresh_from_db()
        interface.refresh_from_db()
        self.assertEqual(device.site, self.site_b)
        self.assertEqual(device.location, self.location_b)
        self.assertEqual(interface._site, self.site_b)
        self.assertEqual(interface._location, self.location_b)

    def _seed_rack_with_devices(self):
        rack = Rack.objects.create(name='Rack', site=self.site_a)
        device = Device.objects.create(
            name='Device',
            site=self.site_a,
            rack=rack,
            device_type=self.device_type,
            role=self.device_role,
        )
        Interface.objects.create(device=device, name='Interface 1')
        return rack

    def test_unchanged_scope_skips_propagation(self):
        # Both values the handler writes are derived from the Rack's site and location
        # assignments, so a save which leaves both alone must not rewrite a single device or
        # component row.
        rack = self._seed_rack_with_devices()
        rack.description = 'updated'

        self.assertEqual(self.capture_propagation_updates(rack), set())

    def test_changed_site_propagates(self):
        # Counterpart to the test above, which would pass vacuously if these UPDATEs stopped
        # being issued (or their tables were renamed) rather than merely being skipped.
        rack = self._seed_rack_with_devices()
        rack.site = self.site_b

        self.assertEqual(self.capture_propagation_updates(rack), self.propagation_tables)

    def test_changed_location_propagates(self):
        # Location moves within the same Site must propagate too: the guard covers both
        # fields, not just the Site.
        rack = self._seed_rack_with_devices()
        rack.site = self.site_b
        rack.save()
        rack.location = self.location_b

        self.assertEqual(self.capture_propagation_updates(rack), self.propagation_tables)

    def test_raw_save_skips_propagation(self):
        # raw=True is set only by Django's loaddata pathway, whose fixture already carries the
        # denormalized values for every object it loads, so the propagation would rewrite each
        # matched row with what it already holds.
        rack = self._seed_rack_with_devices()
        rack.site = self.site_b

        self.assertEqual(self.capture_propagation_updates(rack, raw=True), set())

    def test_stale_partial_save_does_not_propagate_an_unwritten_scope(self):
        # As for Location: this instance was loaded before the move below, so neither of its
        # in-memory scope values is one this save writes, and neither may be propagated.
        rack = self._seed_rack_with_devices()
        stale = Rack.objects.get(pk=rack.pk)

        rack.site = self.site_b
        rack.location = self.location_b
        rack.save()

        stale.description = 'updated'
        self.assertEqual(
            self.capture_propagation_updates(stale, update_fields=['description']), set()
        )

        device = Device.objects.get(rack=rack)
        self.assertEqual(device.site, self.site_b)
        self.assertEqual(device.location, self.location_b)
        interface = Interface.objects.get(device=device)
        self.assertEqual(interface._site, self.site_b)
        self.assertEqual(interface._location, self.location_b)


class StashedScopeFieldsRegistrationTestCase(TestCase):
    """
    Verify cache_presave_scope_fields() is connected for every model in
    signals.STASHED_SCOPE_FIELDS, and that each entry's fields resolve. An entry whose
    receiver was never connected would leave the post_save handlers reading its stash
    finding none, and doing their work unconditionally on every save.
    """

    @classmethod
    def setUpTestData(cls):
        site = Site.objects.create(name='Site', slug='site')
        location = Location.objects.create(name='Location', slug='location', site=site)
        cls.instances = {
            Location: location,
            Rack: Rack.objects.create(name='Rack', site=site, location=location),
        }

    def test_every_mapped_model_stashes_its_fields_on_save(self):
        # TestCase wraps each test in a transaction, so every save below takes a stash.
        self.assertEqual(set(self.instances), set(signals.STASHED_SCOPE_FIELDS))

        for model, fields in signals.STASHED_SCOPE_FIELDS.items():
            with self.subTest(model=model.__name__):
                instance = self.instances[model]
                instance.save()

                self.assertEqual(instance._presave_scope_fields.keys(), set(fields))

    def test_every_mapped_field_resolves_to_both_spellings(self):
        # STASHED_FIELD_ALIASES is derived from the model meta, so a field name which stopped
        # resolving would drop out of it silently — and a field missing from it is one that
        # update_fields can never mark as written, permanently skipping its propagation.
        self.assertEqual(set(signals.STASHED_FIELD_ALIASES), set(signals.STASHED_SCOPE_FIELDS))

        for model, fields in signals.STASHED_SCOPE_FIELDS.items():
            with self.subTest(model=model.__name__):
                aliases = signals.STASHED_FIELD_ALIASES[model]
                self.assertEqual(set(aliases), set(fields))
                for attname, names in aliases.items():
                    # Both the field name and its attname, which update_fields may use
                    # interchangeably.
                    field = model._meta.get_field(attname.removesuffix('_id'))
                    self.assertEqual(names, frozenset((field.name, field.attname)))


class ScopeSignalConnectionTestCase(TestCase):
    """
    Verify the scope-propagation handlers issue every query against the connection the
    saved object was written to, rather than letting DATABASE_ROUTERS select one. On an
    installation with routers configured (e.g. netbox_branching), a routed query both
    writes to the wrong database and falls outside the transaction opened by the handler,
    which makes the handler's select_for_update() raise.
    """

    @classmethod
    def setUpTestData(cls):
        cls.site_a = Site.objects.create(name='Site A', slug='site-a')
        cls.site_b = Site.objects.create(name='Site B', slug='site-b')
        manufacturer = Manufacturer.objects.create(name='Manufacturer', slug='manufacturer')
        cls.device_type = DeviceType.objects.create(manufacturer=manufacturer, model='Device Type')
        cls.device_role = DeviceRole.objects.create(name='Device Role', slug='device-role')

    def test_location_save_pins_queries_to_saving_connection(self):
        parent = Location.objects.create(name='Parent', slug='parent', site=self.site_a)
        child = Location.objects.create(name='Child', slug='child', site=self.site_a, parent=parent)
        rack = Rack.objects.create(name='Rack', site=self.site_a, location=parent)
        device = Device.objects.create(
            name='Device',
            site=self.site_a,
            location=parent,
            device_type=self.device_type,
            role=self.device_role,
        )
        interface = Interface.objects.create(device=device, name='Interface 1')
        power_panel = PowerPanel.objects.create(name='Panel', site=self.site_a, location=parent)
        cluster_type = ClusterType.objects.create(name='Cluster Type', slug='cluster-type')
        cluster = Cluster.objects.create(name='Cluster', type=cluster_type, scope=child)

        # Re-fetch and assign the new Site by ID, leaving the site relation uncached: a
        # handler which reads instance.site rather than instance.site_id would fetch it
        # over a routed connection, which is what the Site entry below catches.
        parent = Location.objects.get(pk=parent.pk)
        parent.site_id = self.site_b.pk
        router = PinnedConnectionRouter(
            CableTermination,
            CircuitTermination,
            Cluster,
            Device,
            Interface,
            PowerPanel,
            Prefix,
            Rack,
            Site,
            WirelessLAN,
        )
        with override_settings(DATABASE_ROUTERS=[router]):
            parent.save()

        for obj in (child, rack, device, power_panel):
            obj.refresh_from_db()
            self.assertEqual(obj.site, self.site_b)
        interface.refresh_from_db()
        self.assertEqual(interface._site, self.site_b)
        cluster.refresh_from_db()
        self.assertEqual(cluster._site, self.site_b)

    def test_rack_save_pins_queries_to_saving_connection(self):
        rack = Rack.objects.create(name='Rack', site=self.site_a)
        device = Device.objects.create(
            name='Device',
            site=self.site_a,
            rack=rack,
            device_type=self.device_type,
            role=self.device_role,
        )
        interface = Interface.objects.create(device=device, name='Interface 1')

        rack = Rack.objects.get(pk=rack.pk)
        rack.site_id = self.site_b.pk
        router = PinnedConnectionRouter(CableTermination, Device, Interface, Site)
        with override_settings(DATABASE_ROUTERS=[router]):
            rack.save()

        device.refresh_from_db()
        interface.refresh_from_db()
        self.assertEqual(device.site, self.site_b)
        self.assertEqual(interface._site, self.site_b)


class DeviceComponentScopeTriggerTestCase(TestCase):
    """
    Verify the PostgreSQL trigger (dcim migration 0239) that propagates a Device's site/location/rack
    onto its components' denormalized _site/_location/_rack columns. This replaces the former
    dcim.signals.handle_device_site_change handler.
    """

    @classmethod
    def setUpTestData(cls):
        cls.site_a = Site.objects.create(name='Site A', slug='site-a')
        cls.site_b = Site.objects.create(name='Site B', slug='site-b')
        manufacturer = Manufacturer.objects.create(name='Manufacturer', slug='manufacturer')
        cls.device_type = DeviceType.objects.create(manufacturer=manufacturer, model='Device Type')
        cls.device_role = DeviceRole.objects.create(name='Device Role', slug='device-role')

    def test_moving_device_updates_components_cached_scope(self):
        device = Device.objects.create(
            name='Device',
            site=self.site_a,
            device_type=self.device_type,
            role=self.device_role,
        )
        interface = Interface.objects.create(device=device, name='Interface 1')
        self.assertEqual(interface._site, self.site_a)

        device.site = self.site_b
        device.save()

        interface.refresh_from_db()
        self.assertEqual(interface._site, self.site_b)

    def test_bulk_update_of_device_updates_components_cached_scope(self):
        """
        A bulk QuerySet.update() bypasses post_save (the old handler never fired for it); the DB
        trigger fires regardless. This is also the path the Rack/Location cascades take.
        """
        device = Device.objects.create(
            name='Device',
            site=self.site_a,
            device_type=self.device_type,
            role=self.device_role,
        )
        interface = Interface.objects.create(device=device, name='Interface 1')
        self.assertEqual(interface._site, self.site_a)

        Device.objects.filter(pk=device.pk).update(site=self.site_b)

        interface.refresh_from_db()
        self.assertEqual(interface._site, self.site_b)


class VirtualChassisMasterSignalTestCase(TestCase):
    """
    Verify dcim.signals.assign_virtualchassis_master links the master device back to a
    newly-created VirtualChassis.
    """

    @classmethod
    def setUpTestData(cls):
        cls.site = Site.objects.create(name='Site', slug='site')
        manufacturer = Manufacturer.objects.create(name='Manufacturer', slug='manufacturer')
        cls.device_type = DeviceType.objects.create(manufacturer=manufacturer, model='Device Type')
        cls.device_role = DeviceRole.objects.create(name='Device Role', slug='device-role')

    def test_master_is_assigned_to_new_virtual_chassis(self):
        master = Device.objects.create(
            name='Master',
            site=self.site,
            device_type=self.device_type,
            role=self.device_role,
        )
        vc = VirtualChassis.objects.create(name='VC 1', master=master)

        master.refresh_from_db()
        self.assertEqual(master.virtual_chassis, vc)
        self.assertEqual(master.vc_position, 1)

    def test_updating_virtual_chassis_does_not_reassign_master(self):
        master = Device.objects.create(
            name='Master',
            site=self.site,
            device_type=self.device_type,
            role=self.device_role,
        )
        vc = VirtualChassis.objects.create(name='VC 1', master=master)

        # Detach the master, then save the VC again — the signal should not re-link.
        master.virtual_chassis = None
        master.vc_position = None
        master.save()

        vc.domain = 'updated'
        vc.save()

        master.refresh_from_db()
        self.assertIsNone(master.virtual_chassis)


class CableSignalTestCase(TestCase):
    """
    Verify dcim.signals.update_connected_endpoints, retrace_cable_paths, and
    nullify_connected_endpoints maintain CablePaths in response to Cable lifecycle events.
    """

    @classmethod
    def setUpTestData(cls):
        cls.site = Site.objects.create(name='Site', slug='site')
        manufacturer = Manufacturer.objects.create(name='Manufacturer', slug='manufacturer')
        device_type = DeviceType.objects.create(manufacturer=manufacturer, model='Device Type')
        role = DeviceRole.objects.create(name='Device Role', slug='device-role')
        cls.device = Device.objects.create(
            name='Device',
            site=cls.site,
            device_type=device_type,
            role=role,
        )

    def test_creating_cable_creates_endpoint_paths(self):
        interface_a = Interface.objects.create(device=self.device, name='Interface A')
        interface_b = Interface.objects.create(device=self.device, name='Interface B')
        cable = Cable(a_terminations=[interface_a], b_terminations=[interface_b])
        cable.save()

        self.assertEqual(CablePath.objects.count(), 2)
        interface_a.refresh_from_db()
        self.assertIsNotNone(interface_a._path_id)

    def test_changing_cable_status_marks_paths_inactive(self):
        interface_a = Interface.objects.create(device=self.device, name='Interface A')
        interface_b = Interface.objects.create(device=self.device, name='Interface B')
        cable = Cable(a_terminations=[interface_a], b_terminations=[interface_b])
        cable.save()
        self.assertTrue(all(cp.is_active for cp in CablePath.objects.all()))

        # Reload to exercise status tracking on a freshly loaded instance, as a request does
        cable = Cable.objects.get(pk=cable.pk)
        cable.status = LinkStatusChoices.STATUS_PLANNED
        cable.save()

        self.assertFalse(any(cp.is_active for cp in CablePath.objects.all()))

    def test_reconnecting_cable_marks_paths_active(self):
        interface_a = Interface.objects.create(device=self.device, name='Interface A')
        interface_b = Interface.objects.create(device=self.device, name='Interface B')
        cable = Cable(
            a_terminations=[interface_a],
            b_terminations=[interface_b],
            status=LinkStatusChoices.STATUS_PLANNED,
        )
        cable.save()
        self.assertFalse(any(cp.is_active for cp in CablePath.objects.all()))

        cable = Cable.objects.get(pk=cable.pk)
        cable.status = LinkStatusChoices.STATUS_CONNECTED
        cable.save()

        self.assertTrue(all(cp.is_active for cp in CablePath.objects.all()))

    def test_toggling_cable_status_on_one_instance_reactivates_paths(self):
        interface_a = Interface.objects.create(device=self.device, name='Interface A')
        interface_b = Interface.objects.create(device=self.device, name='Interface B')
        cable = Cable(a_terminations=[interface_a], b_terminations=[interface_b])
        cable.save()

        # Reuse the same instance for both changes, as a script would
        cable = Cable.objects.get(pk=cable.pk)
        cable.status = LinkStatusChoices.STATUS_PLANNED
        cable.save()
        self.assertFalse(any(cp.is_active for cp in CablePath.objects.all()))

        cable.status = LinkStatusChoices.STATUS_CONNECTED
        cable.save()
        self.assertTrue(all(cp.is_active for cp in CablePath.objects.all()))

    def test_partial_save_does_not_consume_an_unwritten_status_change(self):
        interface_a = Interface.objects.create(device=self.device, name='Interface A')
        interface_b = Interface.objects.create(device=self.device, name='Interface B')
        cable = Cable(
            a_terminations=[interface_a],
            b_terminations=[interface_b],
            status=LinkStatusChoices.STATUS_PLANNED,
        )
        cable.save()
        self.assertFalse(any(cp.is_active for cp in CablePath.objects.all()))

        # A save that excludes status must not advance the status snapshot
        cable.status = LinkStatusChoices.STATUS_CONNECTED
        cable.save(update_fields=['label'])
        self.assertFalse(any(cp.is_active for cp in CablePath.objects.all()))

        # _orig_status was not advanced, so the change must still be detected
        cable.save()
        self.assertTrue(all(cp.is_active for cp in CablePath.objects.all()))

    def test_deleting_cable_retraces_paths(self):
        interface_a = Interface.objects.create(device=self.device, name='Interface A')
        interface_b = Interface.objects.create(device=self.device, name='Interface B')
        cable = Cable(a_terminations=[interface_a], b_terminations=[interface_b])
        cable.save()
        self.assertEqual(CablePath.objects.count(), 2)

        cable.delete()
        self.assertEqual(CablePath.objects.count(), 0)
        interface_a.refresh_from_db()
        interface_b.refresh_from_db()
        # Cable deletion must fully detach both endpoints, even though the
        # nullify_connected_endpoints signal short-circuits during Cable cascade.
        self.assertIsNone(interface_a._path_id)
        self.assertIsNone(interface_b._path_id)
        self.assertIsNone(interface_a.cable_id)
        self.assertIsNone(interface_b.cable_id)
        self.assertIsNone(interface_a.cable_end)
        self.assertIsNone(interface_b.cable_end)

    def test_deleting_profiled_cable_nullifies_endpoints(self):
        """
        Deleting a profiled cable must clear the cached connector and position data on both endpoints.
        """
        interface_a = Interface.objects.create(device=self.device, name='Interface A')
        interface_b = Interface.objects.create(device=self.device, name='Interface B')
        cable = Cable(
            a_terminations=[interface_a],
            b_terminations=[interface_b],
            profile=CableProfileChoices.SINGLE_1C1P,
        )
        cable.save()

        # Confirm the profile metadata was cached on both endpoints.
        interface_a.refresh_from_db()
        interface_b.refresh_from_db()
        self.assertEqual(interface_a.cable_connector, 1)
        self.assertEqual(interface_a.cable_positions, [1])
        self.assertEqual(interface_b.cable_connector, 1)
        self.assertEqual(interface_b.cable_positions, [1])

        cable.delete()

        for interface in (interface_a, interface_b):
            interface.refresh_from_db()
            self.assertIsNone(interface.cable_id)
            self.assertIsNone(interface.cable_end)
            self.assertIsNone(interface.cable_connector)
            self.assertIsNone(interface.cable_positions)

    def test_deleting_cable_skips_per_termination_retrace(self):
        """
        When a Cable is deleted, nullify_connected_endpoints (post_delete on each
        cascaded CableTermination) must skip retracing — retrace_cable_paths
        retraces each affected path once on Cable post_delete instead. See #22104.

        Without the short-circuit, retrace would fire (n_terminations * n_paths)
        times from the per-termination handler plus n_paths times from the Cable
        handler — for this 2-termination, 2-path cable, 6 calls total. With the
        short-circuit, only the n_paths calls from retrace_cable_paths remain.
        """
        interface_a = Interface.objects.create(device=self.device, name='Interface A')
        interface_b = Interface.objects.create(device=self.device, name='Interface B')
        cable = Cable(a_terminations=[interface_a], b_terminations=[interface_b])
        cable.save()
        self.assertEqual(CablePath.objects.count(), 2)
        self.assertFalse(Cable._is_being_deleted(cable.pk))

        with patch('dcim.models.cables.CablePath.retrace') as retrace:
            cable.delete()

        # Exactly one retrace per affected CablePath (from retrace_cable_paths),
        # not the n*m calls the per-termination handler would have made.
        self.assertEqual(retrace.call_count, 2)
        # The deletion-tracking set must be cleaned up after delete() returns,
        # even when the cascade runs to completion.
        self.assertFalse(Cable._is_being_deleted(cable.pk))

    def test_creating_portmapping_retraces_dependent_paths(self):
        interface = Interface.objects.create(device=self.device, name='Interface A')
        front_port = FrontPort.objects.create(device=self.device, name='Front Port 1')
        rear_port = RearPort.objects.create(device=self.device, name='Rear Port 1')
        Cable(a_terminations=[interface], b_terminations=[front_port]).save()

        # Creating a PortMapping connecting the front and rear ports should retrace paths
        # that traverse either port (i.e. the incomplete path through front_port).
        PortMapping.objects.create(
            device=self.device,
            front_port=front_port,
            front_port_position=1,
            rear_port=rear_port,
            rear_port_position=1,
        )

        path = CablePath.objects.filter(_nodes__contains=front_port).first()
        self.assertIsNotNone(path)
        # The retraced path should now extend through to the rear port. Path nodes are
        # encoded as "<content_type_id>:<object_id>".
        rear_port_node = f'{ContentType.objects.get_for_model(RearPort).pk}:{rear_port.pk}'
        flat_nodes = [n for step in path.path for n in step]
        self.assertIn(rear_port_node, flat_nodes)

    def test_deleting_cabletermination_nullifies_endpoints(self):
        interface_a = Interface.objects.create(device=self.device, name='Interface A')
        interface_b = Interface.objects.create(device=self.device, name='Interface B')
        cable = Cable(a_terminations=[interface_a], b_terminations=[interface_b])
        cable.save()
        termination = cable.terminations.get(cable_end=CableEndChoices.SIDE_A)

        termination.delete()
        interface_a.refresh_from_db()
        self.assertIsNone(interface_a.cable_id)
        self.assertIsNone(interface_a.cable_end)


class MACAddressInterfaceSignalTestCase(TestCase):
    """
    Verify dcim.signals.update_mac_address_interface assigns a designated primary MAC to
    the newly-created Interface or VMInterface.
    """

    @classmethod
    def setUpTestData(cls):
        cls.site = Site.objects.create(name='Site', slug='site')
        manufacturer = Manufacturer.objects.create(name='Manufacturer', slug='manufacturer')
        device_type = DeviceType.objects.create(manufacturer=manufacturer, model='Device Type')
        role = DeviceRole.objects.create(name='Device Role', slug='device-role')
        cls.device = Device.objects.create(
            name='Device',
            site=cls.site,
            device_type=device_type,
            role=role,
        )

    def test_primary_mac_is_assigned_to_new_interface(self):
        mac = MACAddress.objects.create(mac_address='00:11:22:33:44:55')
        interface = Interface(device=self.device, name='Interface 1', primary_mac_address=mac)
        interface.save()

        mac.refresh_from_db()
        self.assertEqual(mac.assigned_object, interface)

    def test_primary_mac_is_not_reassigned_on_interface_update(self):
        mac = MACAddress.objects.create(mac_address='00:11:22:33:44:55')
        interface = Interface.objects.create(device=self.device, name='Interface 1')
        mac.assigned_object = interface
        mac.save()
        # Detach (simulate the MAC having been moved off the interface).
        mac.assigned_object = None
        mac.save()

        interface.primary_mac_address = mac
        interface.description = 'updated'
        interface.save()

        mac.refresh_from_db()
        # Updating an existing interface should not re-assign the MAC.
        self.assertIsNone(mac.assigned_object)


class CachedScopeFieldTriggerTestCase(TestCase):
    """
    Verify the PostgreSQL triggers (ipam/virtualization/wireless denormalization migrations) that keep
    the CachedScopeMixin scope columns (_site/_location/_region/_site_group) on Prefix, Cluster, and
    WirelessLAN in sync when a scoped Site or Location is modified. These replace the former
    dcim.signals.sync_cached_scope_fields handler.
    """

    def test_site_group_change_updates_prefix_cached_scope(self):
        group_a = SiteGroup.objects.create(name='Group A', slug='group-a')
        group_b = SiteGroup.objects.create(name='Group B', slug='group-b')
        site = Site.objects.create(name='Site', slug='site', group=group_a)
        prefix = Prefix.objects.create(
            prefix='10.0.0.0/24',
            scope_type=ContentType.objects.get_for_model(Site),
            scope_id=site.pk,
        )
        self.assertEqual(prefix._site_group, group_a)

        site.group = group_b
        site.save()

        prefix.refresh_from_db()
        self.assertEqual(prefix._site, site)
        self.assertEqual(prefix._site_group, group_b)

    def test_location_site_change_updates_prefix_cached_scope(self):
        site_a = Site.objects.create(name='Site A', slug='site-a')
        site_b = Site.objects.create(name='Site B', slug='site-b')
        location = Location.objects.create(name='Loc', slug='loc', site=site_a)
        prefix = Prefix.objects.create(
            prefix='10.0.0.0/24',
            scope_type=ContentType.objects.get_for_model(Location),
            scope_id=location.pk,
        )
        self.assertEqual(prefix._site, site_a)
        self.assertEqual(prefix._location, location)

        location.site = site_b
        location.save()

        prefix.refresh_from_db()
        self.assertEqual(prefix._location, location)
        self.assertEqual(prefix._site, site_b)

    def test_triggers_update_cluster_and_wirelesslan_cached_scope(self):
        # Cluster and WirelessLAN each carry their own Site/Location triggers (installed by the
        # virtualization and wireless denormalization migrations); exercise both alongside Prefix.
        group_a = SiteGroup.objects.create(name='Group A', slug='group-a')
        group_b = SiteGroup.objects.create(name='Group B', slug='group-b')
        site = Site.objects.create(name='Site', slug='site', group=group_a)
        cluster_type = ClusterType.objects.create(name='CT', slug='ct')
        cluster = Cluster.objects.create(name='Cluster', type=cluster_type, scope=site)
        wireless_lan = WirelessLAN.objects.create(ssid='LAN', scope=site)

        self.assertEqual(cluster._site_group, group_a)
        self.assertEqual(wireless_lan._site_group, group_a)

        site.group = group_b
        site.save()

        cluster.refresh_from_db()
        wireless_lan.refresh_from_db()
        self.assertEqual(cluster._site_group, group_b)
        self.assertEqual(wireless_lan._site_group, group_b)

    def test_create_site_does_not_attempt_to_resync(self):
        # Should not raise — newly-created sites have nothing to sync.
        Site.objects.create(name='New Site', slug='new-site')


class CableSignalDirectHandlerTestCase(SimpleTestCase):
    """
    Direct-call tests for dcim signal branches that are not reachable through normal
    model operations (raw=True is set only by Django's loaddata pathway).
    """

    def test_update_connected_endpoints_raw_import_is_a_no_op(self):
        cable = SimpleNamespace(_terminations_modified=True)
        logger = MagicMock()

        with (
            patch.object(signals.logging, 'getLogger', return_value=logger),
            patch.object(signals, 'CableTermination') as cabletermination_model,
            patch.object(signals, 'create_cablepaths') as create_cablepaths,
            patch.object(signals, 'rebuild_paths') as rebuild_paths,
        ):
            signals.update_connected_endpoints(instance=cable, created=True, raw=True)

        logger.debug.assert_called_once()
        cabletermination_model.objects.filter.assert_not_called()
        create_cablepaths.assert_not_called()
        rebuild_paths.assert_not_called()

    def test_update_mac_address_interface_raw_import_is_a_no_op(self):
        primary_mac = SimpleNamespace(save=MagicMock())
        interface = SimpleNamespace(primary_mac_address=primary_mac)

        signals.update_mac_address_interface(instance=interface, created=True, raw=True)

        primary_mac.save.assert_not_called()


class CableTerminationDenormalizationTriggerTestCase(TestCase):
    """
    Verify the PostgreSQL triggers (installed by dcim migration 0239) that keep a
    CableTermination's denormalized _device/_rack/_location/_site columns in sync with the
    parent Device/Rack/Location.

    These replace the former Python `post_save` handler in netbox.denormalized. Crucially,
    the triggers also fire for bulk QuerySet.update() writes — which the handler (a post_save
    receiver) never saw — so this exercises that path explicitly.
    """

    @classmethod
    def setUpTestData(cls):
        cls.site_a = Site.objects.create(name='Site A', slug='site-a')
        cls.site_b = Site.objects.create(name='Site B', slug='site-b')
        cls.location_b = Location.objects.create(name='Loc B', slug='loc-b', site=cls.site_b)
        cls.rack_b = Rack.objects.create(name='Rack B', site=cls.site_b, location=cls.location_b)
        manufacturer = Manufacturer.objects.create(name='Manufacturer', slug='manufacturer')
        cls.device_type = DeviceType.objects.create(manufacturer=manufacturer, model='Device Type')
        cls.device_role = DeviceRole.objects.create(name='Device Role', slug='device-role')

    def _connected_termination(self):
        device = Device.objects.create(
            name='Device', site=self.site_a, device_type=self.device_type, role=self.device_role,
        )
        interface_a = Interface.objects.create(device=device, name='Interface A')
        interface_b = Interface.objects.create(device=device, name='Interface B')
        cable = Cable(a_terminations=[interface_a], b_terminations=[interface_b])
        cable.save()
        termination = CableTermination.objects.filter(_device=device).first()
        self.assertIsNotNone(termination)
        self.assertEqual(termination._site, self.site_a)
        return device, termination

    def test_device_move_propagates_to_cable_termination(self):
        device, termination = self._connected_termination()

        device.site = self.site_b
        device.location = self.location_b
        device.rack = self.rack_b
        device.save()

        termination.refresh_from_db()
        self.assertEqual(termination._site, self.site_b)
        self.assertEqual(termination._location, self.location_b)
        self.assertEqual(termination._rack, self.rack_b)

    def test_bulk_update_of_device_propagates_to_cable_termination(self):
        """
        A bulk QuerySet.update() bypasses post_save (the old handler never fired for it);
        the DB trigger fires regardless.
        """
        device, termination = self._connected_termination()

        Device.objects.filter(pk=device.pk).update(site=self.site_b)

        termination.refresh_from_db()
        self.assertEqual(termination._site, self.site_b)


def _concrete_subclasses(base):
    """
    Yield every non-abstract, non-plugin model descending from an abstract base model. Plugin-contributed
    models are skipped: a plugin that adds a ComponentModel/CachedScopeMixin subclass is responsible for
    its own trigger migration, and must not fail core's coverage check just by being installed.
    """
    for subclass in base.__subclasses__():
        if subclass._meta.abstract:
            yield from _concrete_subclasses(subclass)
        elif not isinstance(apps.get_app_config(subclass._meta.app_label), PluginConfig):
            yield subclass


def _installed_triggers():
    with connection.cursor() as cursor:
        cursor.execute('SELECT tgname FROM pg_trigger WHERE NOT tgisinternal')
        return {row[0] for row in cursor.fetchall()}


class DenormalizationTriggerCoverageTestCase(TestCase):
    """
    Guard against a new core model silently shipping without its denormalization triggers. The set of
    device-component tables and CachedScopeMixin dependents is hand-listed in migrations; this test
    derives those sets from the model layer and asserts the expected triggers are installed, so adding
    a new component / scoped model without a matching trigger migration fails CI. Plugin-contributed
    models are excluded (see _concrete_subclasses).
    """

    def test_device_components_have_device_trigger(self):
        triggers = _installed_triggers()
        for model in _concrete_subclasses(ComponentModel):
            table = model._meta.db_table
            self.assertIn(
                f'{table}_denorm_from_dcim_device', triggers,
                msg=f'{model.__name__} has no dcim_device denormalization trigger (add it to '
                    f'dcim migration 0239 COMPONENT_TABLES)',
            )

    def test_cached_scope_models_have_site_and_location_triggers(self):
        triggers = _installed_triggers()
        for model in _concrete_subclasses(CachedScopeMixin):
            table = model._meta.db_table
            for source in ('dcim_site', 'dcim_location'):
                self.assertIn(
                    f'{table}_denorm_from_{source}', triggers,
                    msg=f'{model.__name__} (CachedScopeMixin) has no {source} denormalization trigger; '
                        f'add cached_scope_triggers({table!r}) in a migration for its app',
                )
