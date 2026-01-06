from django.core.exceptions import ValidationError
from django.test import tag, TestCase

from circuits.models import *
from core.models import ObjectType
from dcim.choices import *
from dcim.models import *
from extras.models import CustomField
from netbox.choices import WeightUnitChoices
from tenancy.models import Tenant
from utilities.data import drange
from virtualization.models import Cluster, ClusterType


class MACAddressTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        site = Site.objects.create(name='Test Site 1', slug='test-site-1')
        manufacturer = Manufacturer.objects.create(name='Test Manufacturer 1', slug='test-manufacturer-1')
        device_type = DeviceType.objects.create(
            manufacturer=manufacturer, model='Test Device Type 1', slug='test-device-type-1'
        )
        device_role = DeviceRole.objects.create(name='Test Role 1', slug='test-role-1')
        device = Device.objects.create(
            name='Device 1', device_type=device_type, role=device_role, site=site,
        )
        cls.interface = Interface.objects.create(
            device=device,
            name='Interface 1',
            type=InterfaceTypeChoices.TYPE_1GE_FIXED,
            mgmt_only=True
        )

        cls.mac_a = MACAddress.objects.create(mac_address='1234567890ab', assigned_object=cls.interface)
        cls.mac_b = MACAddress.objects.create(mac_address='1234567890ba', assigned_object=cls.interface)

        cls.interface.primary_mac_address = cls.mac_a
        cls.interface.save()

    @tag('regression')
    def test_clean_will_not_allow_removal_of_assigned_object_if_primary(self):
        self.mac_a.assigned_object = None
        with self.assertRaisesMessage(ValidationError, 'Cannot unassign MAC Address while'):
            self.mac_a.clean()

    @tag('regression')
    def test_clean_will_allow_removal_of_assigned_object_if_not_primary(self):
        self.mac_b.assigned_object = None
        self.mac_b.clean()


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
        for role in roles:
            role.save()

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

        frontport = FrontPortTemplate(
            device_type=device_type,
            name='Front Port 1',
            type=PortTypeChoices.TYPE_8P8C,
        )
        frontport.save()

        PortTemplateMapping.objects.create(
            device_type=device_type,
            front_port=frontport,
            rear_port=rearport,
            rear_port_position=2,
        )

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
            feed_leg=PowerOutletFeedLegChoices.FEED_LEG_A,
            status=PowerOutletStatusChoices.STATUS_ENABLED,
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
            positions=1
        )
        self.assertEqual(frontport.cf['cf1'], 'foo')

        self.assertTrue(PortMapping.objects.filter(front_port=frontport, rear_port=rearport).exists())

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

    def test_device_label(self):
        device1 = Device(
            site=Site.objects.first(),
            device_type=DeviceType.objects.first(),
            role=DeviceRole.objects.first(),
            name=None,
        )
        self.assertEqual(device1.label, None)

        device1.name = 'Test Device 1'
        self.assertEqual(device1.label, 'Test Device 1')

        virtual_chassis = VirtualChassis.objects.create(name='VC 1')
        device2 = Device(
            site=Site.objects.first(),
            device_type=DeviceType.objects.first(),
            role=DeviceRole.objects.first(),
            name=None,
            virtual_chassis=virtual_chassis,
            vc_position=2,
        )
        self.assertEqual(device2.label, 'VC 1:2')

        device2.name = 'Test Device 2'
        self.assertEqual(device2.label, 'Test Device 2')

    def test_device_mismatched_site_cluster(self):
        cluster_type = ClusterType.objects.create(name='Cluster Type 1', slug='cluster-type-1')
        Cluster.objects.create(name='Cluster 1', type=cluster_type)

        sites = (
            Site(name='Site 1', slug='site-1'),
            Site(name='Site 2', slug='site-2'),
        )
        Site.objects.bulk_create(sites)

        clusters = (
            Cluster(name='Cluster 1', type=cluster_type, scope=sites[0]),
            Cluster(name='Cluster 2', type=cluster_type, scope=sites[1]),
            Cluster(name='Cluster 3', type=cluster_type, scope=None),
        )
        for cluster in clusters:
            cluster.save()

        device_type = DeviceType.objects.first()
        device_role = DeviceRole.objects.first()

        # Device with site only should pass
        Device(
            name='device1',
            site=sites[0],
            device_type=device_type,
            role=device_role
        ).full_clean()

        # Device with site, cluster non-site should pass
        Device(
            name='device1',
            site=sites[0],
            device_type=device_type,
            role=device_role,
            cluster=clusters[2]
        ).full_clean()

        # Device with mismatched site & cluster should fail
        with self.assertRaises(ValidationError):
            Device(
                name='device1',
                site=sites[0],
                device_type=device_type,
                role=device_role,
                cluster=clusters[1]
            ).full_clean()


class ModuleBayTestCase(TestCase):

    @classmethod
    def setUpTestData(cls):
        site = Site.objects.create(name='Test Site 1', slug='test-site-1')
        manufacturer = Manufacturer.objects.create(name='Test Manufacturer 1', slug='test-manufacturer-1')
        device_type = DeviceType.objects.create(
            manufacturer=manufacturer, model='Test Device Type 1', slug='test-device-type-1'
        )
        device_role = DeviceRole.objects.create(name='Test Role 1', slug='test-role-1')

        # Create a CustomField with a default value & assign it to all component models
        location = Location.objects.create(name='Location 1', slug='location-1', site=site)
        rack = Rack.objects.create(name='Rack 1', site=site)
        device = Device.objects.create(
            name='Device 1', device_type=device_type, role=device_role, site=site, location=location, rack=rack
        )

        module_bays = (
            ModuleBay(device=device, name='Module Bay 1', label='A', description='First'),
            ModuleBay(device=device, name='Module Bay 2', label='B', description='Second'),
            ModuleBay(device=device, name='Module Bay 3', label='C', description='Third'),
        )
        for module_bay in module_bays:
            module_bay.save()

        manufacturer = Manufacturer.objects.create(name='Manufacturer 1', slug='manufacturer-1')
        module_type = ModuleType.objects.create(manufacturer=manufacturer, model='Module Type 1')
        modules = (
            Module(device=device, module_bay=module_bays[0], module_type=module_type),
            Module(device=device, module_bay=module_bays[1], module_type=module_type),
            Module(device=device, module_bay=module_bays[2], module_type=module_type),
        )
        # M3 -> MB3 -> M2 -> MB2 -> M1 -> MB1
        Module.objects.bulk_create(modules)
        module_bays[1].module = modules[0]
        module_bays[1].clean()
        module_bays[1].save()
        module_bays[2].module = modules[1]
        module_bays[2].clean()
        module_bays[2].save()

    def test_module_bay_recursion(self):
        module_bay_1 = ModuleBay.objects.get(name='Module Bay 1')
        module_bay_3 = ModuleBay.objects.get(name='Module Bay 3')
        module_1 = Module.objects.get(module_bay=module_bay_1)
        module_3 = Module.objects.get(module_bay=module_bay_3)

        # Confirm error if ModuleBay recurses
        with self.assertRaises(ValidationError):
            module_bay_1.module = module_3
            module_bay_1.clean()
            module_bay_1.save()

        # Confirm error if Module recurses
        with self.assertRaises(ValidationError):
            module_1.module_bay = module_bay_3
            module_1.clean()
            module_1.save()

    def test_single_module_token(self):
        device_type = DeviceType.objects.first()
        device_role = DeviceRole.objects.first()
        site = Site.objects.first()
        location = Location.objects.first()
        rack = Rack.objects.first()

        # Create DeviceType components
        ConsolePortTemplate.objects.create(
            device_type=device_type,
            name='{module}',
            label='{module}',
        )
        ModuleBayTemplate.objects.create(
            device_type=device_type,
            name='Module Bay 1'
        )

        device = Device.objects.create(
            name='Device 2',
            device_type=device_type,
            role=device_role,
            site=site,
            location=location,
            rack=rack
        )
        device.consoleports.first()

    @tag('regression')  # #19918
    def test_nested_module_bay_label_resolution(self):
        """Test that nested module bay labels properly resolve {module} placeholders"""
        manufacturer = Manufacturer.objects.first()
        site = Site.objects.first()
        device_role = DeviceRole.objects.first()

        # Create device type with module bay template (position='A')
        device_type = DeviceType.objects.create(
            manufacturer=manufacturer,
            model='Device with Bays',
            slug='device-with-bays'
        )
        ModuleBayTemplate.objects.create(
            device_type=device_type,
            name='Bay A',
            position='A'
        )

        # Create module type with nested bay template using {module} placeholder
        module_type = ModuleType.objects.create(
            manufacturer=manufacturer,
            model='Module with Nested Bays'
        )
        ModuleBayTemplate.objects.create(
            module_type=module_type,
            name='SFP {module}-21',
            label='{module}-21',
            position='21'
        )

        # Create device and install module
        device = Device.objects.create(
            name='Test Device',
            device_type=device_type,
            role=device_role,
            site=site
        )
        module_bay = device.modulebays.get(name='Bay A')
        module = Module.objects.create(
            device=device,
            module_bay=module_bay,
            module_type=module_type
        )

        # Verify nested bay label resolves {module} to parent position
        nested_bay = module.modulebays.get(name='SFP A-21')
        self.assertEqual(nested_bay.label, 'A-21')

    def test_nested_module_single_placeholder_full_path(self):
        """
        Test that installing a module at depth=2 with a single {module} placeholder
        in the interface template name resolves to the full path (e.g., "1/1").
        Regression test for transceiver modeling use case.
        """
        manufacturer = Manufacturer.objects.first()
        site = Site.objects.first()
        device_role = DeviceRole.objects.first()

        # Create device type with module bay template
        device_type = DeviceType.objects.create(
            manufacturer=manufacturer,
            model='Chassis Device',
            slug='chassis-device'
        )
        ModuleBayTemplate.objects.create(
            device_type=device_type,
            name='Line Card Bay 1',
            position='1'
        )

        # Create line card module type with nested module bay
        line_card_type = ModuleType.objects.create(
            manufacturer=manufacturer,
            model='Line Card'
        )
        ModuleBayTemplate.objects.create(
            module_type=line_card_type,
            name='SFP Bay {module}/1',
            label='SFP {module}/1',
            position='1'
        )
        ModuleBayTemplate.objects.create(
            module_type=line_card_type,
            name='SFP Bay {module}/2',
            label='SFP {module}/2',
            position='2'
        )

        # Create SFP module type with interface using single {module} placeholder
        sfp_type = ModuleType.objects.create(
            manufacturer=manufacturer,
            model='SFP Transceiver'
        )
        InterfaceTemplate.objects.create(
            module_type=sfp_type,
            name='SFP {module}',
            label='{module}',
            type=InterfaceTypeChoices.TYPE_10GE_SFP_PLUS
        )

        # Create device
        device = Device.objects.create(
            name='Test Chassis',
            device_type=device_type,
            role=device_role,
            site=site
        )

        # Install line card in bay 1
        line_card_bay = device.modulebays.get(name='Line Card Bay 1')
        line_card = Module.objects.create(
            device=device,
            module_bay=line_card_bay,
            module_type=line_card_type
        )

        # Install SFP in nested bay 1 (depth=2)
        sfp_bay_1 = line_card.modulebays.get(name='SFP Bay 1/1')
        sfp_module_1 = Module.objects.create(
            device=device,
            module_bay=sfp_bay_1,
            module_type=sfp_type
        )

        # Verify interface name resolves to full path "1/1"
        interface_1 = sfp_module_1.interfaces.first()
        self.assertEqual(interface_1.name, 'SFP 1/1')
        self.assertEqual(interface_1.label, '1/1')

        # Install second SFP in nested bay 2 (depth=2) - verifies uniqueness
        sfp_bay_2 = line_card.modulebays.get(name='SFP Bay 1/2')
        sfp_module_2 = Module.objects.create(
            device=device,
            module_bay=sfp_bay_2,
            module_type=sfp_type
        )

        # Verify second interface name resolves to full path "1/2"
        interface_2 = sfp_module_2.interfaces.first()
        self.assertEqual(interface_2.name, 'SFP 1/2')
        self.assertEqual(interface_2.label, '1/2')

    def test_single_placeholder_direct_install_depth_1(self):
        """
        Test that installing a module directly at depth=1 with a single {module}
        placeholder still resolves correctly (just the position, not a path).
        """
        manufacturer = Manufacturer.objects.first()
        site = Site.objects.first()
        device_role = DeviceRole.objects.first()

        # Create device type with module bay template
        device_type = DeviceType.objects.create(
            manufacturer=manufacturer,
            model='Simple Chassis',
            slug='simple-chassis'
        )
        ModuleBayTemplate.objects.create(
            device_type=device_type,
            name='SFP Bay 1',
            position='1'
        )

        # Create SFP module type with interface using single {module} placeholder
        sfp_type = ModuleType.objects.create(
            manufacturer=manufacturer,
            model='Direct SFP'
        )
        InterfaceTemplate.objects.create(
            module_type=sfp_type,
            name='SFP {module}',
            label='{module}',
            type=InterfaceTypeChoices.TYPE_10GE_SFP_PLUS
        )

        # Create device
        device = Device.objects.create(
            name='Test Simple Chassis',
            device_type=device_type,
            role=device_role,
            site=site
        )

        # Install SFP directly in bay 1 (depth=1)
        sfp_bay = device.modulebays.get(name='SFP Bay 1')
        sfp_module = Module.objects.create(
            device=device,
            module_bay=sfp_bay,
            module_type=sfp_type
        )

        # Verify interface name resolves to just "1"
        interface = sfp_module.interfaces.first()
        self.assertEqual(interface.name, 'SFP 1')
        self.assertEqual(interface.label, '1')

    def test_multi_token_level_by_level_depth_2(self):
        """
        T1: Multi-token behavior remains unchanged at depth=2.
        Ensure legacy {module}/{module} still resolves level-by-level.
        """
        site = Site.objects.create(name='T1 Site', slug='t1-site')
        manufacturer = Manufacturer.objects.create(name='T1 Manufacturer', slug='t1-manufacturer')
        device_role = DeviceRole.objects.create(name='T1 Role', slug='t1-role')

        # Create device type with module bay
        device_type = DeviceType.objects.create(
            manufacturer=manufacturer,
            model='T1 Chassis',
            slug='t1-chassis'
        )
        ModuleBayTemplate.objects.create(
            device_type=device_type,
            name='Bay 1',
            position='1'
        )

        # Create line card module type with nested bay
        line_card_type = ModuleType.objects.create(
            manufacturer=manufacturer,
            model='T1 Line Card'
        )
        ModuleBayTemplate.objects.create(
            module_type=line_card_type,
            name='Nested Bay 2',
            position='2'
        )

        # Create SFP module type with 2-token interface template
        sfp_type = ModuleType.objects.create(
            manufacturer=manufacturer,
            model='T1 SFP'
        )
        InterfaceTemplate.objects.create(
            module_type=sfp_type,
            name='SFP {module}/{module}',
            type=InterfaceTypeChoices.TYPE_10GE_SFP_PLUS
        )

        # Create device and install modules
        device = Device.objects.create(
            name='T1 Device',
            device_type=device_type,
            role=device_role,
            site=site
        )

        # Install line card at position 1
        line_card_bay = device.modulebays.get(name='Bay 1')
        line_card = Module.objects.create(
            device=device,
            module_bay=line_card_bay,
            module_type=line_card_type
        )

        # Install SFP at nested bay (position 2)
        sfp_bay = line_card.modulebays.get(name='Nested Bay 2')
        sfp_module = Module.objects.create(
            device=device,
            module_bay=sfp_bay,
            module_type=sfp_type
        )

        # Verify level-by-level substitution: 1/2 (not 1/2/1/2)
        interface = sfp_module.interfaces.first()
        self.assertEqual(interface.name, 'SFP 1/2')

    def test_multi_token_deeper_tree_only_consumes_tokens(self):
        """
        T2: Multi-token with deeper tree only consumes tokens (depth=3, tokens=2).
        2 tokens → 2 levels, even if tree is deeper.
        """
        site = Site.objects.create(name='T2 Site', slug='t2-site')
        manufacturer = Manufacturer.objects.create(name='T2 Manufacturer', slug='t2-manufacturer')
        device_role = DeviceRole.objects.create(name='T2 Role', slug='t2-role')

        # Create device type with module bay
        device_type = DeviceType.objects.create(
            manufacturer=manufacturer,
            model='T2 Chassis',
            slug='t2-chassis'
        )
        ModuleBayTemplate.objects.create(
            device_type=device_type,
            name='Bay 1',
            position='1'
        )

        # Create level 2 module type with nested bay
        level2_type = ModuleType.objects.create(
            manufacturer=manufacturer,
            model='T2 Level2'
        )
        ModuleBayTemplate.objects.create(
            module_type=level2_type,
            name='Level2 Bay',
            position='1'
        )

        # Create level 3 module type with nested bay
        level3_type = ModuleType.objects.create(
            manufacturer=manufacturer,
            model='T2 Level3'
        )
        ModuleBayTemplate.objects.create(
            module_type=level3_type,
            name='Level3 Bay',
            position='1'
        )

        # Create leaf module type with 2-token interface template
        leaf_type = ModuleType.objects.create(
            manufacturer=manufacturer,
            model='T2 Leaf'
        )
        InterfaceTemplate.objects.create(
            module_type=leaf_type,
            name='SFP {module}/{module}',
            type=InterfaceTypeChoices.TYPE_10GE_SFP_PLUS
        )

        # Create device and install 3 levels of modules
        device = Device.objects.create(
            name='T2 Device',
            device_type=device_type,
            role=device_role,
            site=site
        )

        # Level 1
        bay1 = device.modulebays.get(name='Bay 1')
        module1 = Module.objects.create(
            device=device,
            module_bay=bay1,
            module_type=level2_type
        )

        # Level 2
        bay2 = module1.modulebays.get(name='Level2 Bay')
        module2 = Module.objects.create(
            device=device,
            module_bay=bay2,
            module_type=level3_type
        )

        # Level 3 (leaf)
        bay3 = module2.modulebays.get(name='Level3 Bay')
        leaf_module = Module.objects.create(
            device=device,
            module_bay=bay3,
            module_type=leaf_type
        )

        # Verify: 2 tokens → consumes first 2 levels only: "1/1" (not "1/1/1")
        interface = leaf_module.interfaces.first()
        self.assertEqual(interface.name, 'SFP 1/1')

    def test_too_many_tokens_fails_validation(self):
        """
        T3: Too-many-tokens still fails (depth=2, tokens=3).
        Confirms the validation prevents impossible substitution.
        """
        from dcim.forms import ModuleForm

        site = Site.objects.create(name='T3 Site', slug='t3-site')
        manufacturer = Manufacturer.objects.create(name='T3 Manufacturer', slug='t3-manufacturer')
        device_role = DeviceRole.objects.create(name='T3 Role', slug='t3-role')

        # Create device type with module bay
        device_type = DeviceType.objects.create(
            manufacturer=manufacturer,
            model='T3 Chassis',
            slug='t3-chassis'
        )
        ModuleBayTemplate.objects.create(
            device_type=device_type,
            name='Bay 1',
            position='1'
        )

        # Create line card module type with nested bay
        line_card_type = ModuleType.objects.create(
            manufacturer=manufacturer,
            model='T3 Line Card'
        )
        ModuleBayTemplate.objects.create(
            module_type=line_card_type,
            name='Nested Bay',
            position='1'
        )

        # Create leaf module type with 3-token interface template (too many!)
        leaf_type = ModuleType.objects.create(
            manufacturer=manufacturer,
            model='T3 Leaf'
        )
        InterfaceTemplate.objects.create(
            module_type=leaf_type,
            name='{module}/{module}/{module}',
            type=InterfaceTypeChoices.TYPE_10GE_SFP_PLUS
        )

        # Create device and install line card
        device = Device.objects.create(
            name='T3 Device',
            device_type=device_type,
            role=device_role,
            site=site
        )

        bay1 = device.modulebays.get(name='Bay 1')
        line_card = Module.objects.create(
            device=device,
            module_bay=bay1,
            module_type=line_card_type
        )

        # Attempt to install leaf module at depth=2 with 3 tokens - should fail
        nested_bay = line_card.modulebays.get(name='Nested Bay')

        form = ModuleForm(data={
            'device': device.pk,
            'module_bay': nested_bay.pk,
            'module_type': leaf_type.pk,
            'status': 'active',
            'replicate_components': True,
            'adopt_components': False,
        })

        self.assertFalse(form.is_valid())
        # Check the error message mentions the mismatch
        self.assertIn('2', str(form.errors))
        self.assertIn('3', str(form.errors))

    def test_label_substitution_matches_name_depth_2(self):
        """
        T4: Label substitution works the same way as name (depth=2 single-token).
        """
        site = Site.objects.create(name='T4 Site', slug='t4-site')
        manufacturer = Manufacturer.objects.create(name='T4 Manufacturer', slug='t4-manufacturer')
        device_role = DeviceRole.objects.create(name='T4 Role', slug='t4-role')

        # Create device type with module bay
        device_type = DeviceType.objects.create(
            manufacturer=manufacturer,
            model='T4 Chassis',
            slug='t4-chassis'
        )
        ModuleBayTemplate.objects.create(
            device_type=device_type,
            name='Bay 1',
            position='1'
        )

        # Create line card module type with nested bay at position 2
        line_card_type = ModuleType.objects.create(
            manufacturer=manufacturer,
            model='T4 Line Card'
        )
        ModuleBayTemplate.objects.create(
            module_type=line_card_type,
            name='Nested Bay',
            position='2'
        )

        # Create leaf module type with single-token name AND label
        leaf_type = ModuleType.objects.create(
            manufacturer=manufacturer,
            model='T4 Leaf'
        )
        InterfaceTemplate.objects.create(
            module_type=leaf_type,
            name='SFP {module}',
            label='LBL {module}',
            type=InterfaceTypeChoices.TYPE_10GE_SFP_PLUS
        )

        # Create device and install modules
        device = Device.objects.create(
            name='T4 Device',
            device_type=device_type,
            role=device_role,
            site=site
        )

        bay1 = device.modulebays.get(name='Bay 1')
        line_card = Module.objects.create(
            device=device,
            module_bay=bay1,
            module_type=line_card_type
        )

        nested_bay = line_card.modulebays.get(name='Nested Bay')
        leaf_module = Module.objects.create(
            device=device,
            module_bay=nested_bay,
            module_type=leaf_type
        )

        # Verify both name and label resolve to full path
        interface = leaf_module.interfaces.first()
        self.assertEqual(interface.name, 'SFP 1/2')
        self.assertEqual(interface.label, 'LBL 1/2')

    def test_non_interface_component_template_substitution(self):
        """
        T5: Non-interface modular component templates (ConsolePortTemplate).
        Ensures the fix is general to all ModularComponentTemplateModel subclasses.
        """
        site = Site.objects.create(name='T5 Site', slug='t5-site')
        manufacturer = Manufacturer.objects.create(name='T5 Manufacturer', slug='t5-manufacturer')
        device_role = DeviceRole.objects.create(name='T5 Role', slug='t5-role')

        # Create device type with module bay
        device_type = DeviceType.objects.create(
            manufacturer=manufacturer,
            model='T5 Chassis',
            slug='t5-chassis'
        )
        ModuleBayTemplate.objects.create(
            device_type=device_type,
            name='Bay 1',
            position='1'
        )

        # Create line card module type with nested bay at position 2
        line_card_type = ModuleType.objects.create(
            manufacturer=manufacturer,
            model='T5 Line Card'
        )
        ModuleBayTemplate.objects.create(
            module_type=line_card_type,
            name='Nested Bay',
            position='2'
        )

        # Create leaf module type with ConsolePortTemplate using single token
        leaf_type = ModuleType.objects.create(
            manufacturer=manufacturer,
            model='T5 Leaf'
        )
        ConsolePortTemplate.objects.create(
            module_type=leaf_type,
            name='Console {module}',
            label='{module}'
        )

        # Create device and install modules
        device = Device.objects.create(
            name='T5 Device',
            device_type=device_type,
            role=device_role,
            site=site
        )

        bay1 = device.modulebays.get(name='Bay 1')
        line_card = Module.objects.create(
            device=device,
            module_bay=bay1,
            module_type=line_card_type
        )

        nested_bay = line_card.modulebays.get(name='Nested Bay')
        leaf_module = Module.objects.create(
            device=device,
            module_bay=nested_bay,
            module_type=leaf_type
        )

        # Verify ConsolePort resolves with full path
        console_port = leaf_module.consoleports.first()
        self.assertEqual(console_port.name, 'Console 1/2')
        self.assertEqual(console_port.label, '1/2')

    def test_positions_with_slashes_join_correctly(self):
        """
        T6: Positions that already contain slashes don't break joining (depth=2, single token).
        Some platforms use positions like 0/1 (PIC/port style) even before nesting.
        """
        site = Site.objects.create(name='T6 Site', slug='t6-site')
        manufacturer = Manufacturer.objects.create(name='T6 Manufacturer', slug='t6-manufacturer')
        device_role = DeviceRole.objects.create(name='T6 Role', slug='t6-role')

        # Create device type with module bay using slash in position
        device_type = DeviceType.objects.create(
            manufacturer=manufacturer,
            model='T6 Chassis',
            slug='t6-chassis'
        )
        ModuleBayTemplate.objects.create(
            device_type=device_type,
            name='PIC Bay',
            position='0/1'  # Position already contains slash
        )

        # Create line card module type with nested bay at position 2
        line_card_type = ModuleType.objects.create(
            manufacturer=manufacturer,
            model='T6 Line Card'
        )
        ModuleBayTemplate.objects.create(
            module_type=line_card_type,
            name='Nested Bay',
            position='2'
        )

        # Create leaf module type with single-token interface template
        leaf_type = ModuleType.objects.create(
            manufacturer=manufacturer,
            model='T6 Leaf'
        )
        InterfaceTemplate.objects.create(
            module_type=leaf_type,
            name='Gi{module}',
            type=InterfaceTypeChoices.TYPE_1GE_FIXED
        )

        # Create device and install modules
        device = Device.objects.create(
            name='T6 Device',
            device_type=device_type,
            role=device_role,
            site=site
        )

        bay1 = device.modulebays.get(name='PIC Bay')
        line_card = Module.objects.create(
            device=device,
            module_bay=bay1,
            module_type=line_card_type
        )

        nested_bay = line_card.modulebays.get(name='Nested Bay')
        leaf_module = Module.objects.create(
            device=device,
            module_bay=nested_bay,
            module_type=leaf_type
        )

        # Verify: 0/1 + 2 = 0/1/2
        interface = leaf_module.interfaces.first()
        self.assertEqual(interface.name, 'Gi0/1/2')

    def test_depth_1_single_token_no_extra_slashes(self):
        """
        T7: Ensure depth=1 single-token still resolves to the position, not an unnecessary "path join".
        """
        site = Site.objects.create(name='T7 Site', slug='t7-site')
        manufacturer = Manufacturer.objects.create(name='T7 Manufacturer', slug='t7-manufacturer')
        device_role = DeviceRole.objects.create(name='T7 Role', slug='t7-role')

        # Create device type with module bay at position 7
        device_type = DeviceType.objects.create(
            manufacturer=manufacturer,
            model='T7 Chassis',
            slug='t7-chassis'
        )
        ModuleBayTemplate.objects.create(
            device_type=device_type,
            name='Bay 7',
            position='7'
        )

        # Create module type with single-token template
        module_type = ModuleType.objects.create(
            manufacturer=manufacturer,
            model='T7 Module'
        )
        InterfaceTemplate.objects.create(
            module_type=module_type,
            name='{module}',
            type=InterfaceTypeChoices.TYPE_1GE_FIXED
        )

        # Create device and install module directly at depth=1
        device = Device.objects.create(
            name='T7 Device',
            device_type=device_type,
            role=device_role,
            site=site
        )

        bay = device.modulebays.get(name='Bay 7')
        module = Module.objects.create(
            device=device,
            module_bay=bay,
            module_type=module_type
        )

        # Verify: just "7", not "7/" or similar
        interface = module.interfaces.first()
        self.assertEqual(interface.name, '7')

    def test_multi_occurrence_tokens_level_by_level(self):
        """
        T8: Multiple occurrences of {module} in a single template (token_count > 1) still level-by-level.
        Ensure the token_count logic and replacement loop behaves with duplicated patterns.
        """
        site = Site.objects.create(name='T8 Site', slug='t8-site')
        manufacturer = Manufacturer.objects.create(name='T8 Manufacturer', slug='t8-manufacturer')
        device_role = DeviceRole.objects.create(name='T8 Role', slug='t8-role')

        # Create device type with module bay
        device_type = DeviceType.objects.create(
            manufacturer=manufacturer,
            model='T8 Chassis',
            slug='t8-chassis'
        )
        ModuleBayTemplate.objects.create(
            device_type=device_type,
            name='Bay 1',
            position='1'
        )

        # Create line card module type with nested bay at position 2
        line_card_type = ModuleType.objects.create(
            manufacturer=manufacturer,
            model='T8 Line Card'
        )
        ModuleBayTemplate.objects.create(
            module_type=line_card_type,
            name='Nested Bay',
            position='2'
        )

        # Create leaf module type with 2-token template (non-slash separator)
        leaf_type = ModuleType.objects.create(
            manufacturer=manufacturer,
            model='T8 Leaf'
        )
        InterfaceTemplate.objects.create(
            module_type=leaf_type,
            name='X{module}-Y{module}',
            type=InterfaceTypeChoices.TYPE_1GE_FIXED
        )

        # Create device and install modules
        device = Device.objects.create(
            name='T8 Device',
            device_type=device_type,
            role=device_role,
            site=site
        )

        bay1 = device.modulebays.get(name='Bay 1')
        line_card = Module.objects.create(
            device=device,
            module_bay=bay1,
            module_type=line_card_type
        )

        nested_bay = line_card.modulebays.get(name='Nested Bay')
        leaf_module = Module.objects.create(
            device=device,
            module_bay=nested_bay,
            module_type=leaf_type
        )

        # Verify: X1-Y2 (level-by-level, not full-path stuffed into first)
        interface = leaf_module.interfaces.first()
        self.assertEqual(interface.name, 'X1-Y2')


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
        interfaces = (
            Interface(device=device1, name='eth0'),
            Interface(device=device2, name='eth0'),
            Interface(device=device2, name='eth1'),
        )
        Interface.objects.bulk_create(interfaces)
        Cable(a_terminations=[interfaces[0]], b_terminations=[interfaces[1]]).save()
        PowerPort.objects.create(device=device2, name='psu1')

        patch_panel = Device.objects.create(
            device_type=devicetype, role=role, name='TestPatchPanel', site=site
        )
        rear_ports = (
            RearPort(device=patch_panel, name='RP1', type='8p8c'),
            RearPort(device=patch_panel, name='RP2', type='8p8c', positions=2),
            RearPort(device=patch_panel, name='RP3', type='8p8c', positions=3),
            RearPort(device=patch_panel, name='RP4', type='8p8c', positions=3),
        )
        RearPort.objects.bulk_create(rear_ports)
        front_ports = (
            FrontPort(device=patch_panel, name='FP1', type='8p8c'),
            FrontPort(device=patch_panel, name='FP2', type='8p8c'),
            FrontPort(device=patch_panel, name='FP3', type='8p8c'),
            FrontPort(device=patch_panel, name='FP4', type='8p8c'),
        )
        FrontPort.objects.bulk_create(front_ports)
        PortMapping.objects.bulk_create([
            PortMapping(device=patch_panel, front_port=front_ports[0], rear_port=rear_ports[0]),
            PortMapping(device=patch_panel, front_port=front_ports[1], rear_port=rear_ports[1]),
            PortMapping(device=patch_panel, front_port=front_ports[2], rear_port=rear_ports[2]),
            PortMapping(device=patch_panel, front_port=front_ports[3], rear_port=rear_ports[3]),
        ])

        provider = Provider.objects.create(name='Provider 1', slug='provider-1')
        provider_network = ProviderNetwork.objects.create(name='Provider Network 1', provider=provider)
        circuittype = CircuitType.objects.create(name='Circuit Type 1', slug='circuit-type-1')
        circuit1 = Circuit.objects.create(provider=provider, type=circuittype, cid='1')
        circuit2 = Circuit.objects.create(provider=provider, type=circuittype, cid='2')
        CircuitTermination.objects.create(circuit=circuit1, termination=site, term_side='A')
        CircuitTermination.objects.create(circuit=circuit1, termination=site, term_side='Z')
        CircuitTermination.objects.create(circuit=circuit2, termination=provider_network, term_side='A')

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

    @tag('regression')
    def test_cable_cannot_terminate_to_a_cellular_interface(self):
        """
        A cable cannot terminate to a cellular interface
        """
        device1 = Device.objects.get(name='TestDevice1')
        interface2 = Interface.objects.get(device__name='TestDevice2', name='eth0')

        cellular_interface = Interface(device=device1, name="W1", type=InterfaceTypeChoices.TYPE_LTE)
        cable = Cable(a_terminations=[interface2], b_terminations=[cellular_interface])
        with self.assertRaises(ValidationError):
            cable.clean()

    def test_cannot_cable_to_mark_connected(self):
        """
        Test that a cable cannot be connected to an interface marked as connected.
        """
        device1 = Device.objects.get(name='TestDevice1')
        interface1 = Interface.objects.get(device__name='TestDevice2', name='eth1')

        mark_connected_interface = Interface(device=device1, name='mark_connected1', mark_connected=True)
        cable = Cable(a_terminations=[mark_connected_interface], b_terminations=[interface1])
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


class VirtualChassisTestCase(TestCase):

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
        Device.objects.create(
            device_type=devicetype, role=role, name='TestDevice2', site=site
        )

    def test_virtualchassis_deletion_clears_vc_position(self):
        """
        Test that when a VirtualChassis is deleted, member devices have their
        vc_position and vc_priority fields set to None.
        """
        devices = Device.objects.all()
        device1 = devices[0]
        device2 = devices[1]

        # Create a VirtualChassis with two member devices
        vc = VirtualChassis.objects.create(name='Test VC', master=device1)

        device1.virtual_chassis = vc
        device1.vc_position = 1
        device1.vc_priority = 10
        device1.save()

        device2.virtual_chassis = vc
        device2.vc_position = 2
        device2.vc_priority = 20
        device2.save()

        # Verify devices are members of the VC with positions set
        device1.refresh_from_db()
        device2.refresh_from_db()
        self.assertEqual(device1.virtual_chassis, vc)
        self.assertEqual(device1.vc_position, 1)
        self.assertEqual(device1.vc_priority, 10)
        self.assertEqual(device2.virtual_chassis, vc)
        self.assertEqual(device2.vc_position, 2)
        self.assertEqual(device2.vc_priority, 20)

        # Delete the VirtualChassis
        vc.delete()

        # Verify devices have vc_position and vc_priority set to None
        device1.refresh_from_db()
        device2.refresh_from_db()
        self.assertIsNone(device1.virtual_chassis)
        self.assertIsNone(device1.vc_position)
        self.assertIsNone(device1.vc_priority)
        self.assertIsNone(device2.virtual_chassis)
        self.assertIsNone(device2.vc_position)
        self.assertIsNone(device2.vc_priority)

    def test_virtualchassis_duplicate_vc_position(self):
        """
        Test that two devices cannot be assigned to the same vc_position
        within the same VirtualChassis.
        """
        devices = Device.objects.all()
        device1 = devices[0]
        device2 = devices[1]

        # Create a VirtualChassis
        vc = VirtualChassis.objects.create(name='Test VC')

        # Assign first device to vc_position 1
        device1.virtual_chassis = vc
        device1.vc_position = 1
        device1.full_clean()
        device1.save()

        # Try to assign second device to the same vc_position
        device2.virtual_chassis = vc
        device2.vc_position = 1
        with self.assertRaises(ValidationError):
            device2.full_clean()
