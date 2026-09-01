from types import SimpleNamespace
from unittest.mock import MagicMock, patch

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
from ipam.models import Prefix
from utilities.testing import PinnedConnectionRouter
from virtualization.models import Cluster, ClusterType
from wireless.models import WirelessLAN

COMPONENT_TABLES = frozenset(model._meta.db_table for model in signals.COMPONENT_MODELS)


class ScopePropagationCaptureMixin:
    """
    Helper for asserting whether a save propagated to the tables its post_save handler
    rewrites.

    dcim_cabletermination is never among them: the denormalized-field registry
    (netbox.denormalized) rewrites it on Location, Rack, and Device saves alike, so it
    cannot distinguish a propagation from a plain save. Neither is the saved object's own
    table, which carries the save's own UPDATE.
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
            if q['sql'].startswith(f'UPDATE "{table}"')
        }


class LocationSiteChangeSignalTestCase(ScopePropagationCaptureMixin, TestCase):
    """
    Verify dcim.signals.handle_location_site_change propagates a Location's new Site to
    every descendant Location, Rack, Device, PowerPanel, and component when the parent
    Location's site assignment changes.
    """
    propagation_tables = COMPONENT_TABLES | {'dcim_rack', 'dcim_device', 'dcim_powerpanel'}

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
        # rather than under CachedScopeMixin's scope field, so sync_cached_scope_fields does
        # not cover it and the denormalized-field registry refreshes only _site. Both the
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
        # matched row with what it already holds. netbox.denormalized.update_denormalized_fields()
        # returns early on raw for the same reason.
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

        # Poison a cached column via a signal-less update; an unconditional propagation
        # repairs it.
        Interface.objects.filter(pk=interface.pk).update(_site=other_site)

        location.save()  # Autocommit: no stash, unconditional propagation

        interface.refresh_from_db()
        self.assertEqual(interface._site, site)


class RackSiteChangeSignalTestCase(ScopePropagationCaptureMixin, TestCase):
    """
    Verify dcim.signals.handle_rack_site_change propagates a Rack's site/location to its
    Devices and their components when the Rack is moved, and only then.
    """
    propagation_tables = COMPONENT_TABLES | {'dcim_device'}

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
        cls.instances = {}
        site = Site.objects.create(name='Site', slug='site')
        location = Location.objects.create(name='Location', slug='location', site=site)
        rack = Rack.objects.create(name='Rack', site=site, location=location)
        manufacturer = Manufacturer.objects.create(name='Manufacturer', slug='manufacturer')
        cls.instances = {
            Site: site,
            Location: location,
            Rack: rack,
            Device: Device.objects.create(
                name='Device',
                site=site,
                location=location,
                rack=rack,
                device_type=DeviceType.objects.create(manufacturer=manufacturer, model='Device Type'),
                role=DeviceRole.objects.create(name='Device Role', slug='device-role'),
            ),
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

    def test_device_save_pins_queries_to_saving_connection(self):
        device = Device.objects.create(
            name='Device',
            site=self.site_a,
            device_type=self.device_type,
            role=self.device_role,
        )
        interface = Interface.objects.create(device=device, name='Interface 1')

        device = Device.objects.get(pk=device.pk)
        device.site_id = self.site_b.pk
        with override_settings(DATABASE_ROUTERS=[PinnedConnectionRouter(CableTermination, Interface, Site)]):
            device.save()

        interface.refresh_from_db()
        self.assertEqual(interface._site, self.site_b)

    def test_site_save_pins_scope_resync_to_saving_connection(self):
        region = Region.objects.create(name='Region', slug='region')
        cluster_type = ClusterType.objects.create(name='Cluster Type', slug='cluster-type')
        # Scope the Cluster to a Location rather than to the Site itself: the rebuild then
        # has to resolve the Location behind the object's generic scope, which is the read
        # that must follow the connection the Site was saved on.
        location = Location.objects.create(name='Location', slug='location', site=self.site_a)
        cluster = Cluster.objects.create(name='Cluster', type=cluster_type, scope=location)

        site = Site.objects.get(pk=self.site_a.pk)
        site.region = region
        # Region is included to catch the Location's site.region read made while rebuilding
        # the cached fields; Site itself cannot be, as Django routes the save under test.
        router = PinnedConnectionRouter(CircuitTermination, Cluster, Location, Prefix, Region, WirelessLAN)
        with override_settings(DATABASE_ROUTERS=[router]):
            site.save()

        cluster.refresh_from_db()
        self.assertEqual(cluster._region, region)


class DeviceSiteChangeSignalTestCase(ScopePropagationCaptureMixin, TestCase):
    """
    Verify dcim.signals.handle_device_site_change propagates a Device's site/location/rack
    to its components on save, and only then.
    """
    propagation_tables = COMPONENT_TABLES

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

    def _seed_device_with_components(self):
        device = Device.objects.create(
            name='Device',
            site=self.site_a,
            device_type=self.device_type,
            role=self.device_role,
        )
        Interface.objects.create(device=device, name='Interface 1')
        return device

    def test_unchanged_scope_skips_propagation(self):
        # Components repopulate _site/_location/_rack from their Device on their own save
        # (see ComponentModel.save), so a Device save which moved the Device nowhere has
        # nothing to push down and must not rewrite a single component row.
        device = self._seed_device_with_components()
        device.description = 'updated'

        self.assertEqual(self.capture_propagation_updates(device), set())

    def test_changed_site_propagates(self):
        # Counterpart to the test above, which would pass vacuously if these UPDATEs stopped
        # being issued (or their tables were renamed) rather than merely being skipped.
        device = self._seed_device_with_components()
        device.site = self.site_b

        self.assertEqual(self.capture_propagation_updates(device), self.propagation_tables)

    def test_changed_rack_propagates(self):
        # A Rack assignment is the third guarded field, and the only one changed here: the
        # Rack is deliberately left without a Location, so Device.save() does not inherit one
        # and neither site nor location moves.
        device = self._seed_device_with_components()
        rack = Rack.objects.create(name='Rack', site=self.site_a)
        self.assertIsNone(rack.location)
        device.rack = rack

        self.assertEqual(self.capture_propagation_updates(device), self.propagation_tables)

    def test_raw_save_skips_propagation(self):
        # raw=True is set only by Django's loaddata pathway, whose fixture already carries the
        # denormalized values for every object it loads, so the propagation would rewrite each
        # matched row with what it already holds.
        device = self._seed_device_with_components()
        device.site = self.site_b

        self.assertEqual(self.capture_propagation_updates(device, raw=True), set())

    def test_stale_partial_save_does_not_propagate_an_unwritten_scope(self):
        # As for Location and Rack: this instance was loaded before the move below, so its
        # in-memory site is not one this save writes and must not reach the components.
        device = self._seed_device_with_components()
        stale = Device.objects.get(pk=device.pk)

        device.site = self.site_b
        device.save()

        stale.description = 'updated'
        self.assertEqual(
            self.capture_propagation_updates(stale, update_fields=['description']), set()
        )

        self.assertEqual(Interface.objects.get(device=device)._site, self.site_b)

    def test_stale_partial_save_propagates_written_field_with_database_values(self):
        # The mixed case, which the skip cannot cover: one guarded field is written, so the
        # propagation must run — and the two fields the save did not write have to be taken
        # from the database, not from the stale instance. Assigning the rack alone leaves the
        # site and location columns untouched, so the components must end up at site_b (where
        # the device actually is) rather than site_a (which the instance still carries).
        device = self._seed_device_with_components()
        stale = Device.objects.get(pk=device.pk)

        device.site = self.site_b
        device.save()

        # A rack in site_b with no location, so Device.save() inherits no location from it.
        rack = Rack.objects.create(name='Rack', site=self.site_b)
        self.assertIsNone(rack.location)
        stale.rack = rack

        self.assertEqual(
            self.capture_propagation_updates(stale, update_fields=['rack']),
            self.propagation_tables,
        )

        interface = Interface.objects.get(device=device)
        self.assertEqual(interface._site, self.site_b)
        self.assertEqual(interface._rack, rack)
        self.assertIsNone(interface._location)
        # The device's own site column was never rewritten by the partial save either.
        device.refresh_from_db()
        self.assertEqual(device.site, self.site_b)


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


class SyncCachedScopeFieldsSignalTestCase(TestCase):
    """
    Verify dcim.signals.sync_cached_scope_fields recomputes cached scope fields on
    Prefix, Cluster, and WirelessLAN when a Site or Location is modified.
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

    def test_signal_updates_cluster_and_wirelesslan_cached_scope(self):
        # Lock down the explicit (Prefix, Cluster, WirelessLAN) tuple in the
        # signal by exercising Cluster and WirelessLAN alongside Prefix. If a
        # future change drops Cluster or WirelessLAN from that tuple, this test
        # will catch it.
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

    def test_save_with_unchanged_scope_fields_skips_resync(self):
        group = SiteGroup.objects.create(name='Group', slug='group')
        site = Site.objects.create(name='Site', slug='site', group=group)
        location = Location.objects.create(name='Loc', slug='loc', site=site)
        prefix = Prefix.objects.create(prefix='10.0.0.0/24', scope=site)
        self.assertIsNone(prefix._location)

        # Poison a cached column via a signal-less update; a skipped resync must leave it as-is.
        # _location is poisoned (rather than _region/_site_group) because the denormalized-field
        # registry (netbox.denormalized) unconditionally rewrites those two on every Site save,
        # which would mask whether this signal ran.
        Prefix.objects.filter(pk=prefix.pk).update(_location=location)

        site.description = 'updated'
        site.save()

        prefix.refresh_from_db()
        self.assertEqual(prefix._location, location)

    def test_location_save_with_unchanged_site_skips_resync(self):
        region = Region.objects.create(name='Region', slug='region')
        site = Site.objects.create(name='Site', slug='site')
        location = Location.objects.create(name='Loc', slug='loc', site=site)
        prefix = Prefix.objects.create(prefix='10.0.0.0/24', scope=location)
        self.assertIsNone(prefix._region)

        # Poison a cached column via a signal-less update; a skipped resync must leave it as-is.
        # _region is poisoned because the denormalized-field registry unconditionally rewrites
        # _site on every Location save, which would mask whether this signal ran.
        Prefix.objects.filter(pk=prefix.pk).update(_region=region)

        location.description = 'updated'
        location.save()

        prefix.refresh_from_db()
        self.assertEqual(prefix._region, region)

    def test_save_with_changed_site_group_resyncs(self):
        group_a = SiteGroup.objects.create(name='Group A', slug='group-a')
        group_b = SiteGroup.objects.create(name='Group B', slug='group-b')
        site = Site.objects.create(name='Site', slug='site', group=group_a)
        prefix = Prefix.objects.create(prefix='10.0.0.0/24', scope=site)
        self.assertEqual(prefix._site_group, group_a)

        site.group = group_b
        site.save()

        prefix.refresh_from_db()
        self.assertEqual(prefix._site, site)
        self.assertEqual(prefix._site_group, group_b)
        self.assertIsNone(prefix._region)
        self.assertIsNone(prefix._location)

    def test_save_with_changed_region_resyncs(self):
        region_a = Region.objects.create(name='Region A', slug='region-a')
        region_b = Region.objects.create(name='Region B', slug='region-b')
        site = Site.objects.create(name='Site', slug='site', region=region_a)
        prefix = Prefix.objects.create(prefix='10.0.0.0/24', scope=site)
        self.assertEqual(prefix._region, region_a)

        site.region = region_b
        site.save()

        prefix.refresh_from_db()
        self.assertEqual(prefix._region, region_b)
        self.assertEqual(prefix._site, site)

        # A region-to-None transition must also resync.
        site.region = None
        site.save()

        prefix.refresh_from_db()
        self.assertIsNone(prefix._region)
        self.assertEqual(prefix._site, site)

    def test_location_save_with_changed_site_resyncs(self):
        site_a = Site.objects.create(name='Site A', slug='site-a')
        site_b = Site.objects.create(name='Site B', slug='site-b')
        location = Location.objects.create(name='Loc', slug='loc', site=site_a)
        prefix = Prefix.objects.create(prefix='10.0.0.0/24', scope=location)
        self.assertEqual(prefix._site, site_a)

        location.site = site_b
        location.save()

        prefix.refresh_from_db()
        self.assertEqual(prefix._site, site_b)
        self.assertEqual(prefix._location, location)

    def test_noop_save_skips_resync(self):
        site = Site.objects.create(name='Site', slug='site')
        location = Location.objects.create(name='Loc', slug='loc', site=site)
        prefix = Prefix.objects.create(prefix='10.0.0.0/24', scope=site)

        # Poison a cached column, then save the Site with no field changes. The resync is
        # skipped: the pre-save values read from the database match what is being written.
        # Stale cached values are prevented at their source (handle_location_site_change
        # repairs descendant-scoped objects), so a no-op save no longer doubles as a
        # repair mechanism. _location is poisoned because only this signal (not the
        # denormalized-field registry) could repair it on a Site save.
        Prefix.objects.filter(pk=prefix.pk).update(_location=location)

        site.save()

        prefix.refresh_from_db()
        self.assertEqual(prefix._location, location)

    def test_location_site_change_updates_descendant_scoped_caches(self):
        group_a = SiteGroup.objects.create(name='Group A', slug='group-a')
        group_b = SiteGroup.objects.create(name='Group B', slug='group-b')
        site_a = Site.objects.create(name='Site A', slug='site-a', group=group_a)
        site_b = Site.objects.create(name='Site B', slug='site-b', group=group_b)
        parent = Location.objects.create(name='Parent', slug='parent', site=site_a)
        child = Location.objects.create(name='Child', slug='child', site=site_a, parent=parent)
        prefix = Prefix.objects.create(prefix='10.0.0.0/24', scope=child)
        cluster_type = ClusterType.objects.create(name='CT', slug='ct')
        cluster = Cluster.objects.create(name='Cluster', type=cluster_type, scope=child)
        self.assertEqual(prefix._site, site_a)
        self.assertEqual(cluster._site, site_a)

        # Moving the parent Location drags the child along via a signal-less queryset
        # update, so no post_save fires for the child. The cached scope fields of objects
        # scoped to descendant locations must be updated in the same handler.
        parent.site = site_b
        parent.save()

        child.refresh_from_db()
        self.assertEqual(child.site, site_b)
        prefix.refresh_from_db()
        self.assertEqual(prefix._site, site_b)
        self.assertEqual(prefix._site_group, group_b)
        self.assertEqual(prefix._location, child)
        cluster.refresh_from_db()
        self.assertEqual(cluster._site, site_b)
        self.assertEqual(cluster._site_group, group_b)

    def test_location_site_change_repairs_descendant_row_with_poisoned_location_cache(self):
        site_a = Site.objects.create(name='Site A', slug='site-a')
        site_b = Site.objects.create(name='Site B', slug='site-b')
        parent = Location.objects.create(name='Parent', slug='parent', site=site_a)
        child = Location.objects.create(name='Child', slug='child', site=site_a, parent=parent)
        other = Location.objects.create(name='Other', slug='other', site=site_a)
        prefix = Prefix.objects.create(prefix='10.0.0.0/24', scope=child)

        # Poison the cached _location to point outside the subtree. The repair must select
        # rows through the authoritative scope (scope_type/scope_id), not the cached
        # column, or this descendant-scoped row is missed — and it must repair _location
        # itself, or the row stays invisible to future saves of its real location.
        Prefix.objects.filter(pk=prefix.pk).update(_location=other)

        # Re-fetch: creating further Locations renumbers the MPTT tree, and the in-memory
        # instance's stale bounds would otherwise select the wrong subtree (a pre-existing
        # handler hazard, tracked separately).
        parent = Location.objects.get(pk=parent.pk)
        parent.site = site_b
        parent.save()

        prefix.refresh_from_db()
        self.assertEqual(prefix._site, site_b)
        self.assertEqual(prefix._location, child)

    def test_location_site_change_ignores_foreign_row_with_poisoned_location_cache(self):
        site_a = Site.objects.create(name='Site A', slug='site-a')
        site_b = Site.objects.create(name='Site B', slug='site-b')
        site_c = Site.objects.create(name='Site C', slug='site-c')
        parent = Location.objects.create(name='Parent', slug='parent', site=site_a)
        child = Location.objects.create(name='Child', slug='child', site=site_a, parent=parent)
        elsewhere = Location.objects.create(name='Elsewhere', slug='elsewhere', site=site_c)
        prefix = Prefix.objects.create(prefix='10.0.0.0/24', scope=elsewhere)

        # Poison the cached _location to point INTO the subtree being moved. A repair that
        # selects rows through the cached column would wrongly stamp this unrelated object
        # with the destination site.
        Prefix.objects.filter(pk=prefix.pk).update(_location=child)

        # Re-fetch to avoid stale in-memory MPTT bounds (see the sibling test).
        parent = Location.objects.get(pk=parent.pk)
        parent.site = site_b
        parent.save()

        prefix.refresh_from_db()
        self.assertEqual(prefix._site, site_c)
        # The poisoned _location is intentional residue: this row is not scoped to the
        # moved subtree, so only a save touching its own scope chain repairs it.
        self.assertEqual(prefix._location, child)

    def test_resync_recomputes_from_scope_not_from_saved_instance(self):
        group_a = SiteGroup.objects.create(name='Group A', slug='group-a')
        group_b = SiteGroup.objects.create(name='Group B', slug='group-b')
        group_c = SiteGroup.objects.create(name='Group C', slug='group-c')
        site_a = Site.objects.create(name='Site A', slug='site-a', group=group_a)
        site_b = Site.objects.create(name='Site B', slug='site-b', group=group_b)
        location = Location.objects.create(name='Loc', slug='loc', site=site_b)
        prefix = Prefix.objects.create(prefix='10.0.0.0/24', scope=location)
        self.assertEqual(prefix._site, site_b)

        # Fabricate a stale row pointing at the wrong site, then trigger site_a's resync
        # with a real scope change. The row matches site_a's rebuild filter (_site=site_a)
        # but its actual scope lives under site_b: recomputed values must derive from the
        # row's scope, never be stamped from the saved instance.
        Prefix.objects.filter(pk=prefix.pk).update(_site=site_a, _site_group=group_a)

        site_a.group = group_c
        site_a.save()

        prefix.refresh_from_db()
        self.assertEqual(prefix._site, site_b)
        self.assertEqual(prefix._site_group, group_b)
        self.assertEqual(prefix._location, location)

    def test_stale_save_after_concurrent_update_resyncs(self):
        """
        A stale full save can write an old scope value back over a concurrent update
        (when the client sends no If-Match header). The resync must run so the caches follow
        whatever was actually written. A Cluster is used because it has no
        denormalized-field registration to mask a skipped resync (unlike Prefix). The
        lock-wait variant of this race (the concurrent update not yet committed) cannot
        be exercised in a single-connection TestCase.
        """
        region_a = Region.objects.create(name='Region A', slug='region-a')
        region_b = Region.objects.create(name='Region B', slug='region-b')
        site = Site.objects.create(name='Site', slug='site', region=region_a)
        cluster_type = ClusterType.objects.create(name='CT', slug='ct')
        cluster = Cluster.objects.create(name='Cluster', type=cluster_type, scope=site)

        # Client 1 loads the site (and, like every request-driven save, snapshots it).
        s1 = Site.objects.get(pk=site.pk)
        s1.snapshot()

        # Client 2 changes the region and saves; caches follow.
        s2 = Site.objects.get(pk=site.pk)
        s2.region = region_b
        s2.save()
        cluster.refresh_from_db()
        self.assertEqual(cluster._region, region_b)

        # Client 1's stale save writes region_a back. From client 1's point of view
        # nothing changed, but the database value did: the resync must run.
        s1.save()

        cluster.refresh_from_db()
        self.assertEqual(cluster._region, region_a)

    def test_resync_groups_updates_by_distinct_scope(self):
        group_a = SiteGroup.objects.create(name='Group A', slug='group-a')
        group_b = SiteGroup.objects.create(name='Group B', slug='group-b')
        site = Site.objects.create(name='Site', slug='site', group=group_a)
        location = Location.objects.create(name='Loc', slug='loc', site=site)
        prefix_1 = Prefix.objects.create(prefix='10.0.1.0/24', scope=site)
        prefix_2 = Prefix.objects.create(prefix='10.0.2.0/24', scope=site)
        prefix_3 = Prefix.objects.create(prefix='10.0.3.0/24', scope=location)
        cluster_type = ClusterType.objects.create(name='CT', slug='ct')
        cluster = Cluster.objects.create(name='Cluster', type=cluster_type, scope=site)

        site.group = group_b
        site.save()

        # Each object's cached fields must derive from its own scope; a resync that
        # applies one scope's computed values to all matched rows would corrupt these.
        for prefix in (prefix_1, prefix_2):
            prefix.refresh_from_db()
            self.assertIsNone(prefix._location)
            self.assertEqual(prefix._site, site)
            self.assertEqual(prefix._site_group, group_b)
        prefix_3.refresh_from_db()
        self.assertEqual(prefix_3._location, location)
        self.assertEqual(prefix_3._site, site)
        self.assertEqual(prefix_3._site_group, group_b)
        cluster.refresh_from_db()
        self.assertEqual(cluster._site_group, group_b)

    def test_resync_issues_one_update_per_distinct_scope(self):
        group = SiteGroup.objects.create(name='Group', slug='group')
        site = Site.objects.create(name='Site', slug='site')
        location = Location.objects.create(name='Loc', slug='loc', site=site)
        for i in range(1, 4):
            Prefix.objects.create(prefix=f'10.0.{i}.0/24', scope=site)
        for i in range(4, 6):
            Prefix.objects.create(prefix=f'10.0.{i}.0/24', scope=location)
        cluster_type = ClusterType.objects.create(name='CT', slug='ct')
        Cluster.objects.create(name='Cluster 1', type=cluster_type, scope=site)
        Cluster.objects.create(name='Cluster 2', type=cluster_type, scope=site)

        # One UPDATE per distinct (scope_type, scope) pair — not one per row (nor a single
        # per-row CASE WHEN statement). Multiple rows per scope are seeded above so that a
        # default-ordering leak into DISTINCT (which degrades grouping to one pair per row)
        # changes these counts. Only this signal's UPDATEs set _location_id; the
        # denormalized-field registry (netbox.denormalized) also updates Prefix on every
        # Site save but touches only _region_id/_site_group_id, so the filter below
        # excludes it.
        distinct_prefix_scopes = len(set(
            Prefix.objects.filter(_site=site).values_list('scope_type_id', 'scope_id')
        ))
        self.assertEqual(distinct_prefix_scopes, 2)

        site.group = group  # A real scope change: the resync must run

        with CaptureQueriesContext(connection) as ctx:
            site.save()

        prefix_updates = [
            q for q in ctx.captured_queries
            if q['sql'].startswith('UPDATE "ipam_prefix"') and '"_location_id"' in q['sql']
        ]
        self.assertEqual(len(prefix_updates), distinct_prefix_scopes)
        cluster_updates = [
            q for q in ctx.captured_queries if q['sql'].startswith('UPDATE "virtualization_cluster"')
        ]
        self.assertEqual(len(cluster_updates), 1)

    def test_stale_partial_save_skips_resync(self):
        # A save passing update_fields writes only the fields it names, so an omitted scope
        # field cannot have changed and the rebuild has nothing to recompute.
        group_a = SiteGroup.objects.create(name='Group A', slug='group-a')
        group_b = SiteGroup.objects.create(name='Group B', slug='group-b')
        site = Site.objects.create(name='Site', slug='site', group=group_a)
        cluster_type = ClusterType.objects.create(name='CT', slug='ct')
        cluster = Cluster.objects.create(name='Cluster', type=cluster_type, scope=site)

        stale = Site.objects.get(pk=site.pk)
        site.group = group_b
        site.save()

        stale.description = 'updated'
        with CaptureQueriesContext(connection) as ctx:
            stale.save(update_fields=['description'])

        self.assertEqual(
            [q for q in ctx.captured_queries if q['sql'].startswith('UPDATE "virtualization_cluster"')],
            [],
        )
        cluster.refresh_from_db()
        self.assertEqual(cluster._site_group, group_b)

    def test_raw_save_skips_resync(self):
        # raw=True is set only by Django's loaddata pathway, whose fixture already carries the
        # cached scope fields for every object it loads, so the rebuild would recompute the
        # values the rows already hold.
        group_a = SiteGroup.objects.create(name='Group A', slug='group-a')
        group_b = SiteGroup.objects.create(name='Group B', slug='group-b')
        site = Site.objects.create(name='Site', slug='site', group=group_a)
        cluster_type = ClusterType.objects.create(name='CT', slug='ct')
        Cluster.objects.create(name='Cluster', type=cluster_type, scope=site)

        site.group = group_b  # A real scope change, which a non-raw save would resync

        with CaptureQueriesContext(connection) as ctx:
            site.save_base(raw=True)

        self.assertEqual(
            [q for q in ctx.captured_queries if q['sql'].startswith('UPDATE "virtualization_cluster"')],
            [],
        )


class SyncCachedScopeFieldsAutocommitTestCase(TransactionTestCase):
    """
    Exercise the autocommit save path, which TestCase cannot reach (it wraps every test
    in a transaction). Outside an atomic block the pre-save read and the save's UPDATE
    run in separate transactions, so the skip guard is disabled there: the stash is
    cleared and the rebuild runs unconditionally.

    Note: TransactionTestCase teardown flushes all tables, which removes rows seeded by
    data migrations from a --keepdb database (e.g. the dcim.0206 ModuleTypeProfiles).
    A fresh test database restores them.
    """

    def test_autocommit_noop_save_always_resyncs(self):
        group = SiteGroup.objects.create(name='Group', slug='group')
        site = Site.objects.create(name='Site', slug='site', group=group)
        location = Location.objects.create(name='Loc', slug='loc', site=site)
        prefix = Prefix.objects.create(prefix='10.0.0.0/24', scope=site)

        # A transactional save first, so the instance carries a stash. The subsequent
        # autocommit save must clear it rather than compare against a previous save's
        # values.
        with transaction.atomic():
            site.save()

        Prefix.objects.filter(pk=prefix.pk).update(_location=location)

        site.save()  # Autocommit: no stash, unconditional rebuild

        prefix.refresh_from_db()
        self.assertIsNone(prefix._location)


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
