from decimal import Decimal

import pytz
import yaml
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.urls import reverse
from netaddr import EUI

from dcim.choices import *
from dcim.constants import *
from dcim.models import *
from ipam.models import VLAN
from utilities.testing import ViewTestCases


def create_test_device(name):
    """
    Convenience method for creating a Device (e.g. for component testing).
    """
    site, _ = Site.objects.get_or_create(name='Site 1', slug='site-1')
    manufacturer, _ = Manufacturer.objects.get_or_create(name='Manufacturer 1', slug='manufacturer-1')
    devicetype, _ = DeviceType.objects.get_or_create(model='Device Type 1', manufacturer=manufacturer)
    devicerole, _ = DeviceRole.objects.get_or_create(name='Device Role 1', slug='device-role-1')
    device = Device.objects.create(name=name, site=site, device_type=devicetype, device_role=devicerole)

    return device


class RegionTestCase(ViewTestCases.OrganizationalObjectViewTestCase):
    model = Region

    @classmethod
    def setUpTestData(cls):

        # Create three Regions
        regions = (
            Region(name='Region 1', slug='region-1'),
            Region(name='Region 2', slug='region-2'),
            Region(name='Region 3', slug='region-3'),
        )
        for region in regions:
            region.save()

        cls.form_data = {
            'name': 'Region X',
            'slug': 'region-x',
            'parent': regions[2].pk,
        }

        cls.csv_data = (
            "name,slug",
            "Region 4,region-4",
            "Region 5,region-5",
            "Region 6,region-6",
        )


class SiteTestCase(ViewTestCases.PrimaryObjectViewTestCase):
    model = Site

    @classmethod
    def setUpTestData(cls):

        regions = (
            Region(name='Region 1', slug='region-1'),
            Region(name='Region 2', slug='region-2'),
        )
        for region in regions:
            region.save()

        Site.objects.bulk_create([
            Site(name='Site 1', slug='site-1', region=regions[0]),
            Site(name='Site 2', slug='site-2', region=regions[0]),
            Site(name='Site 3', slug='site-3', region=regions[0]),
        ])

        cls.form_data = {
            'name': 'Site X',
            'slug': 'site-x',
            'status': SiteStatusChoices.STATUS_PLANNED,
            'region': regions[1].pk,
            'tenant': None,
            'facility': 'Facility X',
            'asn': 65001,
            'time_zone': pytz.UTC,
            'description': 'Site description',
            'physical_address': '742 Evergreen Terrace, Springfield, USA',
            'shipping_address': '742 Evergreen Terrace, Springfield, USA',
            'latitude': Decimal('35.780000'),
            'longitude': Decimal('-78.642000'),
            'contact_name': 'Hank Hill',
            'contact_phone': '123-555-9999',
            'contact_email': 'hank@stricklandpropane.com',
            'comments': 'Test site',
            'tags': 'Alpha,Bravo,Charlie',
        }

        cls.csv_data = (
            "name,slug",
            "Site 4,site-4",
            "Site 5,site-5",
            "Site 6,site-6",
        )

        cls.bulk_edit_data = {
            'status': SiteStatusChoices.STATUS_PLANNED,
            'region': regions[1].pk,
            'tenant': None,
            'asn': 65009,
            'time_zone': pytz.timezone('US/Eastern'),
            'description': 'New description',
        }


class RackGroupTestCase(ViewTestCases.OrganizationalObjectViewTestCase):
    model = RackGroup

    @classmethod
    def setUpTestData(cls):

        site = Site(name='Site 1', slug='site-1')
        site.save()

        RackGroup.objects.bulk_create([
            RackGroup(name='Rack Group 1', slug='rack-group-1', site=site),
            RackGroup(name='Rack Group 2', slug='rack-group-2', site=site),
            RackGroup(name='Rack Group 3', slug='rack-group-3', site=site),
        ])

        cls.form_data = {
            'name': 'Rack Group X',
            'slug': 'rack-group-x',
            'site': site.pk,
        }

        cls.csv_data = (
            "site,name,slug",
            "Site 1,Rack Group 4,rack-group-4",
            "Site 1,Rack Group 5,rack-group-5",
            "Site 1,Rack Group 6,rack-group-6",
        )


class RackRoleTestCase(ViewTestCases.OrganizationalObjectViewTestCase):
    model = RackRole

    @classmethod
    def setUpTestData(cls):

        RackRole.objects.bulk_create([
            RackRole(name='Rack Role 1', slug='rack-role-1'),
            RackRole(name='Rack Role 2', slug='rack-role-2'),
            RackRole(name='Rack Role 3', slug='rack-role-3'),
        ])

        cls.form_data = {
            'name': 'Rack Role X',
            'slug': 'rack-role-x',
            'color': 'c0c0c0',
            'description': 'New role',
        }

        cls.csv_data = (
            "name,slug,color",
            "Rack Role 4,rack-role-4,ff0000",
            "Rack Role 5,rack-role-5,00ff00",
            "Rack Role 6,rack-role-6,0000ff",
        )


class RackReservationTestCase(ViewTestCases.PrimaryObjectViewTestCase):
    model = RackReservation

    # Disable inapplicable tests
    test_get_object = None
    test_create_object = None

    # TODO: Fix URL name for view
    test_import_objects = None

    @classmethod
    def setUpTestData(cls):

        user2 = User.objects.create_user(username='testuser2')
        user3 = User.objects.create_user(username='testuser3')

        site = Site.objects.create(name='Site 1', slug='site-1')

        rack = Rack(name='Rack 1', site=site)
        rack.save()

        RackReservation.objects.bulk_create([
            RackReservation(rack=rack, user=user2, units=[1, 2, 3], description='Reservation 1'),
            RackReservation(rack=rack, user=user2, units=[4, 5, 6], description='Reservation 2'),
            RackReservation(rack=rack, user=user2, units=[7, 8, 9], description='Reservation 3'),
        ])

        cls.form_data = {
            'rack': rack.pk,
            'units': [10, 11, 12],
            'user': user3.pk,
            'tenant': None,
            'description': 'Rack reservation',
        }

        cls.bulk_edit_data = {
            'user': user3.pk,
            'tenant': None,
            'description': 'New description',
        }


class RackTestCase(ViewTestCases.PrimaryObjectViewTestCase):
    model = Rack

    @classmethod
    def setUpTestData(cls):

        sites = (
            Site(name='Site 1', slug='site-1'),
            Site(name='Site 2', slug='site-2'),
        )
        Site.objects.bulk_create(sites)

        rackgroups = (
            RackGroup(name='Rack Group 1', slug='rack-group-1', site=sites[0]),
            RackGroup(name='Rack Group 2', slug='rack-group-2', site=sites[1])
        )
        RackGroup.objects.bulk_create(rackgroups)

        rackroles = (
            RackRole(name='Rack Role 1', slug='rack-role-1'),
            RackRole(name='Rack Role 2', slug='rack-role-2'),
        )
        RackRole.objects.bulk_create(rackroles)

        Rack.objects.bulk_create((
            Rack(name='Rack 1', site=sites[0]),
            Rack(name='Rack 2', site=sites[0]),
            Rack(name='Rack 3', site=sites[0]),
        ))

        cls.form_data = {
            'name': 'Rack X',
            'facility_id': 'Facility X',
            'site': sites[1].pk,
            'group': rackgroups[1].pk,
            'tenant': None,
            'status': RackStatusChoices.STATUS_PLANNED,
            'role': rackroles[1].pk,
            'serial': '123456',
            'asset_tag': 'ABCDEF',
            'type': RackTypeChoices.TYPE_CABINET,
            'width': RackWidthChoices.WIDTH_19IN,
            'u_height': 48,
            'desc_units': False,
            'outer_width': 500,
            'outer_depth': 500,
            'outer_unit': RackDimensionUnitChoices.UNIT_MILLIMETER,
            'comments': 'Some comments',
            'tags': 'Alpha,Bravo,Charlie',
        }

        cls.csv_data = (
            "site,name,width,u_height",
            "Site 1,Rack 4,19,42",
            "Site 1,Rack 5,19,42",
            "Site 1,Rack 6,19,42",
        )

        cls.bulk_edit_data = {
            'site': sites[1].pk,
            'group': rackgroups[1].pk,
            'tenant': None,
            'status': RackStatusChoices.STATUS_DEPRECATED,
            'role': rackroles[1].pk,
            'serial': '654321',
            'type': RackTypeChoices.TYPE_4POST,
            'width': RackWidthChoices.WIDTH_23IN,
            'u_height': 49,
            'desc_units': True,
            'outer_width': 30,
            'outer_depth': 30,
            'outer_unit': RackDimensionUnitChoices.UNIT_INCH,
            'comments': 'New comments',
        }


class ManufacturerTestCase(ViewTestCases.OrganizationalObjectViewTestCase):
    model = Manufacturer

    @classmethod
    def setUpTestData(cls):

        Manufacturer.objects.bulk_create([
            Manufacturer(name='Manufacturer 1', slug='manufacturer-1'),
            Manufacturer(name='Manufacturer 2', slug='manufacturer-2'),
            Manufacturer(name='Manufacturer 3', slug='manufacturer-3'),
        ])

        cls.form_data = {
            'name': 'Manufacturer X',
            'slug': 'manufacturer-x',
        }

        cls.csv_data = (
            "name,slug",
            "Manufacturer 4,manufacturer-4",
            "Manufacturer 5,manufacturer-5",
            "Manufacturer 6,manufacturer-6",
        )


class DeviceTypeTestCase(ViewTestCases.PrimaryObjectViewTestCase):
    model = DeviceType

    @classmethod
    def setUpTestData(cls):

        manufacturers = (
            Manufacturer(name='Manufacturer 1', slug='manufacturer-1'),
            Manufacturer(name='Manufacturer 2', slug='manufacturer-2')
        )
        Manufacturer.objects.bulk_create(manufacturers)

        DeviceType.objects.bulk_create([
            DeviceType(model='Device Type 1', slug='device-type-1', manufacturer=manufacturers[0]),
            DeviceType(model='Device Type 2', slug='device-type-2', manufacturer=manufacturers[0]),
            DeviceType(model='Device Type 3', slug='device-type-3', manufacturer=manufacturers[0]),
        ])

        cls.form_data = {
            'manufacturer': manufacturers[1].pk,
            'model': 'Device Type X',
            'slug': 'device-type-x',
            'part_number': '123ABC',
            'u_height': 2,
            'is_full_depth': True,
            'subdevice_role': '',  # CharField
            'comments': 'Some comments',
            'tags': 'Alpha,Bravo,Charlie',
        }

        cls.bulk_edit_data = {
            'manufacturer': manufacturers[1].pk,
            'u_height': 3,
            'is_full_depth': False,
        }

    def test_import_objects(self):
        """
        Custom import test for YAML-based imports (versus CSV)
        """
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

        # Add all required permissions to the test user
        self.add_permissions(
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
        )

        form_data = {
            'data': IMPORT_DATA,
            'format': 'yaml'
        }
        response = self.client.post(reverse('dcim:devicetype_import'), data=form_data, follow=True)
        self.assertHttpStatus(response, 200)

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

    def test_devicetype_export(self):

        url = reverse('dcim:devicetype_list')
        self.add_permissions('dcim.view_devicetype')

        response = self.client.get('{}?export'.format(url))
        self.assertEqual(response.status_code, 200)
        data = list(yaml.load_all(response.content, Loader=yaml.SafeLoader))
        self.assertEqual(len(data), 3)
        self.assertEqual(data[0]['manufacturer'], 'Manufacturer 1')
        self.assertEqual(data[0]['model'], 'Device Type 1')


#
# DeviceType components
#

class ConsolePortTemplateTestCase(ViewTestCases.DeviceComponentTemplateViewTestCase):
    model = ConsolePortTemplate

    @classmethod
    def setUpTestData(cls):
        manufacturer = Manufacturer.objects.create(name='Manufacturer 1', slug='manufacturer-1')
        devicetypes = (
            DeviceType(manufacturer=manufacturer, model='Device Type 1', slug='device-type-1'),
            DeviceType(manufacturer=manufacturer, model='Device Type 2', slug='device-type-2'),
        )
        DeviceType.objects.bulk_create(devicetypes)

        ConsolePortTemplate.objects.bulk_create((
            ConsolePortTemplate(device_type=devicetypes[0], name='Console Port Template 1'),
            ConsolePortTemplate(device_type=devicetypes[0], name='Console Port Template 2'),
            ConsolePortTemplate(device_type=devicetypes[0], name='Console Port Template 3'),
        ))

        cls.form_data = {
            'device_type': devicetypes[1].pk,
            'name': 'Console Port Template X',
            'type': ConsolePortTypeChoices.TYPE_RJ45,
        }

        cls.bulk_create_data = {
            'device_type': devicetypes[1].pk,
            'name_pattern': 'Console Port Template [4-6]',
            'type': ConsolePortTypeChoices.TYPE_RJ45,
        }

        cls.bulk_edit_data = {
            'type': ConsolePortTypeChoices.TYPE_RJ45,
        }


class ConsoleServerPortTemplateTestCase(ViewTestCases.DeviceComponentTemplateViewTestCase):
    model = ConsoleServerPortTemplate

    @classmethod
    def setUpTestData(cls):
        manufacturer = Manufacturer.objects.create(name='Manufacturer 1', slug='manufacturer-1')
        devicetypes = (
            DeviceType(manufacturer=manufacturer, model='Device Type 1', slug='device-type-1'),
            DeviceType(manufacturer=manufacturer, model='Device Type 2', slug='device-type-2'),
        )
        DeviceType.objects.bulk_create(devicetypes)

        ConsoleServerPortTemplate.objects.bulk_create((
            ConsoleServerPortTemplate(device_type=devicetypes[0], name='Console Server Port Template 1'),
            ConsoleServerPortTemplate(device_type=devicetypes[0], name='Console Server Port Template 2'),
            ConsoleServerPortTemplate(device_type=devicetypes[0], name='Console Server Port Template 3'),
        ))

        cls.form_data = {
            'device_type': devicetypes[1].pk,
            'name': 'Console Server Port Template X',
            'type': ConsolePortTypeChoices.TYPE_RJ45,
        }

        cls.bulk_create_data = {
            'device_type': devicetypes[1].pk,
            'name_pattern': 'Console Server Port Template [4-6]',
            'type': ConsolePortTypeChoices.TYPE_RJ45,
        }

        cls.bulk_edit_data = {
            'type': ConsolePortTypeChoices.TYPE_RJ45,
        }


class PowerPortTemplateTestCase(ViewTestCases.DeviceComponentTemplateViewTestCase):
    model = PowerPortTemplate

    @classmethod
    def setUpTestData(cls):
        manufacturer = Manufacturer.objects.create(name='Manufacturer 1', slug='manufacturer-1')
        devicetypes = (
            DeviceType(manufacturer=manufacturer, model='Device Type 1', slug='device-type-1'),
            DeviceType(manufacturer=manufacturer, model='Device Type 2', slug='device-type-2'),
        )
        DeviceType.objects.bulk_create(devicetypes)

        PowerPortTemplate.objects.bulk_create((
            PowerPortTemplate(device_type=devicetypes[0], name='Power Port Template 1'),
            PowerPortTemplate(device_type=devicetypes[0], name='Power Port Template 2'),
            PowerPortTemplate(device_type=devicetypes[0], name='Power Port Template 3'),
        ))

        cls.form_data = {
            'device_type': devicetypes[1].pk,
            'name': 'Power Port Template X',
            'type': PowerPortTypeChoices.TYPE_IEC_C14,
            'maximum_draw': 100,
            'allocated_draw': 50,
        }

        cls.bulk_create_data = {
            'device_type': devicetypes[1].pk,
            'name_pattern': 'Power Port Template [4-6]',
            'type': PowerPortTypeChoices.TYPE_IEC_C14,
            'maximum_draw': 100,
            'allocated_draw': 50,
        }

        cls.bulk_edit_data = {
            'type': PowerPortTypeChoices.TYPE_IEC_C14,
            'maximum_draw': 100,
            'allocated_draw': 50,
        }


class PowerOutletTemplateTestCase(ViewTestCases.DeviceComponentTemplateViewTestCase):
    model = PowerOutletTemplate

    @classmethod
    def setUpTestData(cls):
        manufacturer = Manufacturer.objects.create(name='Manufacturer 1', slug='manufacturer-1')
        devicetype = DeviceType.objects.create(manufacturer=manufacturer, model='Device Type 1', slug='device-type-1')

        PowerOutletTemplate.objects.bulk_create((
            PowerOutletTemplate(device_type=devicetype, name='Power Outlet Template 1'),
            PowerOutletTemplate(device_type=devicetype, name='Power Outlet Template 2'),
            PowerOutletTemplate(device_type=devicetype, name='Power Outlet Template 3'),
        ))

        powerports = (
            PowerPortTemplate(device_type=devicetype, name='Power Port Template 1'),
        )
        PowerPortTemplate.objects.bulk_create(powerports)

        cls.form_data = {
            'device_type': devicetype.pk,
            'name': 'Power Outlet Template X',
            'type': PowerOutletTypeChoices.TYPE_IEC_C13,
            'power_port': powerports[0].pk,
            'feed_leg': PowerOutletFeedLegChoices.FEED_LEG_B,
        }

        cls.bulk_create_data = {
            'device_type': devicetype.pk,
            'name_pattern': 'Power Outlet Template [4-6]',
            'type': PowerOutletTypeChoices.TYPE_IEC_C13,
            'power_port': powerports[0].pk,
            'feed_leg': PowerOutletFeedLegChoices.FEED_LEG_B,
        }

        cls.bulk_edit_data = {
            'type': PowerOutletTypeChoices.TYPE_IEC_C13,
            'feed_leg': PowerOutletFeedLegChoices.FEED_LEG_B,
        }


class InterfaceTemplateTestCase(ViewTestCases.DeviceComponentTemplateViewTestCase):
    model = InterfaceTemplate

    @classmethod
    def setUpTestData(cls):
        manufacturer = Manufacturer.objects.create(name='Manufacturer 1', slug='manufacturer-1')
        devicetypes = (
            DeviceType(manufacturer=manufacturer, model='Device Type 1', slug='device-type-1'),
            DeviceType(manufacturer=manufacturer, model='Device Type 2', slug='device-type-2'),
        )
        DeviceType.objects.bulk_create(devicetypes)

        InterfaceTemplate.objects.bulk_create((
            InterfaceTemplate(device_type=devicetypes[0], name='Interface Template 1'),
            InterfaceTemplate(device_type=devicetypes[0], name='Interface Template 2'),
            InterfaceTemplate(device_type=devicetypes[0], name='Interface Template 3'),
        ))

        cls.form_data = {
            'device_type': devicetypes[1].pk,
            'name': 'Interface Template X',
            'type': InterfaceTypeChoices.TYPE_1GE_GBIC,
            'mgmt_only': True,
        }

        cls.bulk_create_data = {
            'device_type': devicetypes[1].pk,
            'name_pattern': 'Interface Template [4-6]',
            'type': InterfaceTypeChoices.TYPE_1GE_GBIC,
            'mgmt_only': True,
        }

        cls.bulk_edit_data = {
            'type': InterfaceTypeChoices.TYPE_1GE_GBIC,
            'mgmt_only': True,
        }


class FrontPortTemplateTestCase(ViewTestCases.DeviceComponentTemplateViewTestCase):
    model = FrontPortTemplate

    @classmethod
    def setUpTestData(cls):
        manufacturer = Manufacturer.objects.create(name='Manufacturer 1', slug='manufacturer-1')
        devicetype = DeviceType.objects.create(manufacturer=manufacturer, model='Device Type 1', slug='device-type-1')

        rearports = (
            RearPortTemplate(device_type=devicetype, name='Rear Port Template 1'),
            RearPortTemplate(device_type=devicetype, name='Rear Port Template 2'),
            RearPortTemplate(device_type=devicetype, name='Rear Port Template 3'),
            RearPortTemplate(device_type=devicetype, name='Rear Port Template 4'),
            RearPortTemplate(device_type=devicetype, name='Rear Port Template 5'),
            RearPortTemplate(device_type=devicetype, name='Rear Port Template 6'),
        )
        RearPortTemplate.objects.bulk_create(rearports)

        FrontPortTemplate.objects.bulk_create((
            FrontPortTemplate(device_type=devicetype, name='Front Port Template 1', rear_port=rearports[0], rear_port_position=1),
            FrontPortTemplate(device_type=devicetype, name='Front Port Template 2', rear_port=rearports[1], rear_port_position=1),
            FrontPortTemplate(device_type=devicetype, name='Front Port Template 3', rear_port=rearports[2], rear_port_position=1),
        ))

        cls.form_data = {
            'device_type': devicetype.pk,
            'name': 'Front Port X',
            'type': PortTypeChoices.TYPE_8P8C,
            'rear_port': rearports[3].pk,
            'rear_port_position': 1,
        }

        cls.bulk_create_data = {
            'device_type': devicetype.pk,
            'name_pattern': 'Front Port [4-6]',
            'type': PortTypeChoices.TYPE_8P8C,
            'rear_port_set': [
                '{}:1'.format(rp.pk) for rp in rearports[3:6]
            ],
        }

        cls.bulk_edit_data = {
            'type': PortTypeChoices.TYPE_8P8C,
        }


class RearPortTemplateTestCase(ViewTestCases.DeviceComponentTemplateViewTestCase):
    model = RearPortTemplate

    @classmethod
    def setUpTestData(cls):
        manufacturer = Manufacturer.objects.create(name='Manufacturer 1', slug='manufacturer-1')
        devicetypes = (
            DeviceType(manufacturer=manufacturer, model='Device Type 1', slug='device-type-1'),
            DeviceType(manufacturer=manufacturer, model='Device Type 2', slug='device-type-2'),
        )
        DeviceType.objects.bulk_create(devicetypes)

        RearPortTemplate.objects.bulk_create((
            RearPortTemplate(device_type=devicetypes[0], name='Rear Port Template 1'),
            RearPortTemplate(device_type=devicetypes[0], name='Rear Port Template 2'),
            RearPortTemplate(device_type=devicetypes[0], name='Rear Port Template 3'),
        ))

        cls.form_data = {
            'device_type': devicetypes[1].pk,
            'name': 'Rear Port Template X',
            'type': PortTypeChoices.TYPE_8P8C,
            'positions': 2,
        }

        cls.bulk_create_data = {
            'device_type': devicetypes[1].pk,
            'name_pattern': 'Rear Port Template [4-6]',
            'type': PortTypeChoices.TYPE_8P8C,
            'positions': 2,
        }

        cls.bulk_edit_data = {
            'type': PortTypeChoices.TYPE_8P8C,
        }


class DeviceBayTemplateTestCase(ViewTestCases.DeviceComponentTemplateViewTestCase):
    model = DeviceBayTemplate

    # Disable inapplicable views
    test_bulk_edit_objects = None

    @classmethod
    def setUpTestData(cls):
        manufacturer = Manufacturer.objects.create(name='Manufacturer 1', slug='manufacturer-1')
        devicetypes = (
            DeviceType(manufacturer=manufacturer, model='Device Type 1', slug='device-type-1'),
            DeviceType(manufacturer=manufacturer, model='Device Type 2', slug='device-type-2'),
        )
        DeviceType.objects.bulk_create(devicetypes)

        DeviceBayTemplate.objects.bulk_create((
            DeviceBayTemplate(device_type=devicetypes[0], name='Device Bay Template 1'),
            DeviceBayTemplate(device_type=devicetypes[0], name='Device Bay Template 2'),
            DeviceBayTemplate(device_type=devicetypes[0], name='Device Bay Template 3'),
        ))

        cls.form_data = {
            'device_type': devicetypes[1].pk,
            'name': 'Device Bay Template X',
        }

        cls.bulk_create_data = {
            'device_type': devicetypes[1].pk,
            'name_pattern': 'Device Bay Template [4-6]',
        }


class DeviceRoleTestCase(ViewTestCases.OrganizationalObjectViewTestCase):
    model = DeviceRole

    @classmethod
    def setUpTestData(cls):

        DeviceRole.objects.bulk_create([
            DeviceRole(name='Device Role 1', slug='device-role-1'),
            DeviceRole(name='Device Role 2', slug='device-role-2'),
            DeviceRole(name='Device Role 3', slug='device-role-3'),
        ])

        cls.form_data = {
            'name': 'Devie Role X',
            'slug': 'device-role-x',
            'color': 'c0c0c0',
            'vm_role': False,
            'description': 'New device role',
        }

        cls.csv_data = (
            "name,slug,color",
            "Device Role 4,device-role-4,ff0000",
            "Device Role 5,device-role-5,00ff00",
            "Device Role 6,device-role-6,0000ff",
        )


class PlatformTestCase(ViewTestCases.OrganizationalObjectViewTestCase):
    model = Platform

    @classmethod
    def setUpTestData(cls):

        manufacturer = Manufacturer.objects.create(name='Manufacturer 1', slug='manufacturer-1')

        Platform.objects.bulk_create([
            Platform(name='Platform 1', slug='platform-1', manufacturer=manufacturer),
            Platform(name='Platform 2', slug='platform-2', manufacturer=manufacturer),
            Platform(name='Platform 3', slug='platform-3', manufacturer=manufacturer),
        ])

        cls.form_data = {
            'name': 'Platform X',
            'slug': 'platform-x',
            'manufacturer': manufacturer.pk,
            'napalm_driver': 'junos',
            'napalm_args': None,
        }

        cls.csv_data = (
            "name,slug",
            "Platform 4,platform-4",
            "Platform 5,platform-5",
            "Platform 6,platform-6",
        )


class DeviceTestCase(ViewTestCases.PrimaryObjectViewTestCase):
    model = Device

    @classmethod
    def setUpTestData(cls):

        sites = (
            Site(name='Site 1', slug='site-1'),
            Site(name='Site 2', slug='site-2'),
        )
        Site.objects.bulk_create(sites)

        racks = (
            Rack(name='Rack 1', site=sites[0]),
            Rack(name='Rack 2', site=sites[1]),
        )
        Rack.objects.bulk_create(racks)

        manufacturer = Manufacturer.objects.create(name='Manufacturer 1', slug='manufacturer-1')

        devicetypes = (
            DeviceType(model='Device Type 1', slug='device-type-1', manufacturer=manufacturer),
            DeviceType(model='Device Type 2', slug='device-type-2', manufacturer=manufacturer),
        )
        DeviceType.objects.bulk_create(devicetypes)

        deviceroles = (
            DeviceRole(name='Device Role 1', slug='device-role-1'),
            DeviceRole(name='Device Role 2', slug='device-role-2'),
        )
        DeviceRole.objects.bulk_create(deviceroles)

        platforms = (
            Platform(name='Platform 1', slug='platform-1'),
            Platform(name='Platform 2', slug='platform-2'),
        )
        Platform.objects.bulk_create(platforms)

        Device.objects.bulk_create([
            Device(name='Device 1', site=sites[0], rack=racks[0], device_type=devicetypes[0], device_role=deviceroles[0], platform=platforms[0]),
            Device(name='Device 2', site=sites[0], rack=racks[0], device_type=devicetypes[0], device_role=deviceroles[0], platform=platforms[0]),
            Device(name='Device 3', site=sites[0], rack=racks[0], device_type=devicetypes[0], device_role=deviceroles[0], platform=platforms[0]),
        ])

        cls.form_data = {
            'device_type': devicetypes[1].pk,
            'device_role': deviceroles[1].pk,
            'tenant': None,
            'platform': platforms[1].pk,
            'name': 'Device X',
            'serial': '123456',
            'asset_tag': 'ABCDEF',
            'site': sites[1].pk,
            'rack': racks[1].pk,
            'position': 1,
            'face': DeviceFaceChoices.FACE_FRONT,
            'status': DeviceStatusChoices.STATUS_PLANNED,
            'primary_ip4': None,
            'primary_ip6': None,
            'cluster': None,
            'virtual_chassis': None,
            'vc_position': None,
            'vc_priority': None,
            'comments': 'A new device',
            'tags': 'Alpha,Bravo,Charlie',
            'local_context_data': None,
        }

        cls.csv_data = (
            "device_role,manufacturer,model_name,status,site,name",
            "Device Role 1,Manufacturer 1,Device Type 1,Active,Site 1,Device 4",
            "Device Role 1,Manufacturer 1,Device Type 1,Active,Site 1,Device 5",
            "Device Role 1,Manufacturer 1,Device Type 1,Active,Site 1,Device 6",
        )

        cls.bulk_edit_data = {
            'device_type': devicetypes[1].pk,
            'device_role': deviceroles[1].pk,
            'tenant': None,
            'platform': platforms[1].pk,
            'serial': '123456',
            'status': DeviceStatusChoices.STATUS_DECOMMISSIONING,
        }


class ConsolePortTestCase(ViewTestCases.DeviceComponentViewTestCase):
    model = ConsolePort

    @classmethod
    def setUpTestData(cls):
        device = create_test_device('Device 1')

        ConsolePort.objects.bulk_create([
            ConsolePort(device=device, name='Console Port 1'),
            ConsolePort(device=device, name='Console Port 2'),
            ConsolePort(device=device, name='Console Port 3'),
        ])

        cls.form_data = {
            'device': device.pk,
            'name': 'Console Port X',
            'type': ConsolePortTypeChoices.TYPE_RJ45,
            'description': 'A console port',
            'tags': 'Alpha,Bravo,Charlie',
        }

        cls.bulk_create_data = {
            'device': device.pk,
            'name_pattern': 'Console Port [4-6]',
            'type': ConsolePortTypeChoices.TYPE_RJ45,
            'description': 'A console port',
            'tags': 'Alpha,Bravo,Charlie',
        }

        cls.bulk_edit_data = {
            'type': ConsolePortTypeChoices.TYPE_RJ45,
            'description': 'New description',
        }

        cls.csv_data = (
            "device,name",
            "Device 1,Console Port 4",
            "Device 1,Console Port 5",
            "Device 1,Console Port 6",
        )


class ConsoleServerPortTestCase(ViewTestCases.DeviceComponentViewTestCase):
    model = ConsoleServerPort

    @classmethod
    def setUpTestData(cls):
        device = create_test_device('Device 1')

        ConsoleServerPort.objects.bulk_create([
            ConsoleServerPort(device=device, name='Console Server Port 1'),
            ConsoleServerPort(device=device, name='Console Server Port 2'),
            ConsoleServerPort(device=device, name='Console Server Port 3'),
        ])

        cls.form_data = {
            'device': device.pk,
            'name': 'Console Server Port X',
            'type': ConsolePortTypeChoices.TYPE_RJ45,
            'description': 'A console server port',
            'tags': 'Alpha,Bravo,Charlie',
        }

        cls.bulk_create_data = {
            'device': device.pk,
            'name_pattern': 'Console Server Port [4-6]',
            'type': ConsolePortTypeChoices.TYPE_RJ45,
            'description': 'A console server port',
            'tags': 'Alpha,Bravo,Charlie',
        }

        cls.bulk_edit_data = {
            'device': device.pk,
            'type': ConsolePortTypeChoices.TYPE_RJ45,
            'description': 'New description',
        }

        cls.csv_data = (
            "device,name",
            "Device 1,Console Server Port 4",
            "Device 1,Console Server Port 5",
            "Device 1,Console Server Port 6",
        )


class PowerPortTestCase(ViewTestCases.DeviceComponentViewTestCase):
    model = PowerPort

    @classmethod
    def setUpTestData(cls):
        device = create_test_device('Device 1')

        PowerPort.objects.bulk_create([
            PowerPort(device=device, name='Power Port 1'),
            PowerPort(device=device, name='Power Port 2'),
            PowerPort(device=device, name='Power Port 3'),
        ])

        cls.form_data = {
            'device': device.pk,
            'name': 'Power Port X',
            'type': PowerPortTypeChoices.TYPE_IEC_C14,
            'maximum_draw': 100,
            'allocated_draw': 50,
            'description': 'A power port',
            'tags': 'Alpha,Bravo,Charlie',
        }

        cls.bulk_create_data = {
            'device': device.pk,
            'name_pattern': 'Power Port [4-6]]',
            'type': PowerPortTypeChoices.TYPE_IEC_C14,
            'maximum_draw': 100,
            'allocated_draw': 50,
            'description': 'A power port',
            'tags': 'Alpha,Bravo,Charlie',
        }

        cls.bulk_edit_data = {
            'type': PowerPortTypeChoices.TYPE_IEC_C14,
            'maximum_draw': 100,
            'allocated_draw': 50,
            'description': 'New description',
        }

        cls.csv_data = (
            "device,name",
            "Device 1,Power Port 4",
            "Device 1,Power Port 5",
            "Device 1,Power Port 6",
        )


class PowerOutletTestCase(ViewTestCases.DeviceComponentViewTestCase):
    model = PowerOutlet

    @classmethod
    def setUpTestData(cls):
        device = create_test_device('Device 1')

        powerports = (
            PowerPort(device=device, name='Power Port 1'),
            PowerPort(device=device, name='Power Port 2'),
        )
        PowerPort.objects.bulk_create(powerports)

        PowerOutlet.objects.bulk_create([
            PowerOutlet(device=device, name='Power Outlet 1', power_port=powerports[0]),
            PowerOutlet(device=device, name='Power Outlet 2', power_port=powerports[0]),
            PowerOutlet(device=device, name='Power Outlet 3', power_port=powerports[0]),
        ])

        cls.form_data = {
            'device': device.pk,
            'name': 'Power Outlet X',
            'type': PowerOutletTypeChoices.TYPE_IEC_C13,
            'power_port': powerports[1].pk,
            'feed_leg': PowerOutletFeedLegChoices.FEED_LEG_B,
            'description': 'A power outlet',
            'tags': 'Alpha,Bravo,Charlie',
        }

        cls.bulk_create_data = {
            'device': device.pk,
            'name_pattern': 'Power Outlet [4-6]',
            'type': PowerOutletTypeChoices.TYPE_IEC_C13,
            'power_port': powerports[1].pk,
            'feed_leg': PowerOutletFeedLegChoices.FEED_LEG_B,
            'description': 'A power outlet',
            'tags': 'Alpha,Bravo,Charlie',
        }

        cls.bulk_edit_data = {
            'device': device.pk,
            'type': PowerOutletTypeChoices.TYPE_IEC_C13,
            'power_port': powerports[1].pk,
            'feed_leg': PowerOutletFeedLegChoices.FEED_LEG_B,
            'description': 'New description',
        }

        cls.csv_data = (
            "device,name",
            "Device 1,Power Outlet 4",
            "Device 1,Power Outlet 5",
            "Device 1,Power Outlet 6",
        )


class InterfaceTestCase(
    ViewTestCases.GetObjectViewTestCase,
    ViewTestCases.DeviceComponentViewTestCase,
):
    model = Interface

    @classmethod
    def setUpTestData(cls):
        device = create_test_device('Device 1')

        interfaces = (
            Interface(device=device, name='Interface 1'),
            Interface(device=device, name='Interface 2'),
            Interface(device=device, name='Interface 3'),
            Interface(device=device, name='LAG', type=InterfaceTypeChoices.TYPE_LAG),
        )
        Interface.objects.bulk_create(interfaces)

        vlans = (
            VLAN(vid=1, name='VLAN1', site=device.site),
            VLAN(vid=101, name='VLAN101', site=device.site),
            VLAN(vid=102, name='VLAN102', site=device.site),
            VLAN(vid=103, name='VLAN103', site=device.site),
        )
        VLAN.objects.bulk_create(vlans)

        cls.form_data = {
            'device': device.pk,
            'virtual_machine': None,
            'name': 'Interface X',
            'type': InterfaceTypeChoices.TYPE_1GE_GBIC,
            'enabled': False,
            'lag': interfaces[3].pk,
            'mac_address': EUI('01:02:03:04:05:06'),
            'mtu': 2000,
            'mgmt_only': True,
            'description': 'A front port',
            'mode': InterfaceModeChoices.MODE_TAGGED,
            'untagged_vlan': vlans[0].pk,
            'tagged_vlans': [v.pk for v in vlans[1:4]],
            'tags': 'Alpha,Bravo,Charlie',
        }

        cls.bulk_create_data = {
            'device': device.pk,
            'name_pattern': 'Interface [4-6]',
            'type': InterfaceTypeChoices.TYPE_1GE_GBIC,
            'enabled': False,
            'lag': interfaces[3].pk,
            'mac_address': EUI('01:02:03:04:05:06'),
            'mtu': 2000,
            'mgmt_only': True,
            'description': 'A front port',
            'mode': InterfaceModeChoices.MODE_TAGGED,
            'untagged_vlan': vlans[0].pk,
            'tagged_vlans': [v.pk for v in vlans[1:4]],
            'tags': 'Alpha,Bravo,Charlie',
        }

        cls.bulk_edit_data = {
            'device': device.pk,
            'type': InterfaceTypeChoices.TYPE_1GE_GBIC,
            'enabled': False,
            'lag': interfaces[3].pk,
            'mac_address': EUI('01:02:03:04:05:06'),
            'mtu': 2000,
            'mgmt_only': True,
            'description': 'New description',
            'mode': InterfaceModeChoices.MODE_TAGGED,
            'untagged_vlan': vlans[0].pk,
            'tagged_vlans': [v.pk for v in vlans[1:4]],
        }

        cls.csv_data = (
            "device,name,type",
            "Device 1,Interface 4,1000BASE-T (1GE)",
            "Device 1,Interface 5,1000BASE-T (1GE)",
            "Device 1,Interface 6,1000BASE-T (1GE)",
        )


class FrontPortTestCase(ViewTestCases.DeviceComponentViewTestCase):
    model = FrontPort

    @classmethod
    def setUpTestData(cls):
        device = create_test_device('Device 1')

        rearports = (
            RearPort(device=device, name='Rear Port 1'),
            RearPort(device=device, name='Rear Port 2'),
            RearPort(device=device, name='Rear Port 3'),
            RearPort(device=device, name='Rear Port 4'),
            RearPort(device=device, name='Rear Port 5'),
            RearPort(device=device, name='Rear Port 6'),
        )
        RearPort.objects.bulk_create(rearports)

        FrontPort.objects.bulk_create([
            FrontPort(device=device, name='Front Port 1', rear_port=rearports[0]),
            FrontPort(device=device, name='Front Port 2', rear_port=rearports[1]),
            FrontPort(device=device, name='Front Port 3', rear_port=rearports[2]),
        ])

        cls.form_data = {
            'device': device.pk,
            'name': 'Front Port X',
            'type': PortTypeChoices.TYPE_8P8C,
            'rear_port': rearports[3].pk,
            'rear_port_position': 1,
            'description': 'New description',
            'tags': 'Alpha,Bravo,Charlie',
        }

        cls.bulk_create_data = {
            'device': device.pk,
            'name_pattern': 'Front Port [4-6]',
            'type': PortTypeChoices.TYPE_8P8C,
            'rear_port_set': [
                '{}:1'.format(rp.pk) for rp in rearports[3:6]
            ],
            'description': 'New description',
            'tags': 'Alpha,Bravo,Charlie',
        }

        cls.bulk_edit_data = {
            'type': PortTypeChoices.TYPE_8P8C,
            'description': 'New description',
        }

        cls.csv_data = (
            "device,name,type,rear_port,rear_port_position",
            "Device 1,Front Port 4,8P8C,Rear Port 4,1",
            "Device 1,Front Port 5,8P8C,Rear Port 5,1",
            "Device 1,Front Port 6,8P8C,Rear Port 6,1",
        )


class RearPortTestCase(ViewTestCases.DeviceComponentViewTestCase):
    model = RearPort

    @classmethod
    def setUpTestData(cls):
        device = create_test_device('Device 1')

        RearPort.objects.bulk_create([
            RearPort(device=device, name='Rear Port 1'),
            RearPort(device=device, name='Rear Port 2'),
            RearPort(device=device, name='Rear Port 3'),
        ])

        cls.form_data = {
            'device': device.pk,
            'name': 'Rear Port X',
            'type': PortTypeChoices.TYPE_8P8C,
            'positions': 3,
            'description': 'A rear port',
            'tags': 'Alpha,Bravo,Charlie',
        }

        cls.bulk_create_data = {
            'device': device.pk,
            'name_pattern': 'Rear Port [4-6]',
            'type': PortTypeChoices.TYPE_8P8C,
            'positions': 3,
            'description': 'A rear port',
            'tags': 'Alpha,Bravo,Charlie',
        }

        cls.bulk_edit_data = {
            'type': PortTypeChoices.TYPE_8P8C,
            'description': 'New description',
        }

        cls.csv_data = (
            "device,name,type,positions",
            "Device 1,Rear Port 4,8P8C,1",
            "Device 1,Rear Port 5,8P8C,1",
            "Device 1,Rear Port 6,8P8C,1",
        )


class DeviceBayTestCase(ViewTestCases.DeviceComponentViewTestCase):
    model = DeviceBay

    # Disable inapplicable views
    test_bulk_edit_objects = None

    @classmethod
    def setUpTestData(cls):
        device1 = create_test_device('Device 1')
        device2 = create_test_device('Device 2')

        # Update the DeviceType subdevice role to allow adding DeviceBays
        DeviceType.objects.update(subdevice_role=SubdeviceRoleChoices.ROLE_PARENT)

        DeviceBay.objects.bulk_create([
            DeviceBay(device=device1, name='Device Bay 1'),
            DeviceBay(device=device1, name='Device Bay 2'),
            DeviceBay(device=device1, name='Device Bay 3'),
        ])

        cls.form_data = {
            'device': device2.pk,
            'name': 'Device Bay X',
            'description': 'A device bay',
            'tags': 'Alpha,Bravo,Charlie',
        }

        cls.bulk_create_data = {
            'device': device2.pk,
            'name_pattern': 'Device Bay [4-6]',
            'description': 'A device bay',
            'tags': 'Alpha,Bravo,Charlie',
        }

        cls.csv_data = (
            "device,name",
            "Device 1,Device Bay 4",
            "Device 1,Device Bay 5",
            "Device 1,Device Bay 6",
        )


class InventoryItemTestCase(ViewTestCases.DeviceComponentViewTestCase):
    model = InventoryItem

    @classmethod
    def setUpTestData(cls):
        device = create_test_device('Device 1')
        manufacturer, _ = Manufacturer.objects.get_or_create(name='Manufacturer 1', slug='manufacturer-1')

        InventoryItem.objects.bulk_create([
            InventoryItem(device=device, name='Inventory Item 1'),
            InventoryItem(device=device, name='Inventory Item 2'),
            InventoryItem(device=device, name='Inventory Item 3'),
        ])

        cls.form_data = {
            'device': device.pk,
            'manufacturer': manufacturer.pk,
            'name': 'Inventory Item X',
            'parent': None,
            'discovered': False,
            'part_id': '123456',
            'serial': '123ABC',
            'asset_tag': 'ABC123',
            'description': 'An inventory item',
            'tags': 'Alpha,Bravo,Charlie',
        }

        cls.bulk_create_data = {
            'device': device.pk,
            'name_pattern': 'Inventory Item [4-6]',
            'manufacturer': manufacturer.pk,
            'parent': None,
            'discovered': False,
            'part_id': '123456',
            'serial': '123ABC',
            'description': 'An inventory item',
            'tags': 'Alpha,Bravo,Charlie',
        }

        cls.bulk_edit_data = {
            'device': device.pk,
            'manufacturer': manufacturer.pk,
            'part_id': '123456',
            'description': 'New description',
        }

        cls.csv_data = (
            "device,name",
            "Device 1,Inventory Item 4",
            "Device 1,Inventory Item 5",
            "Device 1,Inventory Item 6",
        )


class CableTestCase(ViewTestCases.PrimaryObjectViewTestCase):
    model = Cable

    # TODO: Creation URL needs termination context
    test_create_object = None

    @classmethod
    def setUpTestData(cls):

        site = Site.objects.create(name='Site 1', slug='site-1')
        manufacturer = Manufacturer.objects.create(name='Manufacturer 1', slug='manufacturer-1')
        devicetype = DeviceType.objects.create(model='Device Type 1', manufacturer=manufacturer)
        devicerole = DeviceRole.objects.create(name='Device Role 1', slug='device-role-1')

        devices = (
            Device(name='Device 1', site=site, device_type=devicetype, device_role=devicerole),
            Device(name='Device 2', site=site, device_type=devicetype, device_role=devicerole),
            Device(name='Device 3', site=site, device_type=devicetype, device_role=devicerole),
            Device(name='Device 4', site=site, device_type=devicetype, device_role=devicerole),
        )
        Device.objects.bulk_create(devices)

        interfaces = (
            Interface(device=devices[0], name='Interface 1', type=InterfaceTypeChoices.TYPE_1GE_FIXED),
            Interface(device=devices[0], name='Interface 2', type=InterfaceTypeChoices.TYPE_1GE_FIXED),
            Interface(device=devices[0], name='Interface 3', type=InterfaceTypeChoices.TYPE_1GE_FIXED),
            Interface(device=devices[1], name='Interface 1', type=InterfaceTypeChoices.TYPE_1GE_FIXED),
            Interface(device=devices[1], name='Interface 2', type=InterfaceTypeChoices.TYPE_1GE_FIXED),
            Interface(device=devices[1], name='Interface 3', type=InterfaceTypeChoices.TYPE_1GE_FIXED),
            Interface(device=devices[2], name='Interface 1', type=InterfaceTypeChoices.TYPE_1GE_FIXED),
            Interface(device=devices[2], name='Interface 2', type=InterfaceTypeChoices.TYPE_1GE_FIXED),
            Interface(device=devices[2], name='Interface 3', type=InterfaceTypeChoices.TYPE_1GE_FIXED),
            Interface(device=devices[3], name='Interface 1', type=InterfaceTypeChoices.TYPE_1GE_FIXED),
            Interface(device=devices[3], name='Interface 2', type=InterfaceTypeChoices.TYPE_1GE_FIXED),
            Interface(device=devices[3], name='Interface 3', type=InterfaceTypeChoices.TYPE_1GE_FIXED),
        )
        Interface.objects.bulk_create(interfaces)

        Cable(termination_a=interfaces[0], termination_b=interfaces[3], type=CableTypeChoices.TYPE_CAT6).save()
        Cable(termination_a=interfaces[1], termination_b=interfaces[4], type=CableTypeChoices.TYPE_CAT6).save()
        Cable(termination_a=interfaces[2], termination_b=interfaces[5], type=CableTypeChoices.TYPE_CAT6).save()

        interface_ct = ContentType.objects.get_for_model(Interface)
        cls.form_data = {
            # Changing terminations not supported when editing an existing Cable
            'termination_a_type': interface_ct.pk,
            'termination_a_id': interfaces[0].pk,
            'termination_b_type': interface_ct.pk,
            'termination_b_id': interfaces[3].pk,
            'type': CableTypeChoices.TYPE_CAT6,
            'status': CableStatusChoices.STATUS_PLANNED,
            'label': 'Label',
            'color': 'c0c0c0',
            'length': 100,
            'length_unit': CableLengthUnitChoices.UNIT_FOOT,
        }

        cls.csv_data = (
            "side_a_device,side_a_type,side_a_name,side_b_device,side_b_type,side_b_name",
            "Device 3,interface,Interface 1,Device 4,interface,Interface 1",
            "Device 3,interface,Interface 2,Device 4,interface,Interface 2",
            "Device 3,interface,Interface 3,Device 4,interface,Interface 3",
        )

        cls.bulk_edit_data = {
            'type': CableTypeChoices.TYPE_CAT5E,
            'status': CableStatusChoices.STATUS_CONNECTED,
            'label': 'New label',
            'color': '00ff00',
            'length': 50,
            'length_unit': CableLengthUnitChoices.UNIT_METER,
        }


class VirtualChassisTestCase(ViewTestCases.PrimaryObjectViewTestCase):
    model = VirtualChassis

    # Disable inapplicable tests
    test_get_object = None
    test_import_objects = None
    test_bulk_edit_objects = None
    test_bulk_delete_objects = None

    # TODO: Requires special form handling
    test_create_object = None
    test_edit_object = None

    @classmethod
    def setUpTestData(cls):

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


class PowerPanelTestCase(ViewTestCases.PrimaryObjectViewTestCase):
    model = PowerPanel

    @classmethod
    def setUpTestData(cls):

        sites = (
            Site(name='Site 1', slug='site-1'),
            Site(name='Site 2', slug='site-2'),
        )
        Site.objects.bulk_create(sites)

        rackgroups = (
            RackGroup(name='Rack Group 1', slug='rack-group-1', site=sites[0]),
            RackGroup(name='Rack Group 2', slug='rack-group-2', site=sites[1]),
        )
        RackGroup.objects.bulk_create(rackgroups)

        PowerPanel.objects.bulk_create((
            PowerPanel(site=sites[0], rack_group=rackgroups[0], name='Power Panel 1'),
            PowerPanel(site=sites[0], rack_group=rackgroups[0], name='Power Panel 2'),
            PowerPanel(site=sites[0], rack_group=rackgroups[0], name='Power Panel 3'),
        ))

        cls.form_data = {
            'site': sites[1].pk,
            'rack_group': rackgroups[1].pk,
            'name': 'Power Panel X',
        }

        cls.csv_data = (
            "site,rack_group_name,name",
            "Site 1,Rack Group 1,Power Panel 4",
            "Site 1,Rack Group 1,Power Panel 5",
            "Site 1,Rack Group 1,Power Panel 6",
        )

        cls.bulk_edit_data = {
            'site': sites[1].pk,
            'rack_group': rackgroups[1].pk,
        }


class PowerFeedTestCase(ViewTestCases.PrimaryObjectViewTestCase):
    model = PowerFeed

    @classmethod
    def setUpTestData(cls):

        site = Site.objects.create(name='Site 1', slug='site-1')

        powerpanels = (
            PowerPanel(site=site, name='Power Panel 1'),
            PowerPanel(site=site, name='Power Panel 2'),
        )
        PowerPanel.objects.bulk_create(powerpanels)

        racks = (
            Rack(site=site, name='Rack 1'),
            Rack(site=site, name='Rack 2'),
        )
        Rack.objects.bulk_create(racks)

        PowerFeed.objects.bulk_create((
            PowerFeed(name='Power Feed 1', power_panel=powerpanels[0], rack=racks[0]),
            PowerFeed(name='Power Feed 2', power_panel=powerpanels[0], rack=racks[0]),
            PowerFeed(name='Power Feed 3', power_panel=powerpanels[0], rack=racks[0]),
        ))

        cls.form_data = {
            'name': 'Power Feed X',
            'power_panel': powerpanels[1].pk,
            'rack': racks[1].pk,
            'status': PowerFeedStatusChoices.STATUS_PLANNED,
            'type': PowerFeedTypeChoices.TYPE_REDUNDANT,
            'supply': PowerFeedSupplyChoices.SUPPLY_DC,
            'phase': PowerFeedPhaseChoices.PHASE_3PHASE,
            'voltage': 100,
            'amperage': 100,
            'max_utilization': 50,
            'comments': 'New comments',
            'tags': 'Alpha,Bravo,Charlie',

            # Connection
            'cable': None,
            'connected_endpoint': None,
            'connection_status': None,
        }

        cls.csv_data = (
            "site,panel_name,name,voltage,amperage,max_utilization",
            "Site 1,Power Panel 1,Power Feed 4,120,20,80",
            "Site 1,Power Panel 1,Power Feed 5,120,20,80",
            "Site 1,Power Panel 1,Power Feed 6,120,20,80",
        )

        cls.bulk_edit_data = {
            'power_panel': powerpanels[1].pk,
            'rack': racks[1].pk,
            'status': PowerFeedStatusChoices.STATUS_PLANNED,
            'type': PowerFeedTypeChoices.TYPE_REDUNDANT,
            'supply': PowerFeedSupplyChoices.SUPPLY_DC,
            'phase': PowerFeedPhaseChoices.PHASE_3PHASE,
            'voltage': 100,
            'amperage': 100,
            'max_utilization': 50,
            'comments': 'New comments',
        }
