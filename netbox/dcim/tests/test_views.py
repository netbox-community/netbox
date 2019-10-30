import urllib.parse

from django.test import Client, TestCase
from django.urls import reverse

from dcim.constants import *
from dcim.models import (
    Cable, ConsolePortTemplate, ConsoleServerPortTemplate, Device, DeviceBayTemplate, DeviceRole, DeviceType,
    FrontPortTemplate, Interface, InterfaceTemplate, InventoryItem, Manufacturer, Platform, PowerPortTemplate,
    PowerOutletTemplate, Rack, RackGroup, RackReservation, RackRole, RearPortTemplate, Site, Region, VirtualChassis,
)
from utilities.testing import create_test_user


class RegionTestCase(TestCase):

    def setUp(self):
        user = create_test_user(permissions=['dcim.view_region'])
        self.client = Client()
        self.client.force_login(user)

        # Create three Regions
        for i in range(1, 4):
            Region(name='Region {}'.format(i), slug='region-{}'.format(i)).save()

    def test_region_list(self):

        url = reverse('dcim:region_list')

        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)


class SiteTestCase(TestCase):

    def setUp(self):
        user = create_test_user(permissions=['dcim.view_site'])
        self.client = Client()
        self.client.force_login(user)

        region = Region(name='Region 1', slug='region-1')
        region.save()

        Site.objects.bulk_create([
            Site(name='Site 1', slug='site-1', region=region),
            Site(name='Site 2', slug='site-2', region=region),
            Site(name='Site 3', slug='site-3', region=region),
        ])

    def test_site_list(self):

        url = reverse('dcim:site_list')
        params = {
            "region": Region.objects.first().slug,
        }

        response = self.client.get('{}?{}'.format(url, urllib.parse.urlencode(params)))
        self.assertEqual(response.status_code, 200)

    def test_site(self):

        site = Site.objects.first()
        response = self.client.get(site.get_absolute_url())
        self.assertEqual(response.status_code, 200)


class RackGroupTestCase(TestCase):

    def setUp(self):
        user = create_test_user(permissions=['dcim.view_rackgroup'])
        self.client = Client()
        self.client.force_login(user)

        site = Site(name='Site 1', slug='site-1')
        site.save()

        RackGroup.objects.bulk_create([
            RackGroup(name='Rack Group 1', slug='rack-group-1', site=site),
            RackGroup(name='Rack Group 2', slug='rack-group-2', site=site),
            RackGroup(name='Rack Group 3', slug='rack-group-3', site=site),
        ])

    def test_rackgroup_list(self):

        url = reverse('dcim:rackgroup_list')

        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)


class RackRoleTestCase(TestCase):

    def setUp(self):
        user = create_test_user(permissions=['dcim.view_rackrole'])
        self.client = Client()
        self.client.force_login(user)

        RackRole.objects.bulk_create([
            RackRole(name='Rack Role 1', slug='rack-role-1'),
            RackRole(name='Rack Role 2', slug='rack-role-2'),
            RackRole(name='Rack Role 3', slug='rack-role-3'),
        ])

    def test_rackrole_list(self):

        url = reverse('dcim:rackrole_list')

        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)


class RackReservationTestCase(TestCase):

    def setUp(self):
        user = create_test_user(permissions=['dcim.view_rackreservation'])
        self.client = Client()
        self.client.force_login(user)

        site = Site(name='Site 1', slug='site-1')
        site.save()

        rack = Rack(name='Rack 1', site=site)
        rack.save()

        RackReservation.objects.bulk_create([
            RackReservation(rack=rack, user=user, units=[1, 2, 3], description='Reservation 1'),
            RackReservation(rack=rack, user=user, units=[4, 5, 6], description='Reservation 2'),
            RackReservation(rack=rack, user=user, units=[7, 8, 9], description='Reservation 3'),
        ])

    def test_rackreservation_list(self):

        url = reverse('dcim:rackreservation_list')

        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)


class RackTestCase(TestCase):

    def setUp(self):
        user = create_test_user(permissions=['dcim.view_rack'])
        self.client = Client()
        self.client.force_login(user)

        site = Site(name='Site 1', slug='site-1')
        site.save()

        Rack.objects.bulk_create([
            Rack(name='Rack 1', site=site),
            Rack(name='Rack 2', site=site),
            Rack(name='Rack 3', site=site),
        ])

    def test_rack_list(self):

        url = reverse('dcim:rack_list')
        params = {
            "site": Site.objects.first().slug,
        }

        response = self.client.get('{}?{}'.format(url, urllib.parse.urlencode(params)))
        self.assertEqual(response.status_code, 200)

    def test_rack(self):

        rack = Rack.objects.first()
        response = self.client.get(rack.get_absolute_url())
        self.assertEqual(response.status_code, 200)


class ManufacturerTypeTestCase(TestCase):

    def setUp(self):
        user = create_test_user(permissions=['dcim.view_manufacturer'])
        self.client = Client()
        self.client.force_login(user)

        Manufacturer.objects.bulk_create([
            Manufacturer(name='Manufacturer 1', slug='manufacturer-1'),
            Manufacturer(name='Manufacturer 2', slug='manufacturer-2'),
            Manufacturer(name='Manufacturer 3', slug='manufacturer-3'),
        ])

    def test_manufacturer_list(self):

        url = reverse('dcim:manufacturer_list')

        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)


class DeviceTypeTestCase(TestCase):

    def setUp(self):
        user = create_test_user(permissions=['dcim.view_devicetype'])
        self.client = Client()
        self.client.force_login(user)

        manufacturer = Manufacturer(name='Manufacturer 1', slug='manufacturer-1')
        manufacturer.save()

        DeviceType.objects.bulk_create([
            DeviceType(model='Device Type 1', slug='device-type-1', manufacturer=manufacturer),
            DeviceType(model='Device Type 2', slug='device-type-2', manufacturer=manufacturer),
            DeviceType(model='Device Type 3', slug='device-type-3', manufacturer=manufacturer),
        ])

    def test_devicetype_list(self):

        url = reverse('dcim:devicetype_list')
        params = {
            "manufacturer": Manufacturer.objects.first().slug,
        }

        response = self.client.get('{}?{}'.format(url, urllib.parse.urlencode(params)))
        self.assertEqual(response.status_code, 200)

    def test_devicetype(self):

        devicetype = DeviceType.objects.first()
        response = self.client.get(devicetype.get_absolute_url())
        self.assertEqual(response.status_code, 200)

    def test_devicetype_import(self):

        IMPORT_DATA = """
manufacturer: Generic
model: TEST-1000
slug: test-1000
u_height: 2
console-ports:
  - name: Console Port 1
    type: de-9
  - name: Console Port 2
    type: de-9
  - name: Console Port 3
    type: de-9
console-server-ports:
  - name: Console Server Port 1
    type: rj-45
  - name: Console Server Port 2
    type: rj-45
  - name: Console Server Port 3
    type: rj-45
power-ports:
  - name: Power Port 1
  - name: Power Port 2
  - name: Power Port 3
power-outlets:
  - name: Power Outlet 1
    power_port: Power Port 1
    feed_leg: 1
  - name: Power Outlet 2
    power_port: Power Port 1
    feed_leg: 1
  - name: Power Outlet 3
    power_port: Power Port 1
    feed_leg: 1
interfaces:
  - name: Interface 1
    type: 1000base-t
    mgmt_only: true
  - name: Interface 2
    type: 1000base-t
  - name: Interface 3
    type: 1000base-t
rear-ports:
  - name: Rear Port 1
    type: 8p8c
  - name: Rear Port 2
    type: 8p8c
  - name: Rear Port 3
    type: 8p8c
front-ports:
  - name: Front Port 1
    type: 8p8c
    rear_port: Rear Port 1
  - name: Front Port 2
    type: 8p8c
    rear_port: Rear Port 2
  - name: Front Port 3
    type: 8p8c
    rear_port: Rear Port 3
device-bays:
  - name: Device Bay 1
  - name: Device Bay 2
  - name: Device Bay 3
"""

        # Create the manufacturer
        Manufacturer(name='Generic', slug='generic').save()

        # Authenticate as user with necessary permissions
        user = create_test_user(username='testuser2', permissions=[
            'dcim.view_devicetype',
            'dcim.add_devicetype',
            'dcim.add_consoleporttemplate',
            'dcim.add_consoleserverporttemplate',
            'dcim.add_powerporttemplate',
            'dcim.add_poweroutlettemplate',
            'dcim.add_interfacetemplate',
            'dcim.add_frontporttemplate',
            'dcim.add_rearporttemplate',
            'dcim.add_devicebaytemplate',
        ])
        self.client.force_login(user)

        form_data = {
            'data': IMPORT_DATA,
            'format': 'yaml'
        }
        response = self.client.post(reverse('dcim:devicetype_import'), data=form_data, follow=True)
        self.assertEqual(response.status_code, 200)

        dt = DeviceType.objects.get(model='TEST-1000')

        # Verify all of the components were created
        self.assertEqual(dt.consoleport_templates.count(), 3)
        cp1 = ConsolePortTemplate.objects.first()
        self.assertEqual(cp1.name, 'Console Port 1')
        self.assertEqual(cp1.type, CONSOLE_TYPE_DE9)

        self.assertEqual(dt.consoleserverport_templates.count(), 3)
        csp1 = ConsoleServerPortTemplate.objects.first()
        self.assertEqual(csp1.name, 'Console Server Port 1')
        self.assertEqual(csp1.type, CONSOLE_TYPE_RJ45)

        self.assertEqual(dt.powerport_templates.count(), 3)
        pp1 = PowerPortTemplate.objects.first()
        self.assertEqual(pp1.name, 'Power Port 1')

        self.assertEqual(dt.poweroutlet_templates.count(), 3)
        po1 = PowerOutletTemplate.objects.first()
        self.assertEqual(po1.name, 'Power Outlet 1')
        self.assertEqual(po1.power_port, pp1)
        self.assertEqual(po1.feed_leg, POWERFEED_LEG_A)

        self.assertEqual(dt.interface_templates.count(), 3)
        iface1 = InterfaceTemplate.objects.first()
        self.assertEqual(iface1.name, 'Interface 1')
        self.assertEqual(iface1.type, IFACE_TYPE_1GE_FIXED)
        self.assertTrue(iface1.mgmt_only)

        self.assertEqual(dt.rearport_templates.count(), 3)
        rp1 = RearPortTemplate.objects.first()
        self.assertEqual(rp1.name, 'Rear Port 1')

        self.assertEqual(dt.frontport_templates.count(), 3)
        fp1 = FrontPortTemplate.objects.first()
        self.assertEqual(fp1.name, 'Front Port 1')
        self.assertEqual(fp1.rear_port, rp1)
        self.assertEqual(fp1.rear_port_position, 1)

        self.assertEqual(dt.device_bay_templates.count(), 3)
        db1 = DeviceBayTemplate.objects.first()
        self.assertEqual(db1.name, 'Device Bay 1')


class DeviceRoleTestCase(TestCase):

    def setUp(self):
        user = create_test_user(permissions=['dcim.view_devicerole'])
        self.client = Client()
        self.client.force_login(user)

        DeviceRole.objects.bulk_create([
            DeviceRole(name='Device Role 1', slug='device-role-1'),
            DeviceRole(name='Device Role 2', slug='device-role-2'),
            DeviceRole(name='Device Role 3', slug='device-role-3'),
        ])

    def test_devicerole_list(self):

        url = reverse('dcim:devicerole_list')

        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)


class PlatformTestCase(TestCase):

    def setUp(self):
        user = create_test_user(permissions=['dcim.view_platform'])
        self.client = Client()
        self.client.force_login(user)

        Platform.objects.bulk_create([
            Platform(name='Platform 1', slug='platform-1'),
            Platform(name='Platform 2', slug='platform-2'),
            Platform(name='Platform 3', slug='platform-3'),
        ])

    def test_platform_list(self):

        url = reverse('dcim:platform_list')

        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)


class DeviceTestCase(TestCase):

    def setUp(self):
        user = create_test_user(permissions=['dcim.view_device'])
        self.client = Client()
        self.client.force_login(user)

        site = Site(name='Site 1', slug='site-1')
        site.save()

        manufacturer = Manufacturer(name='Manufacturer 1', slug='manufacturer-1')
        manufacturer.save()

        devicetype = DeviceType(model='Device Type 1', manufacturer=manufacturer)
        devicetype.save()

        devicerole = DeviceRole(name='Device Role 1', slug='device-role-1')
        devicerole.save()

        Device.objects.bulk_create([
            Device(name='Device 1', site=site, device_type=devicetype, device_role=devicerole),
            Device(name='Device 2', site=site, device_type=devicetype, device_role=devicerole),
            Device(name='Device 3', site=site, device_type=devicetype, device_role=devicerole),
        ])

    def test_device_list(self):

        url = reverse('dcim:device_list')
        params = {
            "device_type_id": DeviceType.objects.first().pk,
            "role": DeviceRole.objects.first().slug,
        }

        response = self.client.get('{}?{}'.format(url, urllib.parse.urlencode(params)))
        self.assertEqual(response.status_code, 200)

    def test_device(self):

        device = Device.objects.first()
        response = self.client.get(device.get_absolute_url())
        self.assertEqual(response.status_code, 200)


class InventoryItemTestCase(TestCase):

    def setUp(self):
        user = create_test_user(permissions=['dcim.view_inventoryitem'])
        self.client = Client()
        self.client.force_login(user)

        site = Site(name='Site 1', slug='site-1')
        site.save()

        manufacturer = Manufacturer(name='Manufacturer 1', slug='manufacturer-1')
        manufacturer.save()

        devicetype = DeviceType(model='Device Type 1', manufacturer=manufacturer)
        devicetype.save()

        devicerole = DeviceRole(name='Device Role 1', slug='device-role-1')
        devicerole.save()

        device = Device(name='Device 1', site=site, device_type=devicetype, device_role=devicerole)
        device.save()

        InventoryItem.objects.bulk_create([
            InventoryItem(device=device, name='Inventory Item 1'),
            InventoryItem(device=device, name='Inventory Item 2'),
            InventoryItem(device=device, name='Inventory Item 3'),
        ])

    def test_inventoryitem_list(self):

        url = reverse('dcim:inventoryitem_list')
        params = {
            "device_id": Device.objects.first().pk,
        }

        response = self.client.get('{}?{}'.format(url, urllib.parse.urlencode(params)))
        self.assertEqual(response.status_code, 200)


class CableTestCase(TestCase):

    def setUp(self):
        user = create_test_user(permissions=['dcim.view_cable'])
        self.client = Client()
        self.client.force_login(user)

        site = Site(name='Site 1', slug='site-1')
        site.save()

        manufacturer = Manufacturer(name='Manufacturer 1', slug='manufacturer-1')
        manufacturer.save()

        devicetype = DeviceType(model='Device Type 1', manufacturer=manufacturer)
        devicetype.save()

        devicerole = DeviceRole(name='Device Role 1', slug='device-role-1')
        devicerole.save()

        device1 = Device(name='Device 1', site=site, device_type=devicetype, device_role=devicerole)
        device1.save()
        device2 = Device(name='Device 2', site=site, device_type=devicetype, device_role=devicerole)
        device2.save()

        iface1 = Interface(device=device1, name='Interface 1', type=IFACE_TYPE_1GE_FIXED)
        iface1.save()
        iface2 = Interface(device=device1, name='Interface 2', type=IFACE_TYPE_1GE_FIXED)
        iface2.save()
        iface3 = Interface(device=device1, name='Interface 3', type=IFACE_TYPE_1GE_FIXED)
        iface3.save()
        iface4 = Interface(device=device2, name='Interface 1', type=IFACE_TYPE_1GE_FIXED)
        iface4.save()
        iface5 = Interface(device=device2, name='Interface 2', type=IFACE_TYPE_1GE_FIXED)
        iface5.save()
        iface6 = Interface(device=device2, name='Interface 3', type=IFACE_TYPE_1GE_FIXED)
        iface6.save()

        Cable(termination_a=iface1, termination_b=iface4, type=CABLE_TYPE_CAT6).save()
        Cable(termination_a=iface2, termination_b=iface5, type=CABLE_TYPE_CAT6).save()
        Cable(termination_a=iface3, termination_b=iface6, type=CABLE_TYPE_CAT6).save()

    def test_cable_list(self):

        url = reverse('dcim:cable_list')
        params = {
            "type": CABLE_TYPE_CAT6,
        }

        response = self.client.get('{}?{}'.format(url, urllib.parse.urlencode(params)))
        self.assertEqual(response.status_code, 200)

    def test_cable(self):

        cable = Cable.objects.first()
        response = self.client.get(cable.get_absolute_url())
        self.assertEqual(response.status_code, 200)


class VirtualChassisTestCase(TestCase):

    def setUp(self):
        user = create_test_user(permissions=['dcim.view_virtualchassis'])
        self.client = Client()
        self.client.force_login(user)

        site = Site.objects.create(name='Site 1', slug='site-1')
        manufacturer = Manufacturer.objects.create(name='Manufacturer', slug='manufacturer-1')
        device_type = DeviceType.objects.create(
            manufacturer=manufacturer, model='Device Type 1', slug='device-type-1'
        )
        device_role = DeviceRole.objects.create(
            name='Device Role', slug='device-role-1'
        )

        # Create 9 member Devices
        device1 = Device.objects.create(
            device_type=device_type, device_role=device_role, name='Device 1', site=site
        )
        device2 = Device.objects.create(
            device_type=device_type, device_role=device_role, name='Device 2', site=site
        )
        device3 = Device.objects.create(
            device_type=device_type, device_role=device_role, name='Device 3', site=site
        )
        device4 = Device.objects.create(
            device_type=device_type, device_role=device_role, name='Device 4', site=site
        )
        device5 = Device.objects.create(
            device_type=device_type, device_role=device_role, name='Device 5', site=site
        )
        device6 = Device.objects.create(
            device_type=device_type, device_role=device_role, name='Device 6', site=site
        )

        # Create three VirtualChassis with two members each
        vc1 = VirtualChassis.objects.create(master=device1, domain='test-domain-1')
        Device.objects.filter(pk=device2.pk).update(virtual_chassis=vc1, vc_position=2)
        vc2 = VirtualChassis.objects.create(master=device3, domain='test-domain-2')
        Device.objects.filter(pk=device4.pk).update(virtual_chassis=vc2, vc_position=2)
        vc3 = VirtualChassis.objects.create(master=device5, domain='test-domain-3')
        Device.objects.filter(pk=device6.pk).update(virtual_chassis=vc3, vc_position=2)

    def test_virtualchassis_list(self):

        url = reverse('dcim:virtualchassis_list')

        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
