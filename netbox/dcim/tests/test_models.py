from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db.models.signals import post_save
from django.test import TestCase, tag

from circuits.models import *
from core.models import ObjectType
from dcim.choices import *
from dcim.models import *
from extras.events import serialize_for_event
from extras.models import CustomField
from ipam.models import Prefix
from netbox.choices import DiameterUnitChoices, FlowRateUnitChoices, WeightUnitChoices
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


class DeviceTypeTestCase(TestCase):

    def test_component_template_counts(self):
        """
        DeviceType component template counters should track the addition and removal of templates.
        """
        manufacturer = Manufacturer.objects.create(name='Manufacturer 1', slug='manufacturer-1')
        device_type = DeviceType.objects.create(
            manufacturer=manufacturer, model='Device Type 1', slug='device-type-1'
        )

        # Counters should start at zero
        self.assertEqual(device_type.interface_template_count, 0)
        self.assertEqual(device_type.console_port_template_count, 0)
        self.assertEqual(device_type.module_bay_template_count, 0)
        self.assertEqual(device_type.device_bay_template_count, 0)

        # Adding templates should increment the relevant counters
        InterfaceTemplate.objects.create(device_type=device_type, name='Interface 1')
        InterfaceTemplate.objects.create(device_type=device_type, name='Interface 2')
        ConsolePortTemplate.objects.create(device_type=device_type, name='Console 1')
        ModuleBayTemplate.objects.create(device_type=device_type, name='Module Bay 1')
        DeviceBayTemplate.objects.create(device_type=device_type, name='Device Bay 1')
        device_type.refresh_from_db()
        self.assertEqual(device_type.interface_template_count, 2)
        self.assertEqual(device_type.console_port_template_count, 1)
        self.assertEqual(device_type.module_bay_template_count, 1)
        self.assertEqual(device_type.device_bay_template_count, 1)

        # Deleting a template should decrement the counter
        InterfaceTemplate.objects.get(device_type=device_type, name='Interface 1').delete()
        device_type.refresh_from_db()
        self.assertEqual(device_type.interface_template_count, 1)


class ModuleTypeTestCase(TestCase):

    def test_component_template_counts(self):
        """
        ModuleType component template counters should track the addition and removal of templates.
        """
        manufacturer = Manufacturer.objects.create(name='Manufacturer 1', slug='manufacturer-1')
        module_type = ModuleType.objects.create(manufacturer=manufacturer, model='Module Type 1')

        # Counters should start at zero
        self.assertEqual(module_type.interface_template_count, 0)
        self.assertEqual(module_type.console_port_template_count, 0)
        self.assertEqual(module_type.module_bay_template_count, 0)

        # Adding templates should increment the relevant counters
        InterfaceTemplate.objects.create(module_type=module_type, name='Interface 1')
        InterfaceTemplate.objects.create(module_type=module_type, name='Interface 2')
        ConsolePortTemplate.objects.create(module_type=module_type, name='Console 1')
        ModuleBayTemplate.objects.create(module_type=module_type, name='Module Bay 1')
        module_type.refresh_from_db()
        self.assertEqual(module_type.interface_template_count, 2)
        self.assertEqual(module_type.console_port_template_count, 1)
        self.assertEqual(module_type.module_bay_template_count, 1)

        # Deleting a template should decrement the counter
        InterfaceTemplate.objects.get(module_type=module_type, name='Interface 1').delete()
        module_type.refresh_from_db()
        self.assertEqual(module_type.interface_template_count, 1)

    def test_attributes(self):
        """
        ModuleType.attributes should normalize iterable values into strings for presentation.
        """
        manufacturer = Manufacturer.objects.create(name='Manufacturer 1', slug='manufacturer-1')
        profile = ModuleTypeProfile.objects.create(
            name='Module Type Profile 1',
            schema={
                'properties': {
                    'media': {
                        'title': 'Media',
                        'type': 'array',
                        'items': {'type': 'string'},
                    },
                    'enabled': {
                        'title': 'Enabled',
                        'type': 'boolean',
                    },
                },
            },
        )
        module_type = ModuleType.objects.create(
            manufacturer=manufacturer,
            model='Module Type 1',
            profile=profile,
            attribute_data={
                'media': ['sfp', 'qsfp28'],
                'enabled': True,
            },
        )

        self.assertEqual(
            module_type.attributes,
            {
                'Enabled': True,
                'Media': 'sfp, qsfp28',
            },
        )


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
            cooling_capability=RackCoolingCapabilityChoices.LIQUID_REQUIRED,
            cooling_capacity=80,
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
            rack_type=rack_type,
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
        # Cooling capability/capacity are inherited from the rack type
        self.assertEqual(rack.cooling_capability, rack_type.cooling_capability)
        self.assertEqual(rack.cooling_capacity, rack_type.cooling_capacity)


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

    def test_empty_asset_tag_coerced_to_null_on_clean(self):
        """
        An empty string assigned to a unique nullable CharField (e.g. asset_tag) must be coerced
        to None on save so that multiple objects can be saved without violating the unique
        constraint. Test that this is done on clean().
        """
        common_kwargs = {
            'site': Site.objects.first(),
            'device_type': DeviceType.objects.first(),
            'role': DeviceRole.objects.first(),
        }
        device1 = Device(name='Device 1', asset_tag='', **common_kwargs)
        device1.clean()
        self.assertIsNone(device1.asset_tag)

    def test_empty_asset_tag_coerced_to_null_on_save(self):
        """
        An empty string assigned to a unique nullable CharField (e.g. asset_tag) must be coerced
        to None on save so that multiple objects can be saved without violating the unique
        constraint. Test that this is done on save().
        """
        common_kwargs = {
            'site': Site.objects.first(),
            'device_type': DeviceType.objects.first(),
            'role': DeviceRole.objects.first(),
        }
        device1 = Device(name='Device 1', asset_tag='', **common_kwargs)
        device1.save()
        device2 = Device(name='Device 2', asset_tag='', **common_kwargs)
        device2.save()

        device1.refresh_from_db()
        device2.refresh_from_db()
        self.assertIsNone(device1.asset_tag)
        self.assertIsNone(device2.asset_tag)

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


class DeviceBayTestCase(TestCase):

    @classmethod
    def setUpTestData(cls):
        site = Site.objects.create(name='Test Site 1', slug='test-site-1')
        manufacturer = Manufacturer.objects.create(name='Test Manufacturer 1', slug='test-manufacturer-1')

        # Parent device type must support device bays (is_parent_device=True)
        parent_device_type = DeviceType.objects.create(
            manufacturer=manufacturer,
            model='Parent Device Type',
            slug='parent-device-type',
            subdevice_role=SubdeviceRoleChoices.ROLE_PARENT
        )
        # Child device type for installation
        child_device_type = DeviceType.objects.create(
            manufacturer=manufacturer,
            model='Child Device Type',
            slug='child-device-type',
            u_height=0,
            subdevice_role=SubdeviceRoleChoices.ROLE_CHILD
        )
        device_role = DeviceRole.objects.create(name='Test Role 1', slug='test-role-1')

        cls.parent_device = Device.objects.create(
            name='Parent Device',
            device_type=parent_device_type,
            role=device_role,
            site=site
        )
        cls.child_device = Device.objects.create(
            name='Child Device',
            device_type=child_device_type,
            role=device_role,
            site=site
        )
        cls.child_device_2 = Device.objects.create(
            name='Child Device 2',
            device_type=child_device_type,
            role=device_role,
            site=site
        )

    def test_cannot_install_device_in_disabled_bay(self):
        """
        Test that a device cannot be installed into a disabled DeviceBay.
        """
        # Create a disabled device bay with a device being installed
        device_bay = DeviceBay(
            device=self.parent_device,
            name='Disabled Bay',
            enabled=False,
            installed_device=self.child_device
        )

        with self.assertRaises(ValidationError) as cm:
            device_bay.clean()

        self.assertIn('installed_device', cm.exception.message_dict)
        self.assertIn('disabled device bay', str(cm.exception.message_dict['installed_device']))

    def test_can_disable_bay_with_existing_device(self):
        """
        Test that disabling a bay that already has a device installed does NOT raise an error
        (same installed_device_id).
        """
        # First, create an enabled device bay with a device installed
        device_bay = DeviceBay.objects.create(
            device=self.parent_device,
            name='Bay To Disable',
            enabled=True,
            installed_device=self.child_device
        )

        # Now disable the bay while keeping the same installed device
        device_bay.enabled = False
        # This should NOT raise a ValidationError
        device_bay.clean()
        device_bay.save()

        device_bay.refresh_from_db()
        self.assertFalse(device_bay.enabled)
        self.assertEqual(device_bay.installed_device, self.child_device)

    def test_cannot_change_installed_device_in_disabled_bay(self):
        """
        Test that changing the installed device in a disabled bay raises a ValidationError.
        """
        # Create an enabled device bay with a device installed
        device_bay = DeviceBay.objects.create(
            device=self.parent_device,
            name='Bay With Device',
            enabled=True,
            installed_device=self.child_device
        )

        # Disable the bay and try to change the installed device
        device_bay.enabled = False
        device_bay.installed_device = self.child_device_2

        with self.assertRaises(ValidationError) as cm:
            device_bay.clean()

        self.assertIn('installed_device', cm.exception.message_dict)


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

        # Confirm error if Module recurses (empty target bay, so the occupied-bay check cannot mask it)
        module_bay_4 = ModuleBay.objects.create(device=module_1.device, name='Module Bay 4', module=module_3)
        with self.assertRaisesMessage(ValidationError, 'cannot belong to a module installed within it'):
            module_1.module_bay = module_bay_4
            module_1.clean()
            module_1.save()

    @tag('regression')  # #22146
    def test_module_bay_ordering_after_recreate(self):
        """
        Module bays must remain in name order after a delete-and-recreate cycle,
        even though MPTT no longer renumbers tree_ids on root insertion.
        """
        device_type = DeviceType.objects.first()
        device_role = DeviceRole.objects.first()
        site = Site.objects.first()
        device = Device.objects.create(
            name='Ordering Test Device',
            device_type=device_type,
            role=device_role,
            site=site,
        )
        for name in ('Bay 1', 'Bay 2', 'Bay 3', 'Bay 4'):
            ModuleBay.objects.create(device=device, name=name)

        ModuleBay.objects.get(device=device, name='Bay 3').delete()
        ModuleBay.objects.create(device=device, name='Bay 3')

        names = list(ModuleBay.objects.filter(device=device).values_list('name', flat=True))
        self.assertEqual(names, ['Bay 1', 'Bay 2', 'Bay 3', 'Bay 4'])

    @tag('regression')  # #22146
    def test_module_bay_natural_ordering(self):
        """
        Module bays must be returned in natural (numeric-aware) order, e.g.
        "Bay 2" before "Bay 10".
        """
        device_type = DeviceType.objects.first()
        device_role = DeviceRole.objects.first()
        site = Site.objects.first()
        device = Device.objects.create(
            name='Natural Sort Device',
            device_type=device_type,
            role=device_role,
            site=site,
        )
        # Insert in non-natural order to confirm sort is not insertion-driven.
        for name in ('Bay 10', 'Bay 1', 'Bay 2', 'Bay 11'):
            ModuleBay.objects.create(device=device, name=name)

        names = list(ModuleBay.objects.filter(device=device).values_list('name', flat=True))
        self.assertEqual(names, ['Bay 1', 'Bay 2', 'Bay 10', 'Bay 11'])

    @tag('regression')  # #22146
    def test_child_module_bay_ordering(self):
        """
        Child module bays inside a module must be returned in name order even
        when inserted out of order.
        """
        device_type = DeviceType.objects.first()
        device_role = DeviceRole.objects.first()
        site = Site.objects.first()
        device = Device.objects.create(
            name='Child Ordering Device',
            device_type=device_type,
            role=device_role,
            site=site,
        )
        root_bay = ModuleBay.objects.create(device=device, name='Bay 1')
        manufacturer = Manufacturer.objects.first()
        module_type = ModuleType.objects.create(
            manufacturer=manufacturer, model='Child Ordering Type'
        )
        module = Module.objects.create(
            device=device, module_bay=root_bay, module_type=module_type
        )
        # Insert children out of name order.
        for name in ('Bay 1.1', 'Bay 1.3', 'Bay 1.2'):
            ModuleBay.objects.create(device=device, module=module, name=name)

        names = list(ModuleBay.objects.filter(device=device).values_list('name', flat=True))
        self.assertEqual(names, ['Bay 1', 'Bay 1.1', 'Bay 1.2', 'Bay 1.3'])

    @tag('regression')  # #22146
    def test_root_module_bay_rename_preserves_paths(self):
        """
        Renaming a root module bay must not rewrite any tree's path. Renaming
        touches only sort_path (the display-ordering column), so every bay's
        path — including the renamed bay's own — must be unchanged afterward.
        """
        device_type = DeviceType.objects.first()
        device_role = DeviceRole.objects.first()
        site = Site.objects.first()
        device = Device.objects.create(
            name='Rename Path Device',
            device_type=device_type,
            role=device_role,
            site=site,
        )
        for name in ('Bay 1', 'Bay 2', 'Bay 3', 'Bay 4'):
            ModuleBay.objects.create(device=device, name=name)

        paths_before = {
            bay.pk: str(bay.path)
            for bay in ModuleBay.objects.filter(device=device)
        }

        bay = ModuleBay.objects.get(device=device, name='Bay 2')
        bay.name = 'Bay 99'
        bay.save()

        paths_after = {
            bay.pk: str(bay.path)
            for bay in ModuleBay.objects.filter(device=device)
        }
        self.assertEqual(paths_after, paths_before)

    @tag('regression')  # #22146
    def test_root_module_bay_rename_updates_display_order(self):
        """
        Even though renaming a root module bay does not rewrite its path,
        the manager's _root_name annotation must reflect the new name so the
        display ordering is correct.
        """
        device_type = DeviceType.objects.first()
        device_role = DeviceRole.objects.first()
        site = Site.objects.first()
        device = Device.objects.create(
            name='Rename Order Device',
            device_type=device_type,
            role=device_role,
            site=site,
        )
        for name in ('Bay 1', 'Bay 2', 'Bay 3'):
            ModuleBay.objects.create(device=device, name=name)

        bay = ModuleBay.objects.get(device=device, name='Bay 1')
        bay.name = 'Bay 4'
        bay.save()

        names = list(ModuleBay.objects.filter(device=device).values_list('name', flat=True))
        self.assertEqual(names, ['Bay 2', 'Bay 3', 'Bay 4'])

    @tag('regression')  # #22146
    def test_child_module_bay_rename_preserves_intra_tree_ordering(self):
        """
        Renaming a *child* module bay must still trigger MPTT's intra-tree
        reorder, so siblings appear in name order after the rename. The
        rename-bypass only covers root bays.
        """
        device_type = DeviceType.objects.first()
        device_role = DeviceRole.objects.first()
        site = Site.objects.first()
        device = Device.objects.create(
            name='Child Rename Device',
            device_type=device_type,
            role=device_role,
            site=site,
        )
        root_bay = ModuleBay.objects.create(device=device, name='Bay 1')
        manufacturer = Manufacturer.objects.first()
        module_type = ModuleType.objects.create(
            manufacturer=manufacturer, model='Child Rename Type'
        )
        module = Module.objects.create(
            device=device, module_bay=root_bay, module_type=module_type
        )
        for name in ('Bay 1.1', 'Bay 1.2', 'Bay 1.3'):
            ModuleBay.objects.create(device=device, module=module, name=name)

        child = ModuleBay.objects.get(device=device, name='Bay 1.1')
        child.name = 'Bay 1.4'
        child.save()

        names = list(ModuleBay.objects.filter(device=device).values_list('name', flat=True))
        self.assertEqual(names, ['Bay 1', 'Bay 1.2', 'Bay 1.3', 'Bay 1.4'])

    @tag('regression')  # #22146
    def test_root_to_child_transition_still_relocates(self):
        """
        Promoting an existing root module bay to a child (by assigning a
        module) must still flow through MPTT's normal move logic. The
        rename-bypass must not suppress legitimate parent changes.
        """
        device_type = DeviceType.objects.first()
        device_role = DeviceRole.objects.first()
        site = Site.objects.first()
        device = Device.objects.create(
            name='Root To Child Device',
            device_type=device_type,
            role=device_role,
            site=site,
        )
        host_bay = ModuleBay.objects.create(device=device, name='Host Bay')
        movable_bay = ModuleBay.objects.create(device=device, name='Movable Bay')

        manufacturer = Manufacturer.objects.first()
        module_type = ModuleType.objects.create(
            manufacturer=manufacturer, model='Root To Child Type'
        )
        host_module = Module.objects.create(
            device=device, module_bay=host_bay, module_type=module_type
        )

        movable_bay.module = host_module
        movable_bay.save()

        movable_bay.refresh_from_db()
        host_bay.refresh_from_db()
        self.assertEqual(movable_bay.parent_id, host_bay.pk)
        # The trigger cascade must have re-rooted the moved bay into host_bay's
        # tree: its path is now a strict descendant of host_bay's path.
        self.assertTrue(str(movable_bay.path).startswith(f'{host_bay.path}.'))

    @tag('regression')  # #22251
    def test_moving_module_reparents_child_module_bays(self):
        """
        When a module is moved to a different module bay, each child ModuleBay
        (a bay that belongs to the module) must have its parent updated to the
        new host bay. Without the fix the children stay parented to the old bay
        even though Module.module_bay_id has changed.
        """
        device_type = DeviceType.objects.first()
        device_role = DeviceRole.objects.first()
        site = Site.objects.first()
        device = Device.objects.create(
            name='Move Module Device',
            device_type=device_type,
            role=device_role,
            site=site,
        )
        bay_a = ModuleBay.objects.create(device=device, name='Bay A')
        bay_b = ModuleBay.objects.create(device=device, name='Bay B')

        manufacturer = Manufacturer.objects.first()
        module_type = ModuleType.objects.create(
            manufacturer=manufacturer, model='Move Module Type'
        )
        module = Module.objects.create(
            device=device, module_bay=bay_a, module_type=module_type
        )

        child_1 = ModuleBay.objects.create(device=device, module=module, name='Child Bay 1')
        child_2 = ModuleBay.objects.create(device=device, module=module, name='Child Bay 2')
        self.assertEqual(child_1.parent_id, bay_a.pk)
        self.assertEqual(child_2.parent_id, bay_a.pk)

        # Move the module to bay_b.
        module.module_bay = bay_b
        module.save()

        child_1.refresh_from_db()
        child_2.refresh_from_db()
        self.assertEqual(child_1.parent_id, bay_b.pk)
        self.assertEqual(child_2.parent_id, bay_b.pk)
        # Children must be re-rooted under bay_b in the ltree hierarchy.
        bay_b.refresh_from_db()
        self.assertTrue(str(child_1.path).startswith(f'{bay_b.path}.'))
        self.assertTrue(str(child_2.path).startswith(f'{bay_b.path}.'))

    @tag('regression')  # #22251
    def test_moving_module_reparents_grandchild_module_bays(self):
        """
        When a module is moved, grandchild ModuleBays (bays inside a module
        that is itself installed inside a child bay of the moved module) must
        also land in the new ltree subtree. The trigger cascade moves subtrees
        atomically, so calling save() only on direct children is sufficient —
        this test documents and preserves that invariant for future tree-backend
        changes.
        """
        device_type = DeviceType.objects.first()
        device_role = DeviceRole.objects.first()
        site = Site.objects.first()
        device = Device.objects.create(
            name='Grandchild Move Device',
            device_type=device_type,
            role=device_role,
            site=site,
        )
        bay_a = ModuleBay.objects.create(device=device, name='Bay A')
        bay_b = ModuleBay.objects.create(device=device, name='Bay B')

        manufacturer = Manufacturer.objects.first()
        module_type = ModuleType.objects.create(
            manufacturer=manufacturer, model='Grandchild Move Type'
        )
        # Depth-1: module installed in bay_a, with one child bay.
        module_1 = Module.objects.create(device=device, module_bay=bay_a, module_type=module_type)
        child_bay = ModuleBay.objects.create(device=device, module=module_1, name='Child Bay')

        # Depth-2: module installed in child_bay, with one grandchild bay.
        module_2 = Module.objects.create(device=device, module_bay=child_bay, module_type=module_type)
        grandchild_bay = ModuleBay.objects.create(device=device, module=module_2, name='Grandchild Bay')

        self.assertEqual(child_bay.parent_id, bay_a.pk)
        self.assertEqual(grandchild_bay.parent_id, child_bay.pk)
        bay_a.refresh_from_db()
        self.assertTrue(str(grandchild_bay.path).startswith(f'{bay_a.path}.'))

        # Move the top-level module to bay_b.
        module_1.module_bay = bay_b
        module_1.save()

        child_bay.refresh_from_db()
        grandchild_bay.refresh_from_db()
        bay_b.refresh_from_db()

        self.assertEqual(child_bay.parent_id, bay_b.pk)
        self.assertTrue(str(child_bay.path).startswith(f'{bay_b.path}.'))
        # Grandchild's direct parent (child_bay) is unchanged; only tree placement moves.
        self.assertEqual(grandchild_bay.parent_id, child_bay.pk)
        self.assertTrue(str(grandchild_bay.path).startswith(f'{bay_b.path}.'))

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

    @tag('regression')  # #21418
    def test_module_install_nests_module_bay_parent(self):
        """
        A module bay instantiated when a module is installed must be nested under the
        installing module's bay. bulk_create() bypasses ModuleBay.save(), so the parent
        is assigned in ModuleBayTemplate.instantiate(); without it the bay would be left
        a root with a top-level ltree path.
        """
        manufacturer = Manufacturer.objects.first()
        site = Site.objects.first()
        device_role = DeviceRole.objects.first()

        device_type = DeviceType.objects.create(
            manufacturer=manufacturer, model='Chassis with Bay', slug='chassis-with-bay'
        )
        ModuleBayTemplate.objects.create(device_type=device_type, name='Bay A')

        module_type = ModuleType.objects.create(manufacturer=manufacturer, model='Module with Sub-bay')
        ModuleBayTemplate.objects.create(module_type=module_type, name='Sub-bay 1')

        device = Device.objects.create(
            name='Nested Bay Parent Device', device_type=device_type, role=device_role, site=site
        )
        parent_bay = device.modulebays.get(name='Bay A')
        module = Module.objects.create(device=device, module_bay=parent_bay, module_type=module_type)

        nested_bay = module.modulebays.get(name='Sub-bay 1')
        self.assertEqual(nested_bay.parent, parent_bay)
        # The ltree path/level must reflect the nesting, not a root placement.
        self.assertEqual(nested_bay.level, parent_bay.level + 1)
        self.assertTrue(str(nested_bay.path).startswith(f'{parent_bay.path}.'))

    @tag('regression')  # #20467
    def test_nested_module_bay_position_resolution(self):
        """Test that {module} in a module bay template's position field is resolved when the module is installed."""
        manufacturer = Manufacturer.objects.first()
        site = Site.objects.first()
        device_role = DeviceRole.objects.first()

        device_type = DeviceType.objects.create(
            manufacturer=manufacturer,
            model='Device with Position Test',
            slug='device-with-position-test'
        )
        ModuleBayTemplate.objects.create(
            device_type=device_type,
            name='Slot 1',
            position='1'
        )

        module_type = ModuleType.objects.create(
            manufacturer=manufacturer,
            model='Module with Position Placeholder'
        )
        ModuleBayTemplate.objects.create(
            module_type=module_type,
            name='Sub-bay {module}-1',
            position='{module}-1'
        )

        device = Device.objects.create(
            name='Position Test Device',
            device_type=device_type,
            role=device_role,
            site=site
        )
        module_bay = device.modulebays.get(name='Slot 1')
        module = Module.objects.create(
            device=device,
            module_bay=module_bay,
            module_type=module_type
        )

        nested_bay = module.modulebays.get(name='Sub-bay 1-1')
        self.assertEqual(nested_bay.position, '1-1')

    #
    # Position inheritance tests (#19796)
    #

    def test_position_inheritance_depth_2(self):
        """
        A module bay with position '{module}/2' under a parent bay with position '1'
        should resolve to position '1/2'. A single {module} in the interface template
        should then resolve to '1/2'.
        """
        manufacturer = Manufacturer.objects.first()
        site = Site.objects.first()
        device_role = DeviceRole.objects.first()

        device_type = DeviceType.objects.create(
            manufacturer=manufacturer,
            model='Chassis for Inheritance',
            slug='chassis-for-inheritance'
        )
        ModuleBayTemplate.objects.create(
            device_type=device_type,
            name='Line card slot 1',
            position='1'
        )

        line_card_type = ModuleType.objects.create(
            manufacturer=manufacturer,
            model='Line Card with Inherited Bays'
        )
        ModuleBayTemplate.objects.create(
            module_type=line_card_type,
            name='SFP bay {module}/1',
            position='{module}/1'
        )
        ModuleBayTemplate.objects.create(
            module_type=line_card_type,
            name='SFP bay {module}/2',
            position='{module}/2'
        )

        sfp_type = ModuleType.objects.create(
            manufacturer=manufacturer,
            model='SFP with Inherited Path'
        )
        InterfaceTemplate.objects.create(
            module_type=sfp_type,
            name='SFP {module}',
            type=InterfaceTypeChoices.TYPE_10GE_SFP_PLUS
        )

        device = Device.objects.create(
            name='Inheritance Chassis',
            device_type=device_type,
            role=device_role,
            site=site
        )

        lc_bay = device.modulebays.get(name='Line card slot 1')
        line_card = Module.objects.create(
            device=device,
            module_bay=lc_bay,
            module_type=line_card_type
        )

        sfp_bay = line_card.modulebays.get(name='SFP bay 1/2')
        sfp_module = Module.objects.create(
            device=device,
            module_bay=sfp_bay,
            module_type=sfp_type
        )

        interface = sfp_module.interfaces.first()
        self.assertEqual(interface.name, 'SFP 1/2')

    def test_position_inheritance_depth_3(self):
        """
        Position inheritance at depth 3: positions should chain through the tree.
        """
        manufacturer = Manufacturer.objects.first()
        site = Site.objects.first()
        device_role = DeviceRole.objects.first()

        device_type = DeviceType.objects.create(
            manufacturer=manufacturer,
            model='Deep Chassis',
            slug='deep-chassis'
        )
        ModuleBayTemplate.objects.create(
            device_type=device_type,
            name='Slot A',
            position='A'
        )

        mid_type = ModuleType.objects.create(
            manufacturer=manufacturer,
            model='Mid Module'
        )
        ModuleBayTemplate.objects.create(
            module_type=mid_type,
            name='Sub {module}-1',
            position='{module}-1'
        )

        leaf_type = ModuleType.objects.create(
            manufacturer=manufacturer,
            model='Leaf Module'
        )
        InterfaceTemplate.objects.create(
            module_type=leaf_type,
            name='Port {module}',
            type=InterfaceTypeChoices.TYPE_1GE_FIXED
        )

        device = Device.objects.create(
            name='Deep Device',
            device_type=device_type,
            role=device_role,
            site=site
        )

        slot_a = device.modulebays.get(name='Slot A')
        mid_module = Module.objects.create(
            device=device,
            module_bay=slot_a,
            module_type=mid_type
        )

        sub_bay = mid_module.modulebays.get(name='Sub A-1')
        self.assertEqual(sub_bay.position, 'A-1')

        leaf_module = Module.objects.create(
            device=device,
            module_bay=sub_bay,
            module_type=leaf_type
        )

        interface = leaf_module.interfaces.first()
        self.assertEqual(interface.name, 'Port A-1')

    def test_position_inheritance_custom_separator(self):
        """
        Users control the separator through the position field template.
        Using '.' instead of '/' should work correctly.
        """
        manufacturer = Manufacturer.objects.first()
        site = Site.objects.first()
        device_role = DeviceRole.objects.first()

        device_type = DeviceType.objects.create(
            manufacturer=manufacturer,
            model='Dot Separator Chassis',
            slug='dot-separator-chassis'
        )
        ModuleBayTemplate.objects.create(
            device_type=device_type,
            name='Bay 1',
            position='1'
        )

        card_type = ModuleType.objects.create(
            manufacturer=manufacturer,
            model='Card with Dot Separator'
        )
        ModuleBayTemplate.objects.create(
            module_type=card_type,
            name='Port {module}.1',
            position='{module}.1'
        )

        sfp_type = ModuleType.objects.create(
            manufacturer=manufacturer,
            model='SFP Dot'
        )
        InterfaceTemplate.objects.create(
            module_type=sfp_type,
            name='eth{module}',
            type=InterfaceTypeChoices.TYPE_10GE_SFP_PLUS
        )

        device = Device.objects.create(
            name='Dot Device',
            device_type=device_type,
            role=device_role,
            site=site
        )

        bay = device.modulebays.get(name='Bay 1')
        card = Module.objects.create(
            device=device,
            module_bay=bay,
            module_type=card_type
        )

        port_bay = card.modulebays.get(name='Port 1.1')
        sfp = Module.objects.create(
            device=device,
            module_bay=port_bay,
            module_type=sfp_type
        )

        interface = sfp.interfaces.first()
        self.assertEqual(interface.name, 'eth1.1')

    def test_multi_token_backwards_compat(self):
        """
        Multi-token {module}/{module} at matching depth should still resolve
        level-by-level (backwards compatibility).
        """
        manufacturer = Manufacturer.objects.first()
        site = Site.objects.first()
        device_role = DeviceRole.objects.first()

        device_type = DeviceType.objects.create(
            manufacturer=manufacturer,
            model='Multi Token Chassis',
            slug='multi-token-chassis'
        )
        ModuleBayTemplate.objects.create(
            device_type=device_type,
            name='Slot 1',
            position='1'
        )

        card_type = ModuleType.objects.create(
            manufacturer=manufacturer,
            model='Card for Multi Token'
        )
        ModuleBayTemplate.objects.create(
            module_type=card_type,
            name='Port 1',
            position='2'
        )

        iface_type = ModuleType.objects.create(
            manufacturer=manufacturer,
            model='Interface Module Multi Token'
        )
        InterfaceTemplate.objects.create(
            module_type=iface_type,
            name='Gi{module}/{module}',
            type=InterfaceTypeChoices.TYPE_1GE_FIXED
        )

        device = Device.objects.create(
            name='Multi Token Device',
            device_type=device_type,
            role=device_role,
            site=site
        )

        slot = device.modulebays.get(name='Slot 1')
        card = Module.objects.create(
            device=device,
            module_bay=slot,
            module_type=card_type
        )

        port = card.modulebays.get(name='Port 1')
        iface_module = Module.objects.create(
            device=device,
            module_bay=port,
            module_type=iface_type
        )

        interface = iface_module.interfaces.first()
        self.assertEqual(interface.name, 'Gi1/2')

    @tag('regression')  # #20912
    def test_module_bay_parent_cleared_when_module_removed(self):
        """Test that the parent field is properly cleared when a module bay's module assignment is removed"""
        device = Device.objects.first()
        manufacturer = Manufacturer.objects.first()
        module_type = ModuleType.objects.create(manufacturer=manufacturer, model='Test Module Type')
        bay1 = ModuleBay.objects.create(device=device, name='Test Bay 1')
        bay2 = ModuleBay.objects.create(device=device, name='Test Bay 2')

        # Install a module in bay1
        module1 = Module.objects.create(device=device, module_bay=bay1, module_type=module_type)

        # Assign bay2 to module1 and verify parent is now set to bay1 (module1's bay)
        bay2.module = module1
        bay2.save()
        bay2.refresh_from_db()
        self.assertEqual(bay2.parent, bay1)
        self.assertEqual(bay2.module, module1)

        # Clear the module assignment (return bay2 to device level) Verify parent is cleared
        bay2.module = None
        bay2.save()
        bay2.refresh_from_db()
        self.assertIsNone(bay2.parent)
        self.assertIsNone(bay2.module)

    def test_module_installation_creates_port_mappings(self):
        """
        Test that installing a module with front/rear port templates correctly
        creates PortMapping instances for the device.
        """
        device = Device.objects.first()
        manufacturer = Manufacturer.objects.first()
        module_bay = ModuleBay.objects.create(device=device, name='Test Bay PortMapping 1')

        # Create a module type with a rear port template
        module_type_with_mappings = ModuleType.objects.create(
            manufacturer=manufacturer,
            model='Module Type With Mappings',
        )

        # Create a rear port template with 12 positions (splice)
        rear_port_template = RearPortTemplate.objects.create(
            module_type=module_type_with_mappings,
            name='Rear Port 1',
            type=PortTypeChoices.TYPE_SPLICE,
            positions=12,
        )

        # Create 12 front port templates mapped to the rear port
        front_port_templates = []
        for i in range(1, 13):
            front_port_template = FrontPortTemplate.objects.create(
                module_type=module_type_with_mappings,
                name=f'port {i}',
                type=PortTypeChoices.TYPE_LC,
                positions=1,
            )
            front_port_templates.append(front_port_template)

            # Create port template mapping
            PortTemplateMapping.objects.create(
                device_type=None,
                module_type=module_type_with_mappings,
                front_port=front_port_template,
                front_port_position=1,
                rear_port=rear_port_template,
                rear_port_position=i,
            )

        # Install the module
        module = Module.objects.create(
            device=device,
            module_bay=module_bay,
            module_type=module_type_with_mappings,
            status=ModuleStatusChoices.STATUS_ACTIVE,
        )

        # Verify that front ports were created
        front_ports = FrontPort.objects.filter(device=device, module=module)
        self.assertEqual(front_ports.count(), 12)

        # Verify that the rear port was created
        rear_ports = RearPort.objects.filter(device=device, module=module)
        self.assertEqual(rear_ports.count(), 1)
        rear_port = rear_ports.first()
        self.assertEqual(rear_port.positions, 12)

        # Verify that port mappings were created
        port_mappings = PortMapping.objects.filter(front_port__module=module)
        self.assertEqual(port_mappings.count(), 12)

        # Verify each mapping is correct
        for i, front_port_template in enumerate(front_port_templates, start=1):
            front_port = FrontPort.objects.get(
                device=device,
                name=front_port_template.name,
                module=module,
            )

            # Check that a mapping exists for this front port
            mapping = PortMapping.objects.get(
                device=device,
                front_port=front_port,
                front_port_position=1,
            )

            self.assertEqual(mapping.rear_port, rear_port)
            self.assertEqual(mapping.front_port_position, 1)
            self.assertEqual(mapping.rear_port_position, i)

    def test_module_installation_without_mappings(self):
        """
        Test that installing a module without port template mappings
        doesn't create any PortMapping instances.
        """
        device = Device.objects.first()
        manufacturer = Manufacturer.objects.first()
        module_bay = ModuleBay.objects.create(device=device, name='Test Bay PortMapping 2')

        # Create a module type without any port template mappings
        module_type_no_mappings = ModuleType.objects.create(
            manufacturer=manufacturer,
            model='Module Type Without Mappings',
        )

        # Create a rear port template
        RearPortTemplate.objects.create(
            module_type=module_type_no_mappings,
            name='Rear Port 1',
            type=PortTypeChoices.TYPE_SPLICE,
            positions=12,
        )

        # Create front port templates but DO NOT create PortTemplateMapping rows
        for i in range(1, 13):
            FrontPortTemplate.objects.create(
                module_type=module_type_no_mappings,
                name=f'port {i}',
                type=PortTypeChoices.TYPE_LC,
                positions=1,
            )

        # Install the module
        module = Module.objects.create(
            device=device,
            module_bay=module_bay,
            module_type=module_type_no_mappings,
            status=ModuleStatusChoices.STATUS_ACTIVE,
        )

        # Verify no port mappings were created for this module
        port_mappings = PortMapping.objects.filter(
            device=device,
            front_port__module=module,
            front_port_position=1,
        )
        self.assertEqual(port_mappings.count(), 0)
        self.assertEqual(FrontPort.objects.filter(module=module).count(), 12)
        self.assertEqual(RearPort.objects.filter(module=module).count(), 1)
        self.assertEqual(PortMapping.objects.filter(front_port__module=module).count(), 0)

    def test_cannot_install_module_in_disabled_bay(self):
        """
        Test that a Module cannot be installed into a disabled ModuleBay.
        """
        device = Device.objects.first()
        manufacturer = Manufacturer.objects.first()
        module_type = ModuleType.objects.create(manufacturer=manufacturer, model='Test Module Type Disabled')

        # Create a disabled module bay
        disabled_bay = ModuleBay.objects.create(device=device, name='Disabled Bay', enabled=False)

        # Attempt to install a module into the disabled bay
        module = Module(device=device, module_bay=disabled_bay, module_type=module_type)
        with self.assertRaises(ValidationError) as cm:
            module.clean()

        self.assertIn('module_bay', cm.exception.message_dict)
        self.assertIn('disabled module bay', str(cm.exception.message_dict['module_bay']))


class ModuleBayTypeCompatibilityTestCase(TestCase):
    """Tests for bay type compatibility: Module.is_bay_compatible, ModuleType.get_incompatible_modules,
    ModuleBay.is_module_compatible, and Module.clean() validation."""

    @classmethod
    def setUpTestData(cls):
        site = Site.objects.create(name='Compat Site', slug='compat-site')
        manufacturer = Manufacturer.objects.create(name='Compat Mfr', slug='compat-mfr')
        device_type = DeviceType.objects.create(
            manufacturer=manufacturer, model='Compat Device Type', slug='compat-dt'
        )
        device_role = DeviceRole.objects.create(name='Compat Role', slug='compat-role')
        cls.device = Device.objects.create(
            name='Compat Device', device_type=device_type, role=device_role, site=site
        )

        cls.bay_type_a = ModuleBayType.objects.create(
            manufacturer=manufacturer, name='Bay Type A', slug='bay-type-a'
        )
        cls.bay_type_b = ModuleBayType.objects.create(
            manufacturer=manufacturer, name='Bay Type B', slug='bay-type-b'
        )

        cls.module_type_a = ModuleType.objects.create(manufacturer=manufacturer, model='Module Type A')
        cls.module_type_a.module_bay_types.set([cls.bay_type_a])

        cls.module_type_b = ModuleType.objects.create(manufacturer=manufacturer, model='Module Type B')
        cls.module_type_b.module_bay_types.set([cls.bay_type_b])

        cls.module_type_any = ModuleType.objects.create(manufacturer=manufacturer, model='Module Type Any')

    def _make_bay(self, name, *bay_types):
        bay = ModuleBay.objects.create(device=self.device, name=name)
        if bay_types:
            bay.module_bay_types.set(bay_types)
        return bay

    def _install(self, bay, module_type):
        return Module.objects.create(device=self.device, module_bay=bay, module_type=module_type)

    # --- Module.clean() validation ---

    def test_clean_blocks_incompatible_install(self):
        """Module.clean() raises ValidationError when bay and module type have disjoint type sets."""
        bay = self._make_bay('Bay Compat 1', self.bay_type_b)
        module = Module(device=self.device, module_bay=bay, module_type=self.module_type_a)
        with self.assertRaises(ValidationError):
            module.clean()

    def test_clean_allows_compatible_install(self):
        """Module.clean() passes when bay and module type share at least one bay type."""
        bay = self._make_bay('Bay Compat 2', self.bay_type_a)
        module = Module(device=self.device, module_bay=bay, module_type=self.module_type_a)
        module.clean()  # should not raise

    def test_clean_allows_unconstrained_module_type(self):
        """Module.clean() passes when the module type has no bay type constraints."""
        bay = self._make_bay('Bay Compat 3', self.bay_type_a)
        module = Module(device=self.device, module_bay=bay, module_type=self.module_type_any)
        module.clean()  # should not raise

    def test_clean_allows_unconstrained_bay(self):
        """Module.clean() passes when the bay has no bay type constraints."""
        bay = self._make_bay('Bay Compat 4')
        module = Module(device=self.device, module_bay=bay, module_type=self.module_type_a)
        module.clean()  # should not raise

    # --- Module.is_bay_compatible ---

    def test_is_bay_compatible_false_when_disjoint(self):
        """Module.is_bay_compatible returns False when bay and module type sets are disjoint."""
        bay = self._make_bay('Bay Compat 5', self.bay_type_b)
        # Bypass clean() to create an incompatible installation for testing the property
        module = Module.objects.create(device=self.device, module_bay=bay, module_type=self.module_type_a)
        module.refresh_from_db()
        self.assertFalse(module.is_bay_compatible)

    def test_is_bay_compatible_true_when_overlapping(self):
        """Module.is_bay_compatible returns True when bay and module type share a bay type."""
        bay = self._make_bay('Bay Compat 6', self.bay_type_a)
        module = self._install(bay, self.module_type_a)
        self.assertTrue(module.is_bay_compatible)

    def test_is_bay_compatible_true_when_module_type_unconstrained(self):
        """Module.is_bay_compatible returns True when module type has no constraints."""
        bay = self._make_bay('Bay Compat 7', self.bay_type_a)
        module = self._install(bay, self.module_type_any)
        self.assertTrue(module.is_bay_compatible)

    def test_is_bay_compatible_true_when_bay_unconstrained(self):
        """Module.is_bay_compatible returns True when bay has no constraints."""
        bay = self._make_bay('Bay Compat 8')
        module = self._install(bay, self.module_type_a)
        self.assertTrue(module.is_bay_compatible)

    # --- ModuleType.get_incompatible_modules ---

    def test_get_incompatible_modules_returns_incompatible(self):
        """ModuleType.get_incompatible_modules includes modules in bays with disjoint type sets."""
        bay = self._make_bay('Bay Compat 9', self.bay_type_b)
        module = Module.objects.create(device=self.device, module_bay=bay, module_type=self.module_type_a)
        qs = self.module_type_a.get_incompatible_modules()
        self.assertIn(module, qs)

    def test_get_incompatible_modules_excludes_compatible(self):
        """ModuleType.get_incompatible_modules excludes modules in bays with matching type sets."""
        bay = self._make_bay('Bay Compat 10', self.bay_type_a)
        module = self._install(bay, self.module_type_a)
        qs = self.module_type_a.get_incompatible_modules()
        self.assertNotIn(module, qs)

    def test_get_incompatible_modules_excludes_unconstrained_bay(self):
        """ModuleType.get_incompatible_modules excludes modules in unconstrained bays."""
        bay = self._make_bay('Bay Compat 11')
        module = self._install(bay, self.module_type_a)
        qs = self.module_type_a.get_incompatible_modules()
        self.assertNotIn(module, qs)

    def test_get_incompatible_modules_empty_when_type_unconstrained(self):
        """ModuleType.get_incompatible_modules returns empty queryset when type has no constraints."""
        bay = self._make_bay('Bay Compat 12', self.bay_type_a)
        self._install(bay, self.module_type_any)
        qs = self.module_type_any.get_incompatible_modules()
        self.assertFalse(qs.exists())

    # --- ModuleBay.is_module_compatible ---

    def test_bay_is_module_compatible_false_when_disjoint(self):
        """ModuleBay.is_module_compatible returns False when bay and installed module sets are disjoint."""
        bay = self._make_bay('Bay Compat 13', self.bay_type_b)
        Module.objects.create(device=self.device, module_bay=bay, module_type=self.module_type_a)
        bay.refresh_from_db()
        self.assertFalse(bay.is_module_compatible)

    def test_bay_is_module_compatible_true_when_overlapping(self):
        """ModuleBay.is_module_compatible returns True when sets overlap."""
        bay = self._make_bay('Bay Compat 14', self.bay_type_a)
        self._install(bay, self.module_type_a)
        bay.refresh_from_db()
        self.assertTrue(bay.is_module_compatible)

    def test_bay_is_module_compatible_true_when_no_module(self):
        """ModuleBay.is_module_compatible returns True when nothing is installed."""
        bay = self._make_bay('Bay Compat 15', self.bay_type_a)
        self.assertTrue(bay.is_module_compatible)

    def test_bay_is_module_compatible_true_when_bay_unconstrained(self):
        """ModuleBay.is_module_compatible returns True when bay has no constraints."""
        bay = self._make_bay('Bay Compat 16')
        Module.objects.create(device=self.device, module_bay=bay, module_type=self.module_type_a)
        bay.refresh_from_db()
        self.assertTrue(bay.is_module_compatible)


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

    def test_cable_profile_change_preserves_terminations(self):
        """
        When a Cable's profile is changed via save() without explicitly setting terminations (as happens during
        bulk edit), the existing termination points must be preserved.
        """
        cable = Cable.objects.first()
        interface1 = Interface.objects.get(device__name='TestDevice1', name='eth0')
        interface2 = Interface.objects.get(device__name='TestDevice2', name='eth0')

        # Verify initial state: cable has terminations and no profile
        self.assertEqual(cable.profile, '')
        self.assertEqual(CableTermination.objects.filter(cable=cable).count(), 2)

        # Simulate what bulk edit does: load the cable from DB, set profile via setattr, and save.
        # Crucially, do NOT set a_terminations or b_terminations on the instance.
        cable_from_db = Cable.objects.get(pk=cable.pk)
        cable_from_db.profile = CableProfileChoices.SINGLE_1C1P
        cable_from_db.save()

        # Verify terminations are preserved
        self.assertEqual(CableTermination.objects.filter(cable=cable).count(), 2)

        # Verify the correct interfaces are still terminated
        cable_from_db.refresh_from_db()
        a_terms = [ct.termination for ct in CableTermination.objects.filter(cable=cable, cable_end='A')]
        b_terms = [ct.termination for ct in CableTermination.objects.filter(cable=cable, cable_end='B')]
        self.assertEqual(a_terms, [interface1])
        self.assertEqual(b_terms, [interface2])

    @tag('regression')  # #21498
    def test_path_refreshes_replaced_cablepath_reference(self):
        """
        An already-instantiated interface should refresh its denormalized
        `_path` foreign key when the referenced CablePath row has been
        replaced in the database.
        """
        stale_interface = Interface.objects.get(device__name='TestDevice1', name='eth0')
        old_path = CablePath.objects.get(pk=stale_interface._path_id)

        new_path = CablePath(
            path=old_path.path,
            is_active=old_path.is_active,
            is_complete=old_path.is_complete,
            is_split=old_path.is_split,
        )
        old_path_id = old_path.pk
        old_path.delete()
        new_path.save()

        # The old CablePath no longer exists
        self.assertFalse(CablePath.objects.filter(pk=old_path_id).exists())

        # The already-instantiated interface still points to the deleted path
        # until the accessor refreshes `_path` from the database.
        self.assertEqual(stale_interface._path_id, old_path_id)
        self.assertEqual(stale_interface.path.pk, new_path.pk)

    @tag('regression')  # #21498
    def test_serialize_for_event_handles_stale_cablepath_reference_after_retermination(self):
        """
        Serializing an interface whose previously cached `_path` row has been
        deleted during cable retermination must not raise.
        """
        stale_interface = Interface.objects.get(device__name='TestDevice2', name='eth0')
        old_path_id = stale_interface._path_id
        new_peer = Interface.objects.get(device__name='TestDevice2', name='eth1')
        cable = stale_interface.cable

        self.assertIsNotNone(cable)
        self.assertIsNotNone(old_path_id)
        self.assertEqual(stale_interface.cable_end, 'B')

        cable.b_terminations = [new_peer]
        cable.save()

        # The old CablePath was deleted during retrace.
        self.assertFalse(CablePath.objects.filter(pk=old_path_id).exists())

        # The stale in-memory instance still holds the deleted FK value.
        self.assertEqual(stale_interface._path_id, old_path_id)

        # Serialization must not raise ObjectDoesNotExist. Because this interface
        # was the former B-side termination, it is now disconnected.
        data = serialize_for_event(stale_interface)
        self.assertIsNone(data['connected_endpoints'])
        self.assertIsNone(data['connected_endpoints_type'])
        self.assertFalse(data['connected_endpoints_reachable'])

    @tag('regression')  # #21338
    def test_path_refreshes_unset_cablepath_reference(self):
        """
        An endpoint instance saved during cable creation, before path tracing,
        should resolve its path and connected endpoints.

        The stale-instance preconditions rely on Cable.save() saving each
        CableTermination (which re-saves the endpoint) before trace_paths
        creates the CablePath records.
        """
        device = Device.objects.get(name='TestDevice2')
        interface_a = Interface.objects.create(device=device, name='eth2')
        interface_b = Interface.objects.create(device=device, name='eth3')

        # Capture the instances handed to the event machinery on save
        saved_instances = []

        def capture(sender, instance, **kwargs):
            saved_instances.append(instance)

        post_save.connect(capture, sender=Interface)
        try:
            Cable(a_terminations=[interface_a], b_terminations=[interface_b]).save()
        finally:
            post_save.disconnect(capture, sender=Interface)

        self.assertEqual(len(saved_instances), 2)
        captured_a = next(i for i in saved_instances if i.pk == interface_a.pk)
        captured_b = next(i for i in saved_instances if i.pk == interface_b.pk)

        # The captured instances predate path tracing: cabled, but no path yet
        self.assertIsNotNone(captured_a.cable_id)
        self.assertIsNone(captured_a._path_id)
        self.assertIsNone(captured_b._path_id)

        # The accessor must repair the unset denormalized reference
        self.assertIsNotNone(captured_a.path)
        self.assertEqual(captured_a.connected_endpoints, [interface_b])

        # Serialization as performed by the event queue must see the peer
        data = serialize_for_event(captured_b)
        self.assertEqual([endpoint['id'] for endpoint in data['connected_endpoints']], [interface_a.pk])
        self.assertEqual([peer['id'] for peer in data['link_peers']], [interface_a.pk])
        self.assertTrue(data['connected_endpoints_reachable'])

    def test_path_returns_none_for_unsaved_endpoint(self):
        """
        An unsaved endpoint with a link assigned should report no path rather
        than attempting a database refresh.
        """
        device = Device.objects.get(name='TestDevice1')
        cable = Cable.objects.first()
        interface = Interface(device=device, name='tmp', cable=cable)
        self.assertIsNone(interface.path)

    def test_cable_length_normalization_large_kilometer_value(self):
        """
        A large kilometer length must pass validation and fit in the normalized length field.
        """
        cable = Cable.objects.first()
        cable.length = Decimal('1234')
        cable.length_unit = CableLengthUnitChoices.UNIT_KILOMETER
        cable.full_clean()
        cable.save()
        cable.refresh_from_db()

        self.assertEqual(cable._abs_length, Decimal('1234000.0000'))

    def test_cable_length_normalization_maximum_mile_value(self):
        """
        The maximum length value expressed in miles must fit in the normalized length field.
        """
        cable = Cable.objects.first()
        cable.length = Decimal('999999.99')
        cable.length_unit = CableLengthUnitChoices.UNIT_MILE
        cable.full_clean()
        cable.save()
        cable.refresh_from_db()

        self.assertEqual(cable._abs_length, Decimal('1609343983.9066'))


class CableTerminationTestCase(TestCase):

    def test_cache_related_objects_requires_resolvable_termination(self):
        """cache_related_objects raises ValueError when the termination cannot be resolved."""
        cable_termination = CableTermination(
            termination_type=ObjectType.objects.get_for_model(Interface),
            termination_id=0,
        )
        with self.assertRaises(ValueError):
            cable_termination.cache_related_objects()


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


class VCPositionTokenTestCase(TestCase):

    @classmethod
    def setUpTestData(cls):
        Site.objects.create(name='Test Site 1', slug='test-site-1')
        manufacturer = Manufacturer.objects.create(name='Test Manufacturer 1', slug='test-manufacturer-1')
        DeviceType.objects.create(
            manufacturer=manufacturer, model='Test Device Type 1', slug='test-device-type-1'
        )
        ModuleType.objects.create(
            manufacturer=manufacturer, model='Test Module Type 1'
        )
        DeviceRole.objects.create(name='Test Role 1', slug='test-role-1')

    def test_vc_position_token_in_vc(self):
        site = Site.objects.first()
        device_type = DeviceType.objects.first()
        module_type = ModuleType.objects.first()
        device_role = DeviceRole.objects.first()

        InterfaceTemplate.objects.create(
            module_type=module_type,
            name='ge-{vc_position}/{module}/0',
            type='1000base-t',
        )
        vc = VirtualChassis.objects.create(name='Test VC 1')
        device = Device.objects.create(
            name='Device VC 1', device_type=device_type, role=device_role,
            site=site, virtual_chassis=vc, vc_position=8,
        )
        module_bay = ModuleBay.objects.create(device=device, name='Bay 1', position='1')
        Module.objects.create(device=device, module_bay=module_bay, module_type=module_type)

        interface = device.interfaces.get(name='ge-8/1/0')
        self.assertEqual(interface.name, 'ge-8/1/0')

    def test_vc_position_token_not_in_vc_default_fallback(self):
        site = Site.objects.first()
        device_type = DeviceType.objects.first()
        module_type = ModuleType.objects.first()
        device_role = DeviceRole.objects.first()

        InterfaceTemplate.objects.create(
            module_type=module_type,
            name='ge-{vc_position}/{module}/0',
            type='1000base-t',
        )
        device = Device.objects.create(
            name='Device NoVC 1', device_type=device_type, role=device_role,
            site=site,
        )
        module_bay = ModuleBay.objects.create(device=device, name='Bay 1', position='1')
        Module.objects.create(device=device, module_bay=module_bay, module_type=module_type)

        interface = device.interfaces.get(name='ge-0/1/0')
        self.assertEqual(interface.name, 'ge-0/1/0')

    def test_vc_position_token_explicit_fallback(self):
        site = Site.objects.first()
        device_type = DeviceType.objects.first()
        module_type = ModuleType.objects.first()
        device_role = DeviceRole.objects.first()

        InterfaceTemplate.objects.create(
            module_type=module_type,
            name='ge-{vc_position:18}/{module}/0',
            type='1000base-t',
        )
        device = Device.objects.create(
            name='Device NoVC 2', device_type=device_type, role=device_role,
            site=site,
        )
        module_bay = ModuleBay.objects.create(device=device, name='Bay 1', position='1')
        Module.objects.create(device=device, module_bay=module_bay, module_type=module_type)

        interface = device.interfaces.get(name='ge-18/1/0')
        self.assertEqual(interface.name, 'ge-18/1/0')

    def test_vc_position_token_explicit_fallback_ignored_when_in_vc(self):
        site = Site.objects.first()
        device_type = DeviceType.objects.first()
        module_type = ModuleType.objects.first()
        device_role = DeviceRole.objects.first()

        InterfaceTemplate.objects.create(
            module_type=module_type,
            name='ge-{vc_position:99}/{module}/0',
            type='1000base-t',
        )
        vc = VirtualChassis.objects.create(name='Test VC 2')
        device = Device.objects.create(
            name='Device VC 2', device_type=device_type, role=device_role,
            site=site, virtual_chassis=vc, vc_position=2,
        )
        module_bay = ModuleBay.objects.create(device=device, name='Bay 1', position='1')
        Module.objects.create(device=device, module_bay=module_bay, module_type=module_type)

        interface = device.interfaces.get(name='ge-2/1/0')
        self.assertEqual(interface.name, 'ge-2/1/0')

    def test_vc_position_token_device_type_template(self):
        site = Site.objects.first()
        device_type = DeviceType.objects.first()
        device_role = DeviceRole.objects.first()

        InterfaceTemplate.objects.create(
            device_type=device_type,
            name='ge-{vc_position:0}/0/0',
            type='1000base-t',
        )
        vc = VirtualChassis.objects.create(name='Test VC 3')
        device = Device.objects.create(
            name='Device VC 3', device_type=device_type, role=device_role,
            site=site, virtual_chassis=vc, vc_position=3,
        )

        interface = device.interfaces.get(name='ge-3/0/0')
        self.assertEqual(interface.name, 'ge-3/0/0')

    def test_vc_position_token_device_type_template_not_in_vc(self):
        site = Site.objects.first()
        device_type = DeviceType.objects.first()
        device_role = DeviceRole.objects.first()

        InterfaceTemplate.objects.create(
            device_type=device_type,
            name='ge-{vc_position:0}/0/0',
            type='1000base-t',
        )
        device = Device.objects.create(
            name='Device NoVC 3', device_type=device_type, role=device_role,
            site=site,
        )

        interface = device.interfaces.get(name='ge-0/0/0')
        self.assertEqual(interface.name, 'ge-0/0/0')

    def test_vc_position_token_label_resolution(self):
        site = Site.objects.first()
        device_type = DeviceType.objects.first()
        module_type = ModuleType.objects.first()
        device_role = DeviceRole.objects.first()

        InterfaceTemplate.objects.create(
            module_type=module_type,
            name='ge-{vc_position}/{module}/0',
            label='Member {vc_position:0} / Slot {module}',
            type='1000base-t',
        )
        vc = VirtualChassis.objects.create(name='Test VC 4')
        device = Device.objects.create(
            name='Device VC 4', device_type=device_type, role=device_role,
            site=site, virtual_chassis=vc, vc_position=2,
        )
        module_bay = ModuleBay.objects.create(device=device, name='Bay 1', position='1')
        Module.objects.create(device=device, module_bay=module_bay, module_type=module_type)

        interface = device.interfaces.get(name='ge-2/1/0')
        self.assertEqual(interface.label, 'Member 2 / Slot 1')

    @tag('regression')  # Ref: #22707
    def test_vc_position_token_interface_bridge_device_type_template(self):
        site = Site.objects.first()
        device_type = DeviceType.objects.first()
        device_role = DeviceRole.objects.first()

        bridge_template = InterfaceTemplate.objects.create(
            device_type=device_type,
            name='br-{vc_position}',
            type='bridge',
        )
        InterfaceTemplate.objects.create(
            device_type=device_type,
            name='ge-{vc_position}/0/1',
            type='1000base-t',
            bridge=bridge_template,
        )
        vc = VirtualChassis.objects.create(name='Test VC 5')
        device = Device.objects.create(
            name='Device VC 5', device_type=device_type, role=device_role,
            site=site, virtual_chassis=vc, vc_position=5,
        )

        interface = device.interfaces.get(name='ge-5/0/1')
        self.assertEqual(interface.bridge, device.interfaces.get(name='br-5'))

    @tag('regression')  # Ref: #22707
    def test_vc_position_token_port_mapping_device_type_template(self):
        site = Site.objects.first()
        device_type = DeviceType.objects.first()
        device_role = DeviceRole.objects.first()

        rear_port_template = RearPortTemplate.objects.create(
            device_type=device_type,
            name='rp-{vc_position}/1',
            type=PortTypeChoices.TYPE_LC,
            positions=1,
        )
        front_port_template = FrontPortTemplate.objects.create(
            device_type=device_type,
            name='fp-{vc_position}/1',
            type=PortTypeChoices.TYPE_LC,
            positions=1,
        )
        PortTemplateMapping.objects.create(
            device_type=device_type,
            front_port=front_port_template,
            front_port_position=1,
            rear_port=rear_port_template,
            rear_port_position=1,
        )
        vc = VirtualChassis.objects.create(name='Test VC 6')
        device = Device.objects.create(
            name='Device VC 6', device_type=device_type, role=device_role,
            site=site, virtual_chassis=vc, vc_position=6,
        )

        front_port = FrontPort.objects.get(device=device, name='fp-6/1')
        rear_port = RearPort.objects.get(device=device, name='rp-6/1')
        mapping = PortMapping.objects.get(device=device, front_port=front_port)
        self.assertEqual(mapping.rear_port, rear_port)
        self.assertEqual(mapping.front_port_position, 1)
        self.assertEqual(mapping.rear_port_position, 1)


class SiteSignalTestCase(TestCase):

    @tag('regression')
    def test_edit_site_with_prefix_no_vrf(self):
        site = Site.objects.create(name='Test Site', slug='test-site')
        Prefix.objects.create(prefix='192.0.2.0/24', scope=site, vrf=None)

        # Regression test for #21045: should not raise ValueError
        site.save()


class PowerPortDrawTestCase(TestCase):
    """
    Tests for PowerPort.get_power_draw() power aggregation logic.
    """

    @classmethod
    def setUpTestData(cls):
        cls.site = Site.objects.create(name='Test Site', slug='test-site')
        manufacturer = Manufacturer.objects.create(name='Generic', slug='generic')
        device_type = DeviceType.objects.create(manufacturer=manufacturer, model='Test Device Type')
        role = DeviceRole.objects.create(name='Test Role', slug='test-role')
        cls.pdu = Device.objects.create(
            device_type=device_type, role=role, site=cls.site, name='pdu'
        )
        cls.server = Device.objects.create(
            device_type=device_type, role=role, site=cls.site, name='server'
        )

    def test_direct_draw_aggregation(self):
        """
        Sanity check: with one PowerOutlet chained directly to a downstream PSU PowerPort,
        the upstream PowerPort should reflect the PSU's allocated/maximum draw.

            [main] -- [outlet] --C-- [psu]
        """
        main = PowerPort.objects.create(device=self.pdu, name='main')
        outlet = PowerOutlet.objects.create(device=self.pdu, name='outlet', power_port=main)
        psu = PowerPort.objects.create(
            device=self.server, name='psu', allocated_draw=200, maximum_draw=400
        )
        Cable(a_terminations=[outlet], b_terminations=[psu]).save()

        draw = main.get_power_draw()
        self.assertEqual(draw['allocated'], 200)
        self.assertEqual(draw['maximum'], 400)

    @tag('regression')
    def test_recursive_draw_through_intermediate_powerport(self):
        """
        Regression test for #21949: A PDU modeled with internal fuses (intermediate PowerPorts in
        auto mode) should still aggregate downstream PSU draw up to the main PowerPort.

            [main] -- [feedback] --C-- [fuse] -- [outlet] --C-- [psu]

        Both `main` and `fuse` are in auto mode (no allocated_draw/maximum_draw set). The draw
        reported by `psu` must propagate through `fuse` and be reflected at `main`.
        """
        main = PowerPort.objects.create(device=self.pdu, name='main')
        feedback = PowerOutlet.objects.create(device=self.pdu, name='feedback', power_port=main)
        fuse = PowerPort.objects.create(device=self.pdu, name='fuse')
        outlet = PowerOutlet.objects.create(device=self.pdu, name='outlet', power_port=fuse)
        psu = PowerPort.objects.create(
            device=self.server, name='psu', allocated_draw=150, maximum_draw=300
        )
        Cable(a_terminations=[feedback], b_terminations=[fuse]).save()
        Cable(a_terminations=[outlet], b_terminations=[psu]).save()

        fuse_draw = fuse.get_power_draw()
        self.assertEqual(fuse_draw['allocated'], 150)
        self.assertEqual(fuse_draw['maximum'], 300)

        main_draw = main.get_power_draw()
        self.assertEqual(main_draw['allocated'], 150)
        self.assertEqual(main_draw['maximum'], 300)

    def test_intermediate_manual_override_stops_recursion(self):
        """
        When an intermediate PowerPort has an explicit allocated_draw/maximum_draw, recursion should
        stop there and the administratively defined values should be used.
        """
        main = PowerPort.objects.create(device=self.pdu, name='main')
        feedback = PowerOutlet.objects.create(device=self.pdu, name='feedback', power_port=main)
        fuse = PowerPort.objects.create(
            device=self.pdu, name='fuse', allocated_draw=500, maximum_draw=1000
        )
        outlet = PowerOutlet.objects.create(device=self.pdu, name='outlet', power_port=fuse)
        psu = PowerPort.objects.create(
            device=self.server, name='psu', allocated_draw=150, maximum_draw=300
        )
        Cable(a_terminations=[feedback], b_terminations=[fuse]).save()
        Cable(a_terminations=[outlet], b_terminations=[psu]).save()

        main_draw = main.get_power_draw()
        self.assertEqual(main_draw['allocated'], 500)
        self.assertEqual(main_draw['maximum'], 1000)

    def _connect_three_phase_feed(self, powerport):
        """
        Helper: attach `powerport` via cable to a newly-created three-phase PowerFeed.
        """
        power_panel = PowerPanel.objects.create(site=self.site, name='Panel')
        power_feed = PowerFeed.objects.create(
            power_panel=power_panel,
            name='Feed',
            phase=PowerFeedPhaseChoices.PHASE_3PHASE,
        )
        Cable(a_terminations=[powerport], b_terminations=[power_feed]).save()

    @tag('regression')
    def test_three_phase_per_leg_aggregation(self):
        """
        Regression test: per-leg totals for a main PowerPort connected to a three-phase PowerFeed
        must be populated even when the full aggregation runs first. Previously, a shared visited
        set caused downstream ports to be skipped during the per-leg passes, zeroing the legs.

            [main] --C-- [3-phase PowerFeed]
              ├── [outlet_A] (leg A) --C-- [portA] (allocated=100, maximum=200)
              ├── [outlet_B] (leg B) --C-- [portB] (allocated=200, maximum=400)
              └── [outlet_C] (leg C) --C-- [portC] (allocated=300, maximum=600)
        """
        main = PowerPort.objects.create(device=self.pdu, name='main')
        self._connect_three_phase_feed(main)

        leg_specs = [
            (PowerOutletFeedLegChoices.FEED_LEG_A, 100, 200),
            (PowerOutletFeedLegChoices.FEED_LEG_B, 200, 400),
            (PowerOutletFeedLegChoices.FEED_LEG_C, 300, 600),
        ]
        for leg, allocated, maximum in leg_specs:
            outlet = PowerOutlet.objects.create(
                device=self.pdu, name=f'outlet_{leg}', power_port=main, feed_leg=leg
            )
            port = PowerPort.objects.create(
                device=self.server, name=f'psu_{leg}',
                allocated_draw=allocated, maximum_draw=maximum,
            )
            Cable(a_terminations=[outlet], b_terminations=[port]).save()

        # Re-fetch to clear cached_property values populated before cable creation
        main = PowerPort.objects.get(pk=main.pk)
        draw = main.get_power_draw()
        self.assertEqual(draw['allocated'], 600)
        self.assertEqual(draw['maximum'], 1200)
        legs_by_name = {leg['name']: leg for leg in draw['legs']}
        self.assertEqual(legs_by_name['A']['allocated'], 100)
        self.assertEqual(legs_by_name['A']['maximum'], 200)
        self.assertEqual(legs_by_name['B']['allocated'], 200)
        self.assertEqual(legs_by_name['B']['maximum'], 400)
        self.assertEqual(legs_by_name['C']['allocated'], 300)
        self.assertEqual(legs_by_name['C']['maximum'], 600)

    @tag('regression')
    def test_three_phase_per_leg_recursive_aggregation(self):
        """
        Regression test for #21949 on three-phase feeds: per-leg totals must aggregate through
        intermediate auto-mode PowerPorts (the PDU-internal "fuse" pattern).

            [main] --C-- [3-phase PowerFeed]
              └── [feedback_A] (leg A) --C-- [fuse_A] (auto)
                                            └── [outlet_A] (leg A) --C-- [psu_A] (allocated=100)
        """
        main = PowerPort.objects.create(device=self.pdu, name='main')
        self._connect_three_phase_feed(main)

        feedback = PowerOutlet.objects.create(
            device=self.pdu, name='feedback_A', power_port=main,
            feed_leg=PowerOutletFeedLegChoices.FEED_LEG_A,
        )
        fuse = PowerPort.objects.create(device=self.pdu, name='fuse_A')
        outlet = PowerOutlet.objects.create(
            device=self.pdu, name='outlet_A', power_port=fuse,
            feed_leg=PowerOutletFeedLegChoices.FEED_LEG_A,
        )
        psu = PowerPort.objects.create(
            device=self.server, name='psu_A', allocated_draw=100, maximum_draw=200
        )
        Cable(a_terminations=[feedback], b_terminations=[fuse]).save()
        Cable(a_terminations=[outlet], b_terminations=[psu]).save()

        # Re-fetch to clear cached_property values populated before cable creation
        main = PowerPort.objects.get(pk=main.pk)
        draw = main.get_power_draw()
        self.assertEqual(draw['allocated'], 100)
        self.assertEqual(draw['maximum'], 200)
        legs_by_name = {leg['name']: leg for leg in draw['legs']}
        self.assertEqual(legs_by_name['A']['allocated'], 100)
        self.assertEqual(legs_by_name['A']['maximum'], 200)
        self.assertEqual(legs_by_name['B']['allocated'], 0)
        self.assertEqual(legs_by_name['C']['allocated'], 0)


class InventoryItemCycleTestCase(TestCase):
    """
    InventoryItem (ltree-backed, not the nested-group base) must reject assigning
    self or a descendant as parent — behavior django-mptt previously enforced via
    InvalidMove on save().
    """
    @classmethod
    def setUpTestData(cls):
        site = Site.objects.create(name='Site 1', slug='inv-site-1')
        manufacturer = Manufacturer.objects.create(name='Manufacturer 1', slug='inv-mfr-1')
        device_type = DeviceType.objects.create(
            manufacturer=manufacturer, model='Device Type 1', slug='inv-dt-1'
        )
        role = DeviceRole.objects.create(name='Role 1', slug='inv-role-1')
        cls.device = Device.objects.create(
            name='Device 1', device_type=device_type, role=role, site=site
        )

    def test_cannot_assign_descendant_as_parent(self):
        a = InventoryItem.objects.create(device=self.device, name='A')
        b = InventoryItem.objects.create(device=self.device, name='B', parent=a)
        c = InventoryItem.objects.create(device=self.device, name='C', parent=b)
        a.parent = c
        with self.assertRaises(ValidationError):
            a.full_clean()
        # The save()-level guard also rejects the cycle when clean() is bypassed.
        with self.assertRaises(ValidationError):
            a.save()

    def test_cannot_assign_self_as_parent(self):
        a = InventoryItem.objects.create(device=self.device, name='A')
        a.parent = a
        with self.assertRaises(ValidationError):
            a.full_clean()


class InventoryItemTemplateCycleTestCase(TestCase):
    """InventoryItemTemplate must likewise reject self/descendant as parent."""

    @classmethod
    def setUpTestData(cls):
        manufacturer = Manufacturer.objects.create(name='Manufacturer 1', slug='iit-mfr-1')
        cls.device_type = DeviceType.objects.create(
            manufacturer=manufacturer, model='Device Type 1', slug='iit-dt-1'
        )

    def test_cannot_assign_descendant_as_parent(self):
        a = InventoryItemTemplate.objects.create(device_type=self.device_type, name='A')
        b = InventoryItemTemplate.objects.create(device_type=self.device_type, name='B', parent=a)
        a.parent = b
        with self.assertRaises(ValidationError):
            a.full_clean()
        with self.assertRaises(ValidationError):
            a.save()

    def test_cannot_assign_self_as_parent(self):
        a = InventoryItemTemplate.objects.create(device_type=self.device_type, name='A')
        a.parent = a
        with self.assertRaises(ValidationError):
            a.full_clean()


class CoolingComponentTestCase(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.site = Site.objects.create(name='Site 1', slug='site-1')
        cls.manufacturer = Manufacturer.objects.create(name='Manufacturer 1', slug='manufacturer-1')
        cls.role = DeviceRole.objects.create(name='Device Role 1', slug='device-role-1')

    def test_cooling_method_inherited_from_device_type(self):
        """
        A new Device should inherit its cooling_method from the DeviceType when not explicitly set.
        """
        device_type = DeviceType.objects.create(
            manufacturer=self.manufacturer,
            model='Device Type 1',
            slug='device-type-1',
            cooling_method=CoolingMethodChoices.METHOD_LIQUID
        )
        device = Device.objects.create(
            site=self.site,
            device_type=device_type,
            role=self.role,
            name='Device 1'
        )
        self.assertEqual(device.cooling_method, CoolingMethodChoices.METHOD_LIQUID)

    def test_cooling_method_not_overridden_when_set(self):
        """
        A new Device with an explicitly-set cooling_method should not be overridden by the DeviceType.
        """
        device_type = DeviceType.objects.create(
            manufacturer=self.manufacturer,
            model='Device Type 2',
            slug='device-type-2',
            cooling_method=CoolingMethodChoices.METHOD_LIQUID
        )
        device = Device.objects.create(
            site=self.site,
            device_type=device_type,
            role=self.role,
            name='Device 2',
            cooling_method=CoolingMethodChoices.METHOD_AIR
        )
        self.assertEqual(device.cooling_method, CoolingMethodChoices.METHOD_AIR)

    def test_device_creation_instantiates_cooling_components(self):
        """
        Creating a Device from a DeviceType with cooling component templates should auto-instantiate
        matching CoolingIntake and CoolingOutflow components.
        """
        device_type = DeviceType.objects.create(
            manufacturer=self.manufacturer,
            model='Device Type 3',
            slug='device-type-3'
        )

        cooling_intake_template = CoolingIntakeTemplate.objects.create(
            device_type=device_type,
            name='Cooling Port 1',
            type=CoolingConnectorTypeChoices.TYPE_UQD,
            diameter=Decimal('25'),
            diameter_unit=DiameterUnitChoices.UNIT_MILLIMETER,
            maximum_flow=100,
            maximum_flow_unit=FlowRateUnitChoices.UNIT_LITERS_PER_MINUTE
        )
        CoolingOutflowTemplate.objects.create(
            device_type=device_type,
            name='Cooling Outlet 1',
            type=CoolingConnectorTypeChoices.TYPE_UQD,
            diameter=Decimal('25'),
            diameter_unit=DiameterUnitChoices.UNIT_MILLIMETER
        )

        device = Device.objects.create(
            site=self.site,
            device_type=device_type,
            role=self.role,
            name='Device 3'
        )

        cooling_intake = CoolingIntake.objects.get(
            device=device,
            name='Cooling Port 1',
            type=CoolingConnectorTypeChoices.TYPE_UQD,
            diameter=Decimal('25'),
            diameter_unit=DiameterUnitChoices.UNIT_MILLIMETER,
            maximum_flow=100,
            maximum_flow_unit=FlowRateUnitChoices.UNIT_LITERS_PER_MINUTE
        )
        self.assertEqual(cooling_intake_template.maximum_flow, cooling_intake.maximum_flow)

        CoolingOutflow.objects.get(
            device=device,
            name='Cooling Outlet 1',
            type=CoolingConnectorTypeChoices.TYPE_UQD,
            diameter=Decimal('25'),
            diameter_unit=DiameterUnitChoices.UNIT_MILLIMETER
        )

    def test_cooling_outflow_clean_different_device(self):
        """
        CoolingOutflow.clean() should raise a ValidationError when its cooling_intake belongs to a
        different device.
        """
        device_type = DeviceType.objects.create(
            manufacturer=self.manufacturer,
            model='Device Type 4',
            slug='device-type-4'
        )
        device1 = Device.objects.create(
            site=self.site, device_type=device_type, role=self.role, name='Device A'
        )
        device2 = Device.objects.create(
            site=self.site, device_type=device_type, role=self.role, name='Device B'
        )

        cooling_intake = CoolingIntake.objects.create(device=device1, name='Cooling Port 1')
        cooling_outflow = CoolingOutflow(device=device2, name='Cooling Outlet 1', cooling_intake=cooling_intake)

        with self.assertRaises(ValidationError):
            cooling_outflow.full_clean()

    def test_cooling_source_location_site_mismatch(self):
        """
        CoolingSource.clean() should raise a ValidationError when its location belongs to a different site.
        """
        site2 = Site.objects.create(name='Site 2', slug='site-2')
        location = Location.objects.create(name='Location 1', slug='location-1', site=site2)
        cooling_source = CoolingSource(
            site=self.site,
            location=location,
            name='Cooling Source 1',
            type=CoolingSourceTypeChoices.TYPE_CHILLER,
            status=CoolingSourceStatusChoices.STATUS_ACTIVE,
        )
        with self.assertRaises(ValidationError):
            cooling_source.full_clean()

    def test_cooling_feed_rack_site_mismatch(self):
        """
        CoolingFeed.clean() should raise a ValidationError when its rack is in a different site than the
        cooling source.
        """
        site2 = Site.objects.create(name='Site 3', slug='site-3')
        cooling_source = CoolingSource.objects.create(
            site=self.site,
            name='Cooling Source 3',
            type=CoolingSourceTypeChoices.TYPE_CHILLER,
            status=CoolingSourceStatusChoices.STATUS_ACTIVE,
        )
        rack = Rack.objects.create(name='Rack 1', site=site2, status=RackStatusChoices.STATUS_ACTIVE)
        cooling_feed = CoolingFeed(
            cooling_source=cooling_source,
            rack=rack,
            name='Cooling Feed 1',
            status=CoolingFeedStatusChoices.STATUS_ACTIVE,
        )
        with self.assertRaises(ValidationError):
            cooling_feed.full_clean()
