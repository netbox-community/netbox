from django.core.exceptions import ValidationError
from django.test import TestCase

from circuits.models import *
from core.models import ObjectType
from dcim.choices import *
from dcim.models import *
from extras.models import CustomField
from tenancy.models import Tenant
from utilities.data import drange
from virtualization.models import Cluster, ClusterType


class LocationTestCase(TestCase):

    def test_change_location_site(self):
        """
        Check that all child Locations and Racks get updated when a Location is moved to a new Site. Topology:
        Site A
          - Location A1
            - Location A2
              - Rack 2
              - Device 2
            - Rack 1
            - Device 1
        """
        manufacturer = Manufacturer.objects.create(name='Manufacturer 1', slug='manufacturer-1')
        device_type = DeviceType.objects.create(
            manufacturer=manufacturer, model='Device Type 1', slug='device-type-1'
        )
        role = DeviceRole.objects.create(
            name='Device Role 1', slug='device-role-1', color='ff0000'
        )

        site_a = Site.objects.create(name='Site A', slug='site-a')
        site_b = Site.objects.create(name='Site B', slug='site-b')

        location_a1 = Location(site=site_a, name='Location A1', slug='location-a1')
        location_a1.save()
        location_a2 = Location(site=site_a, parent=location_a1, name='Location A2', slug='location-a2')
        location_a2.save()

        rack1 = Rack.objects.create(site=site_a, location=location_a1, name='Rack 1')
        rack2 = Rack.objects.create(site=site_a, location=location_a2, name='Rack 2')

        device1 = Device.objects.create(
            site=site_a,
            location=location_a1,
            name='Device 1',
            device_type=device_type,
            role=role
        )
        device2 = Device.objects.create(
            site=site_a,
            location=location_a2,
            name='Device 2',
            device_type=device_type,
            role=role
        )

        powerpanel1 = PowerPanel.objects.create(site=site_a, location=location_a1, name='Power Panel 1')

        # Move Location A1 to Site B
        location_a1.site = site_b
        location_a1.save()

        # Check that all objects within Location A1 now belong to Site B
        self.assertEqual(Location.objects.get(pk=location_a1.pk).site, site_b)
        self.assertEqual(Location.objects.get(pk=location_a2.pk).site, site_b)
        self.assertEqual(Rack.objects.get(pk=rack1.pk).site, site_b)
        self.assertEqual(Rack.objects.get(pk=rack2.pk).site, site_b)
        self.assertEqual(Device.objects.get(pk=device1.pk).site, site_b)
        self.assertEqual(Device.objects.get(pk=device2.pk).site, site_b)
        self.assertEqual(PowerPanel.objects.get(pk=powerpanel1.pk).site, site_b)


class RackTypeTestCase(TestCase):

    @classmethod
    def setUpTestData(cls):
        manufacturer = Manufacturer.objects.create(name='Manufacturer 1', slug='manufacturer-1')

        RackType.objects.create(
            manufacturer=manufacturer,
            model='RackType 1',
            slug='rack-type-1',
            width=11,
            u_height=22,
            starting_unit=3,
            desc_units=True,
            outer_width=444,
            outer_depth=5,
            outer_unit=RackDimensionUnitChoices.UNIT_MILLIMETER,
            weight=66,
            weight_unit=WeightUnitChoices.UNIT_POUND,
            max_weight=7777,
            mounting_depth=8,
        )

    def test_rack_creation(self):
        rack_type = RackType.objects.first()
        sites = (
            Site(name='Site 1', slug='site-1'),
        )
        Site.objects.bulk_create(sites)
        locations = (
            Location(name='Location 1', slug='location-1', site=sites[0]),
        )
        for location in locations:
            location.save()

        rack = Rack.objects.create(
            name='Rack 1',
            facility_id='A101',
            site=sites[0],
            location=locations[0],
            rack_type=rack_type
        )
        self.assertEqual(rack.width, rack_type.width)
        self.assertEqual(rack.u_height, rack_type.u_height)
        self.assertEqual(rack.starting_unit, rack_type.starting_unit)
        self.assertEqual(rack.desc_units, rack_type.desc_units)
        self.assertEqual(rack.outer_width, rack_type.outer_width)
        self.assertEqual(rack.outer_depth, rack_type.outer_depth)
        self.assertEqual(rack.outer_unit, rack_type.outer_unit)
        self.assertEqual(rack.weight, rack_type.weight)
        self.assertEqual(rack.weight_unit, rack_type.weight_unit)
        self.assertEqual(rack.max_weight, rack_type.max_weight)
        self.assertEqual(rack.mounting_depth, rack_type.mounting_depth)


class RackTestCase(TestCase):

    @classmethod
    def setUpTestData(cls):

        sites = (
            Site(name='Site 1', slug='site-1'),
            Site(name='Site 2', slug='site-2'),
        )
        Site.objects.bulk_create(sites)

        locations = (
            Location(name='Location 1', slug='location-1', site=sites[0]),
            Location(name='Location 2', slug='location-2', site=sites[1]),
        )
        for location in locations:
            location.save()

        Rack.objects.create(
            name='Rack 1',
            facility_id='A101',
            site=sites[0],
            location=locations[0],
            u_height=42
        )

        manufacturer = Manufacturer.objects.create(name='Manufacturer 1', slug='manufacturer-1')
        device_types = (
            DeviceType(manufacturer=manufacturer, model='Device Type 1', slug='device-type-1', u_height=1),
            DeviceType(manufacturer=manufacturer, model='Device Type 2', slug='device-type-2', u_height=0),
            DeviceType(manufacturer=manufacturer, model='Device Type 3', slug='device-type-3', u_height=0.5),
        )
        DeviceType.objects.bulk_create(device_types)

        DeviceRole.objects.create(name='Device Role 1', slug='device-role-1')

    def test_rack_device_outside_height(self):
        site = Site.objects.first()
        rack = Rack.objects.first()

        device1 = Device(
            name='Device 1',
            device_type=DeviceType.objects.first(),
            role=DeviceRole.objects.first(),
            site=site,
            rack=rack,
            position=43,
            face=DeviceFaceChoices.FACE_FRONT,
        )
        device1.save()

        with self.assertRaises(ValidationError):
            rack.clean()

    def test_location_site(self):
        site1 = Site.objects.get(name='Site 1')
        location2 = Location.objects.get(name='Location 2')

        rack2 = Rack(
            name='Rack 2',
            site=site1,
            location=location2,
            u_height=42
        )
        rack2.save()

        with self.assertRaises(ValidationError):
            rack2.clean()

    def test_mount_single_device(self):
        site = Site.objects.first()
        rack = Rack.objects.first()

        device1 = Device(
            name='TestSwitch1',
            device_type=DeviceType.objects.first(),
            role=DeviceRole.objects.first(),
            site=site,
            rack=rack,
            position=10.0,
            face=DeviceFaceChoices.FACE_REAR,
        )
        device1.save()

        # Validate rack height
        self.assertEqual(list(rack.units), list(drange(42.5, 0.5, -0.5)))

        # Validate inventory (front face)
        rack1_inventory_front = {
            u['id']: u for u in rack.get_rack_units(face=DeviceFaceChoices.FACE_FRONT)
        }
        self.assertEqual(rack1_inventory_front[10.0]['device'], device1)
        self.assertEqual(rack1_inventory_front[10.5]['device'], device1)
        del rack1_inventory_front[10.0]
        del rack1_inventory_front[10.5]
        for u in rack1_inventory_front.values():
            self.assertIsNone(u['device'])

        # Validate inventory (rear face)
        rack1_inventory_rear = {
            u['id']: u for u in rack.get_rack_units(face=DeviceFaceChoices.FACE_REAR)
        }
        self.assertEqual(rack1_inventory_rear[10.0]['device'], device1)
        self.assertEqual(rack1_inventory_rear[10.5]['device'], device1)
        del rack1_inventory_rear[10.0]
        del rack1_inventory_rear[10.5]
        for u in rack1_inventory_rear.values():
            self.assertIsNone(u['device'])

    def test_mount_zero_ru(self):
        """
        Check that a 0RU device can be mounted in a rack with no face/position.
        """
        site = Site.objects.first()
        rack = Rack.objects.first()

        Device(
            name='Device 1',
            role=DeviceRole.objects.first(),
            device_type=DeviceType.objects.first(),
            site=site,
            rack=rack
        ).save()

    def test_mount_half_u_devices(self):
        """
        Check that two 0.5U devices can be mounted in the same rack unit.
        """
        rack = Rack.objects.first()
        attrs = {
            'device_type': DeviceType.objects.get(u_height=0.5),
            'role': DeviceRole.objects.first(),
            'site': Site.objects.first(),
            'rack': rack,
            'face': DeviceFaceChoices.FACE_FRONT,
        }

        Device(name='Device 1', position=1, **attrs).save()
        Device(name='Device 2', position=1.5, **attrs).save()

        self.assertEqual(len(rack.get_available_units()), rack.u_height * 2 - 3)

    def test_change_rack_site(self):
        """
        Check that child Devices get updated when a Rack is moved to a new Site.
        """
        site_a = Site.objects.create(name='Site A', slug='site-a')
        site_b = Site.objects.create(name='Site B', slug='site-b')

        # Create Rack1 in Site A
        rack1 = Rack.objects.create(site=site_a, name='Rack 1')

        # Create Device1 in Rack1
        device1 = Device.objects.create(
            site=site_a,
            rack=rack1,
            device_type=DeviceType.objects.first(),
            role=DeviceRole.objects.first()
        )

        # Move Rack1 to Site B
        rack1.site = site_b
        rack1.save()

        # Check that Device1 is now assigned to Site B
        self.assertEqual(Device.objects.get(pk=device1.pk).site, site_b)

    def test_utilization(self):
        site = Site.objects.first()
        rack = Rack.objects.first()

        Device(
            name='Device 1',
            role=DeviceRole.objects.first(),
            device_type=DeviceType.objects.first(),
            site=site,
            rack=rack,
            position=1
        ).save()
        rack.refresh_from_db()
        self.assertEqual(rack.get_utilization(), 1 / 42 * 100)

        # create device excluded from utilization calculations
        dt = DeviceType.objects.create(
            manufacturer=Manufacturer.objects.first(),
            model='Device Type 4',
            slug='device-type-4',
            u_height=1,
            exclude_from_utilization=True
        )
        Device(
            name='Device 2',
            role=DeviceRole.objects.first(),
            device_type=dt,
            site=site,
            rack=rack,
            position=5
        ).save()
        rack.refresh_from_db()
        self.assertEqual(rack.get_utilization(), 1 / 42 * 100)


class DeviceTestCase(TestCase):

    @classmethod
    def setUpTestData(cls):

        Site.objects.create(name='Test Site 1', slug='test-site-1')
        manufacturer = Manufacturer.objects.create(name='Test Manufacturer 1', slug='test-manufacturer-1')
        device_type = DeviceType.objects.create(
            manufacturer=manufacturer, model='Test Device Type 1', slug='test-device-type-1'
        )
        roles = (
            DeviceRole(name='Test Role 1', slug='test-role-1'),
            DeviceRole(name='Test Role 2', slug='test-role-2'),
        )
        DeviceRole.objects.bulk_create(roles)

        # Create a CustomField with a default value & assign it to all component models
        cf1 = CustomField.objects.create(name='cf1', default='foo')
        cf1.object_types.set(
            ObjectType.objects.filter(app_label='dcim', model__in=[
                'consoleport',
                'consoleserverport',
                'powerport',
                'poweroutlet',
                'interface',
                'rearport',
                'frontport',
                'modulebay',
                'devicebay',
                'inventoryitem',
            ])
        )

        # Create DeviceType components
        ConsolePortTemplate(
            device_type=device_type,
            name='Console Port 1'
        ).save()

        ConsoleServerPortTemplate(
            device_type=device_type,
            name='Console Server Port 1'
        ).save()

        powerport = PowerPortTemplate(
            device_type=device_type,
            name='Power Port 1',
            maximum_draw=1000,
            allocated_draw=500
        )
        powerport.save()

        PowerOutletTemplate(
            device_type=device_type,
            name='Power Outlet 1',
            power_port=powerport,
            feed_leg=PowerOutletFeedLegChoices.FEED_LEG_A
        ).save()

        InterfaceTemplate(
            device_type=device_type,
            name='Interface 1',
            type=InterfaceTypeChoices.TYPE_1GE_FIXED,
            mgmt_only=True
        ).save()

        rearport = RearPortTemplate(
            device_type=device_type,
            name='Rear Port 1',
            type=PortTypeChoices.TYPE_8P8C,
            positions=8
        )
        rearport.save()

        FrontPortTemplate(
            device_type=device_type,
            name='Front Port 1',
            type=PortTypeChoices.TYPE_8P8C,
            rear_port=rearport,
            rear_port_position=2
        ).save()

        ModuleBayTemplate(
            device_type=device_type,
            name='Module Bay 1'
        ).save()

        DeviceBayTemplate(
            device_type=device_type,
            name='Device Bay 1'
        ).save()

        InventoryItemTemplate(
            device_type=device_type,
            name='Inventory Item 1'
        ).save()

    def test_device_creation(self):
        """
        Ensure that all Device components are copied automatically from the DeviceType.
        """
        device = Device(
            site=Site.objects.first(),
            device_type=DeviceType.objects.first(),
            role=DeviceRole.objects.first(),
            name='Test Device 1'
        )
        device.save()

        consoleport = ConsolePort.objects.get(
            device=device,
            name='Console Port 1'
        )
        self.assertEqual(consoleport.cf['cf1'], 'foo')

        consoleserverport = ConsoleServerPort.objects.get(
            device=device,
            name='Console Server Port 1'
        )
        self.assertEqual(consoleserverport.cf['cf1'], 'foo')

        powerport = PowerPort.objects.get(
            device=device,
            name='Power Port 1',
            maximum_draw=1000,
            allocated_draw=500
        )
        self.assertEqual(powerport.cf['cf1'], 'foo')

        poweroutlet = PowerOutlet.objects.get(
            device=device,
            name='Power Outlet 1',
            power_port=powerport,
            feed_leg=PowerOutletFeedLegChoices.FEED_LEG_A
        )
        self.assertEqual(poweroutlet.cf['cf1'], 'foo')

        interface = Interface.objects.get(
            device=device,
            name='Interface 1',
            type=InterfaceTypeChoices.TYPE_1GE_FIXED,
            mgmt_only=True
        )
        self.assertEqual(interface.cf['cf1'], 'foo')

        rearport = RearPort.objects.get(
            device=device,
            name='Rear Port 1',
            type=PortTypeChoices.TYPE_8P8C,
            positions=8
        )
        self.assertEqual(rearport.cf['cf1'], 'foo')

        frontport = FrontPort.objects.get(
            device=device,
            name='Front Port 1',
            type=PortTypeChoices.TYPE_8P8C,
            rear_port=rearport,
            rear_port_position=2
        )
        self.assertEqual(frontport.cf['cf1'], 'foo')

        modulebay = ModuleBay.objects.get(
            device=device,
            name='Module Bay 1'
        )
        self.assertEqual(modulebay.cf['cf1'], 'foo')

        devicebay = DeviceBay.objects.get(
            device=device,
            name='Device Bay 1'
        )
        self.assertEqual(devicebay.cf['cf1'], 'foo')

        inventoryitem = InventoryItem.objects.get(
            device=device,
            name='Inventory Item 1'
        )
        self.assertEqual(inventoryitem.cf['cf1'], 'foo')

    def test_multiple_unnamed_devices(self):

        device1 = Device(
            site=Site.objects.first(),
            device_type=DeviceType.objects.first(),
            role=DeviceRole.objects.first(),
            name=None
        )
        device1.save()

        device2 = Device(
            site=device1.site,
            device_type=device1.device_type,
            role=device1.role,
            name=None
        )
        device2.full_clean()
        device2.save()

        self.assertEqual(Device.objects.filter(name__isnull=True).count(), 2)

    def test_device_name_case_sensitivity(self):

        device1 = Device(
            site=Site.objects.first(),
            device_type=DeviceType.objects.first(),
            role=DeviceRole.objects.first(),
            name='device 1'
        )
        device1.save()

        device2 = Device(
            site=device1.site,
            device_type=device1.device_type,
            role=device1.role,
            name='DEVICE 1'
        )

        # Uniqueness validation for name should ignore case
        with self.assertRaises(ValidationError):
            device2.full_clean()

    def test_device_duplicate_names(self):

        device1 = Device(
            site=Site.objects.first(),
            device_type=DeviceType.objects.first(),
            role=DeviceRole.objects.first(),
            name='Test Device 1'
        )
        device1.save()

        device2 = Device(
            site=device1.site,
            device_type=device1.device_type,
            role=device1.role,
            name=device1.name
        )

        # Two devices assigned to the same Site and no Tenant should fail validation
        with self.assertRaises(ValidationError):
            device2.full_clean()

        tenant = Tenant.objects.create(name='Test Tenant 1', slug='test-tenant-1')
        device1.tenant = tenant
        device1.save()
        device2.tenant = tenant

        # Two devices assigned to the same Site and the same Tenant should fail validation
        with self.assertRaises(ValidationError):
            device2.full_clean()

        device2.tenant = None

        # Two devices assigned to the same Site and different Tenants should pass validation
        device2.full_clean()
        device2.save()

    def test_device_mismatched_site_cluster(self):
        cluster_type = ClusterType.objects.create(name='Cluster Type 1', slug='cluster-type-1')
        Cluster.objects.create(name='Cluster 1', type=cluster_type)

        sites = (
            Site(name='Site 1', slug='site-1'),
            Site(name='Site 2', slug='site-2'),
        )
        Site.objects.bulk_create(sites)

        clusters = (
            Cluster(name='Cluster 1', type=cluster_type, site=sites[0]),
            Cluster(name='Cluster 2', type=cluster_type, site=sites[1]),
            Cluster(name='Cluster 3', type=cluster_type, site=None),
        )
        Cluster.objects.bulk_create(clusters)

        device_type = DeviceType.objects.first()
        device_role = DeviceRole.objects.first()

        # Device with site only should pass
        Device(name='device1', site=sites[0], device_type=device_type, role=device_role).full_clean()

        # Device with site, cluster non-site should pass
        Device(name='device1', site=sites[0], device_type=device_type, role=device_role, cluster=clusters[2]).full_clean()

        # Device with mismatched site & cluster should fail
        with self.assertRaises(ValidationError):
            Device(name='device1', site=sites[0], device_type=device_type, role=device_role, cluster=clusters[1]).full_clean()


class CableTestCase(TestCase):

    @classmethod
    def setUpTestData(cls):

        site = Site.objects.create(name='Test Site 1', slug='test-site-1')
        manufacturer = Manufacturer.objects.create(name='Test Manufacturer 1', slug='test-manufacturer-1')
        devicetype = DeviceType.objects.create(
            manufacturer=manufacturer, model='Test Device Type 1', slug='test-device-type-1'
        )
        role = DeviceRole.objects.create(
            name='Test Device Role 1', slug='test-device-role-1', color='ff0000'
        )
        device1 = Device.objects.create(
            device_type=devicetype, role=role, name='TestDevice1', site=site
        )
        device2 = Device.objects.create(
            device_type=devicetype, role=role, name='TestDevice2', site=site
        )
        interface1 = Interface.objects.create(device=device1, name='eth0')
        interface2 = Interface.objects.create(device=device2, name='eth0')
        interface3 = Interface.objects.create(device=device2, name='eth1')
        Cable(a_terminations=[interface1], b_terminations=[interface2]).save()

        power_port1 = PowerPort.objects.create(device=device2, name='psu1')
        patch_pannel = Device.objects.create(
            device_type=devicetype, role=role, name='TestPatchPanel', site=site
        )
        rear_port1 = RearPort.objects.create(device=patch_pannel, name='RP1', type='8p8c')
        front_port1 = FrontPort.objects.create(
            device=patch_pannel, name='FP1', type='8p8c', rear_port=rear_port1, rear_port_position=1
        )
        rear_port2 = RearPort.objects.create(device=patch_pannel, name='RP2', type='8p8c', positions=2)
        front_port2 = FrontPort.objects.create(
            device=patch_pannel, name='FP2', type='8p8c', rear_port=rear_port2, rear_port_position=1
        )
        rear_port3 = RearPort.objects.create(device=patch_pannel, name='RP3', type='8p8c', positions=3)
        front_port3 = FrontPort.objects.create(
            device=patch_pannel, name='FP3', type='8p8c', rear_port=rear_port3, rear_port_position=1
        )
        rear_port4 = RearPort.objects.create(device=patch_pannel, name='RP4', type='8p8c', positions=3)
        front_port4 = FrontPort.objects.create(
            device=patch_pannel, name='FP4', type='8p8c', rear_port=rear_port4, rear_port_position=1
        )
        provider = Provider.objects.create(name='Provider 1', slug='provider-1')
        provider_network = ProviderNetwork.objects.create(name='Provider Network 1', provider=provider)
        circuittype = CircuitType.objects.create(name='Circuit Type 1', slug='circuit-type-1')
        circuit1 = Circuit.objects.create(provider=provider, type=circuittype, cid='1')
        circuit2 = Circuit.objects.create(provider=provider, type=circuittype, cid='2')
        circuittermination1 = CircuitTermination.objects.create(circuit=circuit1, site=site, term_side='A')
        circuittermination2 = CircuitTermination.objects.create(circuit=circuit1, site=site, term_side='Z')
        circuittermination3 = CircuitTermination.objects.create(circuit=circuit2, provider_network=provider_network, term_side='A')

    def test_cable_creation(self):
        """
        When a new Cable is created, it must be cached on either termination point.
        """
        interface1 = Interface.objects.get(device__name='TestDevice1', name='eth0')
        interface2 = Interface.objects.get(device__name='TestDevice2', name='eth0')
        cable = Cable.objects.first()
        self.assertEqual(interface1.cable, cable)
        self.assertEqual(interface2.cable, cable)
        self.assertEqual(interface1.cable_end, 'A')
        self.assertEqual(interface2.cable_end, 'B')
        self.assertEqual(interface1.link_peers, [interface2])
        self.assertEqual(interface2.link_peers, [interface1])

    def test_cable_deletion(self):
        """
        When a Cable is deleted, the `cable` field on its termination points must be nullified. The str() method
        should still return the PK of the string even after being nullified.
        """
        interface1 = Interface.objects.get(device__name='TestDevice1', name='eth0')
        interface2 = Interface.objects.get(device__name='TestDevice2', name='eth0')
        cable = Cable.objects.first()

        cable.delete()
        self.assertIsNone(cable.pk)
        self.assertNotEqual(str(cable), '#None')
        interface1 = Interface.objects.get(pk=interface1.pk)
        self.assertIsNone(interface1.cable)
        self.assertListEqual(interface1.link_peers, [])
        interface2 = Interface.objects.get(pk=interface2.pk)
        self.assertIsNone(interface2.cable)
        self.assertListEqual(interface2.link_peers, [])

    def test_cable_validates_same_parent_object(self):
        """
        The clean method should ensure that all terminations at either end of a Cable belong to the same parent object.
        """
        interface1 = Interface.objects.get(device__name='TestDevice1', name='eth0')
        powerport1 = PowerPort.objects.get(device__name='TestDevice2', name='psu1')

        cable = Cable(a_terminations=[interface1], b_terminations=[powerport1])
        with self.assertRaises(ValidationError):
            cable.clean()

    def test_cable_validates_same_type(self):
        """
        The clean method should ensure that all terminations at either end of a Cable are of the same type.
        """
        interface1 = Interface.objects.get(device__name='TestDevice1', name='eth0')
        frontport1 = FrontPort.objects.get(device__name='TestPatchPanel', name='FP1')
        rearport1 = RearPort.objects.get(device__name='TestPatchPanel', name='RP1')

        cable = Cable(a_terminations=[frontport1, rearport1], b_terminations=[interface1])
        with self.assertRaises(ValidationError):
            cable.clean()

    def test_cable_validates_compatible_types(self):
        """
        The clean method should have a check to ensure only compatible port types can be connected by a cable
        """
        interface1 = Interface.objects.get(device__name='TestDevice1', name='eth0')
        powerport1 = PowerPort.objects.get(device__name='TestDevice2', name='psu1')

        # An interface cannot be connected to a power port, for example
        cable = Cable(a_terminations=[interface1], b_terminations=[powerport1])
        with self.assertRaises(ValidationError):
            cable.clean()

    def test_cable_cannot_terminate_to_a_provider_network_circuittermination(self):
        """
        Neither side of a cable can be terminated to a CircuitTermination which is attached to a ProviderNetwork
        """
        interface3 = Interface.objects.get(device__name='TestDevice2', name='eth1')
        circuittermination3 = CircuitTermination.objects.get(circuit__cid='2', term_side='A')

        cable = Cable(a_terminations=[interface3], b_terminations=[circuittermination3])
        with self.assertRaises(ValidationError):
            cable.clean()

    def test_cable_cannot_terminate_to_a_virtual_interface(self):
        """
        A cable cannot terminate to a virtual interface
        """
        device1 = Device.objects.get(name='TestDevice1')
        interface2 = Interface.objects.get(device__name='TestDevice2', name='eth0')

        virtual_interface = Interface(device=device1, name="V1", type=InterfaceTypeChoices.TYPE_VIRTUAL)
        cable = Cable(a_terminations=[interface2], b_terminations=[virtual_interface])
        with self.assertRaises(ValidationError):
            cable.clean()

    def test_cable_cannot_terminate_to_a_wireless_interface(self):
        """
        A cable cannot terminate to a wireless interface
        """
        device1 = Device.objects.get(name='TestDevice1')
        interface2 = Interface.objects.get(device__name='TestDevice2', name='eth0')

        wireless_interface = Interface(device=device1, name="W1", type=InterfaceTypeChoices.TYPE_80211A)
        cable = Cable(a_terminations=[interface2], b_terminations=[wireless_interface])
        with self.assertRaises(ValidationError):
            cable.clean()


class VirtualDeviceContextTestCase(TestCase):

    @classmethod
    def setUpTestData(cls):

        site = Site.objects.create(name='Test Site 1', slug='test-site-1')
        manufacturer = Manufacturer.objects.create(name='Test Manufacturer 1', slug='test-manufacturer-1')
        devicetype = DeviceType.objects.create(
            manufacturer=manufacturer, model='Test Device Type 1', slug='test-device-type-1'
        )
        role = DeviceRole.objects.create(
            name='Test Device Role 1', slug='test-device-role-1', color='ff0000'
        )
        Device.objects.create(
            device_type=devicetype, role=role, name='TestDevice1', site=site
        )

    def test_vdc_and_interface_creation(self):
        device = Device.objects.first()

        vdc = VirtualDeviceContext(device=device, name="VDC 1", identifier=1, status='active')
        vdc.full_clean()
        vdc.save()

        interface = Interface(device=device, name='Eth1/1', type='10gbase-t')
        interface.full_clean()
        interface.save()

        interface.vdcs.set([vdc])

    def test_vdc_duplicate_name(self):
        device = Device.objects.first()

        vdc1 = VirtualDeviceContext(device=device, name="VDC 1", identifier=1, status='active')
        vdc1.full_clean()
        vdc1.save()

        vdc2 = VirtualDeviceContext(device=device, name="VDC 1", identifier=2, status='active')
        with self.assertRaises(ValidationError):
            vdc2.full_clean()

    def test_vdc_duplicate_identifier(self):
        device = Device.objects.first()

        vdc1 = VirtualDeviceContext(device=device, name="VDC 1", identifier=1, status='active')
        vdc1.full_clean()
        vdc1.save()

        vdc2 = VirtualDeviceContext(device=device, name="VDC 2", identifier=1, status='active')
        with self.assertRaises(ValidationError):
            vdc2.full_clean()
