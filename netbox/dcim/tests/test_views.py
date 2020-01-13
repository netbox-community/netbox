import urllib.parse

import yaml
from django.test import Client, TestCase
from django.urls import reverse

from dcim.choices import *
from dcim.constants import *
from dcim.models import *
from utilities.testing import create_test_user


class RegionTestCase(TestCase):

    def setUp(self):
        user = create_test_user(
            permissions=[
                'dcim.view_region',
                'dcim.add_region',
            ]
        )
        self.client = Client()
        self.client.force_login(user)

        # Create three Regions
        for i in range(1, 4):
            Region(name='Region {}'.format(i), slug='region-{}'.format(i)).save()

    def test_region_list(self):

        url = reverse('dcim:region_list')

        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_region_import(self):

        csv_data = (
            "name,slug",
            "Region 4,region-4",
            "Region 5,region-5",
            "Region 6,region-6",
        )

        response = self.client.post(reverse('dcim:region_import'), {'csv': '\n'.join(csv_data)})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Region.objects.count(), 6)


class SiteTestCase(TestCase):

    def setUp(self):
        user = create_test_user(
            permissions=[
                'dcim.view_site',
                'dcim.add_site',
            ]
        )
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

    def test_site_import(self):

        csv_data = (
            "name,slug",
            "Site 4,site-4",
            "Site 5,site-5",
            "Site 6,site-6",
        )

        response = self.client.post(reverse('dcim:site_import'), {'csv': '\n'.join(csv_data)})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Site.objects.count(), 6)


class RackGroupTestCase(TestCase):

    def setUp(self):
        user = create_test_user(
            permissions=[
                'dcim.view_rackgroup',
                'dcim.add_rackgroup',
            ]
        )
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

    def test_rackgroup_import(self):

        csv_data = (
            "site,name,slug",
            "Site 1,Rack Group 4,rack-group-4",
            "Site 1,Rack Group 5,rack-group-5",
            "Site 1,Rack Group 6,rack-group-6",
        )

        response = self.client.post(reverse('dcim:rackgroup_import'), {'csv': '\n'.join(csv_data)})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(RackGroup.objects.count(), 6)


class RackRoleTestCase(TestCase):

    def setUp(self):
        user = create_test_user(
            permissions=[
                'dcim.view_rackrole',
                'dcim.add_rackrole',
            ]
        )
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

    def test_rackrole_import(self):

        csv_data = (
            "name,slug,color",
            "Rack Role 4,rack-role-4,ff0000",
            "Rack Role 5,rack-role-5,00ff00",
            "Rack Role 6,rack-role-6,0000ff",
        )

        response = self.client.post(reverse('dcim:rackrole_import'), {'csv': '\n'.join(csv_data)})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(RackRole.objects.count(), 6)


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
        user = create_test_user(
            permissions=[
                'dcim.view_rack',
                'dcim.add_rack',
            ]
        )
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

    def test_rack_import(self):

        csv_data = (
            "site,name,width,u_height",
            "Site 1,Rack 4,19,42",
            "Site 1,Rack 5,19,42",
            "Site 1,Rack 6,19,42",
        )

        response = self.client.post(reverse('dcim:rack_import'), {'csv': '\n'.join(csv_data)})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Rack.objects.count(), 6)


class ManufacturerTypeTestCase(TestCase):

    def setUp(self):
        user = create_test_user(
            permissions=[
                'dcim.view_manufacturer',
                'dcim.add_manufacturer',
            ]
        )
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

    def test_manufacturer_import(self):

        csv_data = (
            "name,slug",
            "Manufacturer 4,manufacturer-4",
            "Manufacturer 5,manufacturer-5",
            "Manufacturer 6,manufacturer-6",
        )

        response = self.client.post(reverse('dcim:manufacturer_import'), {'csv': '\n'.join(csv_data)})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Manufacturer.objects.count(), 6)


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

    def test_devicetype_export(self):

        url = reverse('dcim:devicetype_list')

        response = self.client.get('{}?export'.format(url))
        self.assertEqual(response.status_code, 200)
        data = list(yaml.load_all(response.content, Loader=yaml.SafeLoader))
        self.assertEqual(len(data), 3)
        self.assertEqual(data[0]['manufacturer'], 'Manufacturer 1')
        self.assertEqual(data[0]['model'], 'Device Type 1')

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
    type: iec-60320-c14
  - name: Power Port 2
    type: iec-60320-c14
  - name: Power Port 3
    type: iec-60320-c14
power-outlets:
  - name: Power Outlet 1
    type: iec-60320-c13
    power_port: Power Port 1
    feed_leg: A
  - name: Power Outlet 2
    type: iec-60320-c13
    power_port: Power Port 1
    feed_leg: A
  - name: Power Outlet 3
    type: iec-60320-c13
    power_port: Power Port 1
    feed_leg: A
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
        self.assertEqual(cp1.type, ConsolePortTypeChoices.TYPE_DE9)

        self.assertEqual(dt.consoleserverport_templates.count(), 3)
        csp1 = ConsoleServerPortTemplate.objects.first()
        self.assertEqual(csp1.name, 'Console Server Port 1')
        self.assertEqual(csp1.type, ConsolePortTypeChoices.TYPE_RJ45)

        self.assertEqual(dt.powerport_templates.count(), 3)
        pp1 = PowerPortTemplate.objects.first()
        self.assertEqual(pp1.name, 'Power Port 1')
        self.assertEqual(pp1.type, PowerPortTypeChoices.TYPE_IEC_C14)

        self.assertEqual(dt.poweroutlet_templates.count(), 3)
        po1 = PowerOutletTemplate.objects.first()
        self.assertEqual(po1.name, 'Power Outlet 1')
        self.assertEqual(po1.type, PowerOutletTypeChoices.TYPE_IEC_C13)
        self.assertEqual(po1.power_port, pp1)
        self.assertEqual(po1.feed_leg, PowerOutletFeedLegChoices.FEED_LEG_A)

        self.assertEqual(dt.interface_templates.count(), 3)
        iface1 = InterfaceTemplate.objects.first()
        self.assertEqual(iface1.name, 'Interface 1')
        self.assertEqual(iface1.type, InterfaceTypeChoices.TYPE_1GE_FIXED)
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
        user = create_test_user(
            permissions=[
                'dcim.view_devicerole',
                'dcim.add_devicerole',
            ]
        )
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

    def test_devicerole_import(self):

        csv_data = (
            "name,slug,color",
            "Device Role 4,device-role-4,ff0000",
            "Device Role 5,device-role-5,00ff00",
            "Device Role 6,device-role-6,0000ff",
        )

        response = self.client.post(reverse('dcim:devicerole_import'), {'csv': '\n'.join(csv_data)})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(DeviceRole.objects.count(), 6)


class PlatformTestCase(TestCase):

    def setUp(self):
        user = create_test_user(
            permissions=[
                'dcim.view_platform',
                'dcim.add_platform',
            ]
        )
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

    def test_platform_import(self):

        csv_data = (
            "name,slug",
            "Platform 4,platform-4",
            "Platform 5,platform-5",
            "Platform 6,platform-6",
        )

        response = self.client.post(reverse('dcim:platform_import'), {'csv': '\n'.join(csv_data)})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Platform.objects.count(), 6)


class DeviceTestCase(TestCase):

    def setUp(self):
        user = create_test_user(
            permissions=[
                'dcim.view_device',
                'dcim.add_device',
            ]
        )
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

    def test_device_import(self):

        csv_data = (
            "device_role,manufacturer,model_name,status,site,name",
            "Device Role 1,Manufacturer 1,Device Type 1,Active,Site 1,Device 4",
            "Device Role 1,Manufacturer 1,Device Type 1,Active,Site 1,Device 5",
            "Device Role 1,Manufacturer 1,Device Type 1,Active,Site 1,Device 6",
        )

        response = self.client.post(reverse('dcim:device_import'), {'csv': '\n'.join(csv_data)})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Device.objects.count(), 6)


class ConsolePortTestCase(TestCase):

    def setUp(self):
        user = create_test_user(
            permissions=[
                'dcim.view_consoleport',
                'dcim.add_consoleport',
            ]
        )
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

        ConsolePort.objects.bulk_create([
            ConsolePort(device=device, name='Console Port 1'),
            ConsolePort(device=device, name='Console Port 2'),
            ConsolePort(device=device, name='Console Port 3'),
        ])

    def test_consoleport_list(self):

        url = reverse('dcim:consoleport_list')

        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_consoleport_import(self):

        csv_data = (
            "device,name",
            "Device 1,Console Port 4",
            "Device 1,Console Port 5",
            "Device 1,Console Port 6",
        )

        response = self.client.post(reverse('dcim:consoleport_import'), {'csv': '\n'.join(csv_data)})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(ConsolePort.objects.count(), 6)


class ConsoleServerPortTestCase(TestCase):

    def setUp(self):
        user = create_test_user(
            permissions=[
                'dcim.view_consoleserverport',
                'dcim.add_consoleserverport',
            ]
        )
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

        ConsoleServerPort.objects.bulk_create([
            ConsoleServerPort(device=device, name='Console Server Port 1'),
            ConsoleServerPort(device=device, name='Console Server Port 2'),
            ConsoleServerPort(device=device, name='Console Server Port 3'),
        ])

    def test_consoleserverport_list(self):

        url = reverse('dcim:consoleserverport_list')

        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_consoleserverport_import(self):

        csv_data = (
            "device,name",
            "Device 1,Console Server Port 4",
            "Device 1,Console Server Port 5",
            "Device 1,Console Server Port 6",
        )

        response = self.client.post(reverse('dcim:consoleserverport_import'), {'csv': '\n'.join(csv_data)})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(ConsoleServerPort.objects.count(), 6)


class PowerPortTestCase(TestCase):

    def setUp(self):
        user = create_test_user(
            permissions=[
                'dcim.view_powerport',
                'dcim.add_powerport',
            ]
        )
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

        PowerPort.objects.bulk_create([
            PowerPort(device=device, name='Power Port 1'),
            PowerPort(device=device, name='Power Port 2'),
            PowerPort(device=device, name='Power Port 3'),
        ])

    def test_powerport_list(self):

        url = reverse('dcim:powerport_list')

        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_powerport_import(self):

        csv_data = (
            "device,name",
            "Device 1,Power Port 4",
            "Device 1,Power Port 5",
            "Device 1,Power Port 6",
        )

        response = self.client.post(reverse('dcim:powerport_import'), {'csv': '\n'.join(csv_data)})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(PowerPort.objects.count(), 6)


class PowerOutletTestCase(TestCase):

    def setUp(self):
        user = create_test_user(
            permissions=[
                'dcim.view_poweroutlet',
                'dcim.add_poweroutlet',
            ]
        )
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

        PowerOutlet.objects.bulk_create([
            PowerOutlet(device=device, name='Power Outlet 1'),
            PowerOutlet(device=device, name='Power Outlet 2'),
            PowerOutlet(device=device, name='Power Outlet 3'),
        ])

    def test_poweroutlet_list(self):

        url = reverse('dcim:poweroutlet_list')

        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_poweroutlet_import(self):

        csv_data = (
            "device,name",
            "Device 1,Power Outlet 4",
            "Device 1,Power Outlet 5",
            "Device 1,Power Outlet 6",
        )

        response = self.client.post(reverse('dcim:poweroutlet_import'), {'csv': '\n'.join(csv_data)})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(PowerOutlet.objects.count(), 6)


class InterfaceTestCase(TestCase):

    def setUp(self):
        user = create_test_user(
            permissions=[
                'dcim.view_interface',
                'dcim.add_interface',
            ]
        )
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

        Interface.objects.bulk_create([
            Interface(device=device, name='Interface 1'),
            Interface(device=device, name='Interface 2'),
            Interface(device=device, name='Interface 3'),
        ])

    def test_interface_list(self):

        url = reverse('dcim:interface_list')

        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_interface_import(self):

        csv_data = (
            "device,name,type",
            "Device 1,Interface 4,1000BASE-T (1GE)",
            "Device 1,Interface 5,1000BASE-T (1GE)",
            "Device 1,Interface 6,1000BASE-T (1GE)",
        )

        response = self.client.post(reverse('dcim:interface_import'), {'csv': '\n'.join(csv_data)})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Interface.objects.count(), 6)


class FrontPortTestCase(TestCase):

    def setUp(self):
        user = create_test_user(
            permissions=[
                'dcim.view_frontport',
                'dcim.add_frontport',
            ]
        )
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

        rearport1 = RearPort(device=device, name='Rear Port 1')
        rearport1.save()
        rearport2 = RearPort(device=device, name='Rear Port 2')
        rearport2.save()
        rearport3 = RearPort(device=device, name='Rear Port 3')
        rearport3.save()

        # RearPorts for CSV import test
        RearPort(device=device, name='Rear Port 4').save()
        RearPort(device=device, name='Rear Port 5').save()
        RearPort(device=device, name='Rear Port 6').save()

        FrontPort.objects.bulk_create([
            FrontPort(device=device, name='Front Port 1', rear_port=rearport1),
            FrontPort(device=device, name='Front Port 2', rear_port=rearport2),
            FrontPort(device=device, name='Front Port 3', rear_port=rearport3),
        ])

    def test_frontport_list(self):

        url = reverse('dcim:frontport_list')

        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_frontport_import(self):

        csv_data = (
            "device,name,type,rear_port,rear_port_position",
            "Device 1,Front Port 4,8P8C,Rear Port 4,1",
            "Device 1,Front Port 5,8P8C,Rear Port 5,1",
            "Device 1,Front Port 6,8P8C,Rear Port 6,1",
        )

        response = self.client.post(reverse('dcim:frontport_import'), {'csv': '\n'.join(csv_data)})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(FrontPort.objects.count(), 6)


class RearPortTestCase(TestCase):

    def setUp(self):
        user = create_test_user(
            permissions=[
                'dcim.view_rearport',
                'dcim.add_rearport',
            ]
        )
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

        RearPort.objects.bulk_create([
            RearPort(device=device, name='Rear Port 1'),
            RearPort(device=device, name='Rear Port 2'),
            RearPort(device=device, name='Rear Port 3'),
        ])

    def test_rearport_list(self):

        url = reverse('dcim:rearport_list')

        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_rearport_import(self):

        csv_data = (
            "device,name,type,positions",
            "Device 1,Rear Port 4,8P8C,1",
            "Device 1,Rear Port 5,8P8C,1",
            "Device 1,Rear Port 6,8P8C,1",
        )

        response = self.client.post(reverse('dcim:rearport_import'), {'csv': '\n'.join(csv_data)})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(RearPort.objects.count(), 6)


class DeviceBayTestCase(TestCase):

    def setUp(self):
        user = create_test_user(
            permissions=[
                'dcim.view_devicebay',
                'dcim.add_devicebay',
            ]
        )
        self.client = Client()
        self.client.force_login(user)

        site = Site(name='Site 1', slug='site-1')
        site.save()

        manufacturer = Manufacturer(name='Manufacturer 1', slug='manufacturer-1')
        manufacturer.save()

        devicetype = DeviceType(
            model='Device Type 1',
            manufacturer=manufacturer,
            subdevice_role=SubdeviceRoleChoices.ROLE_PARENT
        )
        devicetype.save()

        devicerole = DeviceRole(name='Device Role 1', slug='device-role-1')
        devicerole.save()

        device = Device(name='Device 1', site=site, device_type=devicetype, device_role=devicerole)
        device.save()

        DeviceBay.objects.bulk_create([
            DeviceBay(device=device, name='Device Bay 1'),
            DeviceBay(device=device, name='Device Bay 2'),
            DeviceBay(device=device, name='Device Bay 3'),
        ])

    def test_devicebay_list(self):

        url = reverse('dcim:devicebay_list')

        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_devicebay_import(self):

        csv_data = (
            "device,name",
            "Device 1,Device Bay 4",
            "Device 1,Device Bay 5",
            "Device 1,Device Bay 6",
        )

        response = self.client.post(reverse('dcim:devicebay_import'), {'csv': '\n'.join(csv_data)})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(DeviceBay.objects.count(), 6)


class InventoryItemTestCase(TestCase):

    def setUp(self):
        user = create_test_user(
            permissions=[
                'dcim.view_inventoryitem',
                'dcim.add_inventoryitem',
            ]
        )
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

    def test_inventoryitem_import(self):

        csv_data = (
            "device,name",
            "Device 1,Inventory Item 4",
            "Device 1,Inventory Item 5",
            "Device 1,Inventory Item 6",
        )

        response = self.client.post(reverse('dcim:inventoryitem_import'), {'csv': '\n'.join(csv_data)})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(InventoryItem.objects.count(), 6)


class CableTestCase(TestCase):

    def setUp(self):
        user = create_test_user(
            permissions=[
                'dcim.view_cable',
                'dcim.add_cable',
            ]
        )
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
        device3 = Device(name='Device 3', site=site, device_type=devicetype, device_role=devicerole)
        device3.save()
        device4 = Device(name='Device 4', site=site, device_type=devicetype, device_role=devicerole)
        device4.save()

        iface1 = Interface(device=device1, name='Interface 1', type=InterfaceTypeChoices.TYPE_1GE_FIXED)
        iface1.save()
        iface2 = Interface(device=device1, name='Interface 2', type=InterfaceTypeChoices.TYPE_1GE_FIXED)
        iface2.save()
        iface3 = Interface(device=device1, name='Interface 3', type=InterfaceTypeChoices.TYPE_1GE_FIXED)
        iface3.save()
        iface4 = Interface(device=device2, name='Interface 1', type=InterfaceTypeChoices.TYPE_1GE_FIXED)
        iface4.save()
        iface5 = Interface(device=device2, name='Interface 2', type=InterfaceTypeChoices.TYPE_1GE_FIXED)
        iface5.save()
        iface6 = Interface(device=device2, name='Interface 3', type=InterfaceTypeChoices.TYPE_1GE_FIXED)
        iface6.save()

        # Interfaces for CSV import testing
        Interface(device=device3, name='Interface 1', type=InterfaceTypeChoices.TYPE_1GE_FIXED).save()
        Interface(device=device3, name='Interface 2', type=InterfaceTypeChoices.TYPE_1GE_FIXED).save()
        Interface(device=device3, name='Interface 3', type=InterfaceTypeChoices.TYPE_1GE_FIXED).save()
        Interface(device=device4, name='Interface 1', type=InterfaceTypeChoices.TYPE_1GE_FIXED).save()
        Interface(device=device4, name='Interface 2', type=InterfaceTypeChoices.TYPE_1GE_FIXED).save()
        Interface(device=device4, name='Interface 3', type=InterfaceTypeChoices.TYPE_1GE_FIXED).save()

        Cable(termination_a=iface1, termination_b=iface4, type=CableTypeChoices.TYPE_CAT6).save()
        Cable(termination_a=iface2, termination_b=iface5, type=CableTypeChoices.TYPE_CAT6).save()
        Cable(termination_a=iface3, termination_b=iface6, type=CableTypeChoices.TYPE_CAT6).save()

    def test_cable_list(self):

        url = reverse('dcim:cable_list')
        params = {
            "type": CableTypeChoices.TYPE_CAT6,
        }

        response = self.client.get('{}?{}'.format(url, urllib.parse.urlencode(params)))
        self.assertEqual(response.status_code, 200)

    def test_cable(self):

        cable = Cable.objects.first()
        response = self.client.get(cable.get_absolute_url())
        self.assertEqual(response.status_code, 200)

    def test_cable_import(self):

        csv_data = (
            "side_a_device,side_a_type,side_a_name,side_b_device,side_b_type,side_b_name",
            "Device 3,interface,Interface 1,Device 4,interface,Interface 1",
            "Device 3,interface,Interface 2,Device 4,interface,Interface 2",
            "Device 3,interface,Interface 3,Device 4,interface,Interface 3",
        )

        response = self.client.post(reverse('dcim:cable_import'), {'csv': '\n'.join(csv_data)})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Cable.objects.count(), 6)


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
