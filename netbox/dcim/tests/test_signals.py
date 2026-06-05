from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from django.contrib.contenttypes.models import ContentType
from django.test import SimpleTestCase, TestCase

from dcim import signals
from dcim.choices import CableEndChoices, LinkStatusChoices
from dcim.models import (
    Cable,
    CablePath,
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
    Site,
    SiteGroup,
    VirtualChassis,
)
from ipam.models import Prefix
from virtualization.models import Cluster, ClusterType
from wireless.models import WirelessLAN


class LocationSiteChangeSignalTestCase(TestCase):
    """
    Verify dcim.signals.handle_location_site_change propagates a Location's new Site to
    every descendant Location, Rack, Device, PowerPanel, and component when the parent
    Location's site assignment changes.
    """

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

    def test_creating_location_does_not_attempt_to_propagate(self):
        # Should not raise — newly-created locations have no descendants.
        Location.objects.create(name='New', slug='new', site=self.site_a)


class RackSiteChangeSignalTestCase(TestCase):
    """
    Verify dcim.signals.handle_rack_site_change propagates a Rack's site/location to its
    Devices and their components when the Rack is moved.
    """

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


class DeviceSiteChangeSignalTestCase(TestCase):
    """
    Verify dcim.signals.handle_device_site_change propagates a Device's site/location/rack
    to its components on save.
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

        # Reload the cable so _orig_status reflects the persisted value and
        # _terminations_modified resets to False.
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
        self.assertEqual(interface_a.cable_end, '')
        self.assertEqual(interface_b.cable_end, '')

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
        self.assertEqual(interface_a.cable_end, '')


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
