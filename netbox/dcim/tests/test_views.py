from decimal import Decimal

import pytz
import yaml
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.test import override_settings
from django.urls import reverse
from netaddr import EUI

from dcim.choices import *
from dcim.constants import *
from dcim.models import *
from ipam.models import VLAN
from utilities.testing import ViewTestCases, create_test_device


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
            'description': 'A new region',
        }

        cls.csv_data = (
            "name,slug,description",
            "Region 4,region-4,Fourth region",
            "Region 5,region-5,Fifth region",
            "Region 6,region-6,Sixth region",
        )

        cls.bulk_edit_data = {
            'description': 'New description',
        }


class SiteGroupTestCase(ViewTestCases.OrganizationalObjectViewTestCase):
    model = SiteGroup

    @classmethod
    def setUpTestData(cls):

        # Create three SiteGroups
        sitegroups = (
            SiteGroup(name='Site Group 1', slug='site-group-1'),
            SiteGroup(name='Site Group 2', slug='site-group-2'),
            SiteGroup(name='Site Group 3', slug='site-group-3'),
        )
        for sitegroup in sitegroups:
            sitegroup.save()

        cls.form_data = {
            'name': 'Site Group X',
            'slug': 'site-group-x',
            'parent': sitegroups[2].pk,
            'description': 'A new site group',
        }

        cls.csv_data = (
            "name,slug,description",
            "Site Group 4,site-group-4,Fourth site group",
            "Site Group 5,site-group-5,Fifth site group",
            "Site Group 6,site-group-6,Sixth site group",
        )

        cls.bulk_edit_data = {
            'description': 'New description',
        }


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

        groups = (
            SiteGroup(name='Site Group 1', slug='site-group-1'),
            SiteGroup(name='Site Group 2', slug='site-group-2'),
        )
        for group in groups:
            group.save()

        Site.objects.bulk_create([
            Site(name='Site 1', slug='site-1', region=regions[0], group=groups[1]),
            Site(name='Site 2', slug='site-2', region=regions[0], group=groups[1]),
            Site(name='Site 3', slug='site-3', region=regions[0], group=groups[1]),
        ])

        tags = cls.create_tags('Alpha', 'Bravo', 'Charlie')

        cls.form_data = {
            'name': 'Site X',
            'slug': 'site-x',
            'status': SiteStatusChoices.STATUS_PLANNED,
            'region': regions[1].pk,
            'group': groups[1].pk,
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
            'tags': [t.pk for t in tags],
        }

        cls.csv_data = (
            "name,slug,status",
            "Site 4,site-4,planned",
            "Site 5,site-5,active",
            "Site 6,site-6,staging",
        )

        cls.bulk_edit_data = {
            'status': SiteStatusChoices.STATUS_PLANNED,
            'region': regions[1].pk,
            'group': groups[1].pk,
            'tenant': None,
            'asn': 65009,
            'time_zone': pytz.timezone('US/Eastern'),
            'description': 'New description',
        }


class LocationTestCase(ViewTestCases.OrganizationalObjectViewTestCase):
    model = Location

    @classmethod
    def setUpTestData(cls):

        site = Site(name='Site 1', slug='site-1')
        site.save()

        locations = (
            Location(name='Location 1', slug='location-1', site=site),
            Location(name='Location 2', slug='location-2', site=site),
            Location(name='Location 3', slug='location-3', site=site),
        )
        for location in locations:
            location.save()

        cls.form_data = {
            'name': 'Location X',
            'slug': 'location-x',
            'site': site.pk,
            'description': 'A new location',
        }

        cls.csv_data = (
            "site,name,slug,description",
            "Site 1,Location 4,location-4,Fourth location",
            "Site 1,Location 5,location-5,Fifth location",
            "Site 1,Location 6,location-6,Sixth location",
        )

        cls.bulk_edit_data = {
            'description': 'New description',
        }


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

        cls.bulk_edit_data = {
            'color': '00ff00',
            'description': 'New description',
        }


class RackReservationTestCase(ViewTestCases.PrimaryObjectViewTestCase):
    model = RackReservation

    @classmethod
    def setUpTestData(cls):

        user2 = User.objects.create_user(username='testuser2')
        user3 = User.objects.create_user(username='testuser3')

        site = Site.objects.create(name='Site 1', slug='site-1')

        location = Location(name='Location 1', slug='location-1', site=site)
        location.save()

        rack = Rack(name='Rack 1', site=site, location=location)
        rack.save()

        RackReservation.objects.bulk_create([
            RackReservation(rack=rack, user=user2, units=[1, 2, 3], description='Reservation 1'),
            RackReservation(rack=rack, user=user2, units=[4, 5, 6], description='Reservation 2'),
            RackReservation(rack=rack, user=user2, units=[7, 8, 9], description='Reservation 3'),
        ])

        tags = cls.create_tags('Alpha', 'Bravo', 'Charlie')

        cls.form_data = {
            'rack': rack.pk,
            'units': "10,11,12",
            'user': user3.pk,
            'tenant': None,
            'description': 'Rack reservation',
            'tags': [t.pk for t in tags],
        }

        cls.csv_data = (
            'site,location,rack,units,description',
            'Site 1,Location 1,Rack 1,"10,11,12",Reservation 1',
            'Site 1,Location 1,Rack 1,"13,14,15",Reservation 2',
            'Site 1,Location 1,Rack 1,"16,17,18",Reservation 3',
        )

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

        locations = (
            Location(name='Location 1', slug='location-1', site=sites[0]),
            Location(name='Location 2', slug='location-2', site=sites[1])
        )
        for location in locations:
            location.save()

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

        tags = cls.create_tags('Alpha', 'Bravo', 'Charlie')

        cls.form_data = {
            'name': 'Rack X',
            'facility_id': 'Facility X',
            'site': sites[1].pk,
            'location': locations[1].pk,
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
            'tags': [t.pk for t in tags],
        }

        cls.csv_data = (
            "site,location,name,width,u_height",
            "Site 1,,Rack 4,19,42",
            "Site 1,Location 1,Rack 5,19,42",
            "Site 2,Location 2,Rack 6,19,42",
        )

        cls.bulk_edit_data = {
            'site': sites[1].pk,
            'location': locations[1].pk,
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

    @override_settings(EXEMPT_VIEW_PERMISSIONS=['*'])
    def test_list_rack_elevations(self):
        """
        Test viewing the list of rack elevations.
        """
        response = self.client.get(reverse('dcim:rack_elevation_list'))
        self.assertHttpStatus(response, 200)


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
            'description': 'A new manufacturer',
        }

        cls.csv_data = (
            "name,slug,description",
            "Manufacturer 4,manufacturer-4,Fourth manufacturer",
            "Manufacturer 5,manufacturer-5,Fifth manufacturer",
            "Manufacturer 6,manufacturer-6,Sixth manufacturer",
        )

        cls.bulk_edit_data = {
            'description': 'New description',
        }


# TODO: Change base class to PrimaryObjectViewTestCase
# Blocked by absence of bulk import view for DeviceTypes
class DeviceTypeTestCase(
    ViewTestCases.GetObjectViewTestCase,
    ViewTestCases.GetObjectChangelogViewTestCase,
    ViewTestCases.CreateObjectViewTestCase,
    ViewTestCases.EditObjectViewTestCase,
    ViewTestCases.DeleteObjectViewTestCase,
    ViewTestCases.ListObjectsViewTestCase,
    ViewTestCases.BulkEditObjectsViewTestCase,
    ViewTestCases.BulkDeleteObjectsViewTestCase
):
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

        tags = cls.create_tags('Alpha', 'Bravo', 'Charlie')

        cls.form_data = {
            'manufacturer': manufacturers[1].pk,
            'model': 'Device Type X',
            'slug': 'device-type-x',
            'part_number': '123ABC',
            'u_height': 2,
            'is_full_depth': True,
            'subdevice_role': '',  # CharField
            'comments': 'Some comments',
            'tags': [t.pk for t in tags],
        }

        cls.bulk_edit_data = {
            'manufacturer': manufacturers[1].pk,
            'u_height': 3,
            'is_full_depth': False,
        }

    @override_settings(EXEMPT_VIEW_PERMISSIONS=['*'])
    def test_import_objects(self):
        """
        Custom import test for YAML-based imports (versus CSV)
        """
        IMPORT_DATA = """
manufacturer: Generic
model: TEST-1000
slug: test-1000
u_height: 2
subdevice_role: parent
comments: test comment
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
        self.assertEqual(dt.comments, 'test comment')

        # Verify all of the components were created
        self.assertEqual(dt.consoleporttemplates.count(), 3)
        cp1 = ConsolePortTemplate.objects.first()
        self.assertEqual(cp1.name, 'Console Port 1')
        self.assertEqual(cp1.type, ConsolePortTypeChoices.TYPE_DE9)

        self.assertEqual(dt.consoleserverporttemplates.count(), 3)
        csp1 = ConsoleServerPortTemplate.objects.first()
        self.assertEqual(csp1.name, 'Console Server Port 1')
        self.assertEqual(csp1.type, ConsolePortTypeChoices.TYPE_RJ45)

        self.assertEqual(dt.powerporttemplates.count(), 3)
        pp1 = PowerPortTemplate.objects.first()
        self.assertEqual(pp1.name, 'Power Port 1')
        self.assertEqual(pp1.type, PowerPortTypeChoices.TYPE_IEC_C14)

        self.assertEqual(dt.poweroutlettemplates.count(), 3)
        po1 = PowerOutletTemplate.objects.first()
        self.assertEqual(po1.name, 'Power Outlet 1')
        self.assertEqual(po1.type, PowerOutletTypeChoices.TYPE_IEC_C13)
        self.assertEqual(po1.power_port, pp1)
        self.assertEqual(po1.feed_leg, PowerOutletFeedLegChoices.FEED_LEG_A)

        self.assertEqual(dt.interfacetemplates.count(), 3)
        iface1 = InterfaceTemplate.objects.first()
        self.assertEqual(iface1.name, 'Interface 1')
        self.assertEqual(iface1.type, InterfaceTypeChoices.TYPE_1GE_FIXED)
        self.assertTrue(iface1.mgmt_only)

        self.assertEqual(dt.rearporttemplates.count(), 3)
        rp1 = RearPortTemplate.objects.first()
        self.assertEqual(rp1.name, 'Rear Port 1')

        self.assertEqual(dt.frontporttemplates.count(), 3)
        fp1 = FrontPortTemplate.objects.first()
        self.assertEqual(fp1.name, 'Front Port 1')
        self.assertEqual(fp1.rear_port, rp1)
        self.assertEqual(fp1.rear_port_position, 1)

        self.assertEqual(dt.devicebaytemplates.count(), 3)
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
            # Test that a label can be applied to each generated interface templates
            'label_pattern': 'Interface Template Label [3-5]',
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

    @classmethod
    def setUpTestData(cls):
        manufacturer = Manufacturer.objects.create(name='Manufacturer 1', slug='manufacturer-1')
        devicetypes = (
            DeviceType(manufacturer=manufacturer, model='Device Type 1', slug='device-type-1', subdevice_role=SubdeviceRoleChoices.ROLE_PARENT),
            DeviceType(manufacturer=manufacturer, model='Device Type 2', slug='device-type-2', subdevice_role=SubdeviceRoleChoices.ROLE_PARENT),
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

        cls.bulk_edit_data = {
            'description': 'Foo bar',
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

        cls.bulk_edit_data = {
            'color': '00ff00',
            'description': 'New description',
        }


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
            'description': 'A new platform',
        }

        cls.csv_data = (
            "name,slug,description",
            "Platform 4,platform-4,Fourth platform",
            "Platform 5,platform-5,Fifth platform",
            "Platform 6,platform-6,Sixth platform",
        )

        cls.bulk_edit_data = {
            'napalm_driver': 'ios',
            'description': 'New description',
        }


class DeviceTestCase(ViewTestCases.PrimaryObjectViewTestCase):
    model = Device

    @classmethod
    def setUpTestData(cls):

        sites = (
            Site(name='Site 1', slug='site-1'),
            Site(name='Site 2', slug='site-2'),
        )
        Site.objects.bulk_create(sites)

        location = Location(site=sites[0], name='Location 1', slug='location-1')
        location.save()

        racks = (
            Rack(name='Rack 1', site=sites[0], location=location),
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

        tags = cls.create_tags('Alpha', 'Bravo', 'Charlie')

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
            'tags': [t.pk for t in tags],
            'local_context_data': None,
        }

        cls.csv_data = (
            "device_role,manufacturer,device_type,status,name,site,location,rack,position,face",
            "Device Role 1,Manufacturer 1,Device Type 1,active,Device 4,Site 1,Location 1,Rack 1,10,front",
            "Device Role 1,Manufacturer 1,Device Type 1,active,Device 5,Site 1,Location 1,Rack 1,20,front",
            "Device Role 1,Manufacturer 1,Device Type 1,active,Device 6,Site 1,Location 1,Rack 1,30,front",
        )

        cls.bulk_edit_data = {
            'device_type': devicetypes[1].pk,
            'device_role': deviceroles[1].pk,
            'tenant': None,
            'platform': platforms[1].pk,
            'serial': '123456',
            'status': DeviceStatusChoices.STATUS_DECOMMISSIONING,
        }

    @override_settings(EXEMPT_VIEW_PERMISSIONS=['*'])
    def test_device_consoleports(self):
        device = Device.objects.first()
        console_ports = (
            ConsolePort(device=device, name='Console Port 1'),
            ConsolePort(device=device, name='Console Port 2'),
            ConsolePort(device=device, name='Console Port 3'),
        )
        ConsolePort.objects.bulk_create(console_ports)

        url = reverse('dcim:device_consoleports', kwargs={'pk': device.pk})
        self.assertHttpStatus(self.client.get(url), 200)

    @override_settings(EXEMPT_VIEW_PERMISSIONS=['*'])
    def test_device_consoleserverports(self):
        device = Device.objects.first()
        console_server_ports = (
            ConsoleServerPort(device=device, name='Console Server Port 1'),
            ConsoleServerPort(device=device, name='Console Server Port 2'),
            ConsoleServerPort(device=device, name='Console Server Port 3'),
        )
        ConsoleServerPort.objects.bulk_create(console_server_ports)

        url = reverse('dcim:device_consoleserverports', kwargs={'pk': device.pk})
        self.assertHttpStatus(self.client.get(url), 200)

    @override_settings(EXEMPT_VIEW_PERMISSIONS=['*'])
    def test_device_powerports(self):
        device = Device.objects.first()
        power_ports = (
            PowerPort(device=device, name='Power Port 1'),
            PowerPort(device=device, name='Power Port 2'),
            PowerPort(device=device, name='Power Port 3'),
        )
        PowerPort.objects.bulk_create(power_ports)

        url = reverse('dcim:device_powerports', kwargs={'pk': device.pk})
        self.assertHttpStatus(self.client.get(url), 200)

    @override_settings(EXEMPT_VIEW_PERMISSIONS=['*'])
    def test_device_poweroutlets(self):
        device = Device.objects.first()
        power_outlets = (
            PowerOutlet(device=device, name='Power Outlet 1'),
            PowerOutlet(device=device, name='Power Outlet 2'),
            PowerOutlet(device=device, name='Power Outlet 3'),
        )
        PowerOutlet.objects.bulk_create(power_outlets)

        url = reverse('dcim:device_poweroutlets', kwargs={'pk': device.pk})
        self.assertHttpStatus(self.client.get(url), 200)

    @override_settings(EXEMPT_VIEW_PERMISSIONS=['*'])
    def test_device_interfaces(self):
        device = Device.objects.first()
        interfaces = (
            Interface(device=device, name='Interface 1'),
            Interface(device=device, name='Interface 2'),
            Interface(device=device, name='Interface 3'),
        )
        Interface.objects.bulk_create(interfaces)

        url = reverse('dcim:device_interfaces', kwargs={'pk': device.pk})
        self.assertHttpStatus(self.client.get(url), 200)

    @override_settings(EXEMPT_VIEW_PERMISSIONS=['*'])
    def test_device_rearports(self):
        device = Device.objects.first()
        rear_ports = (
            RearPort(device=device, name='Rear Port 1'),
            RearPort(device=device, name='Rear Port 2'),
            RearPort(device=device, name='Rear Port 3'),
        )
        RearPort.objects.bulk_create(rear_ports)

        url = reverse('dcim:device_rearports', kwargs={'pk': device.pk})
        self.assertHttpStatus(self.client.get(url), 200)

    @override_settings(EXEMPT_VIEW_PERMISSIONS=['*'])
    def test_device_frontports(self):
        device = Device.objects.first()
        rear_ports = (
            RearPort(device=device, name='Rear Port 1'),
            RearPort(device=device, name='Rear Port 2'),
            RearPort(device=device, name='Rear Port 3'),
        )
        RearPort.objects.bulk_create(rear_ports)
        front_ports = (
            FrontPort(device=device, name='Front Port 1', rear_port=rear_ports[0], rear_port_position=1),
            FrontPort(device=device, name='Front Port 2', rear_port=rear_ports[1], rear_port_position=1),
            FrontPort(device=device, name='Front Port 3', rear_port=rear_ports[2], rear_port_position=1),
        )
        FrontPort.objects.bulk_create(front_ports)

        url = reverse('dcim:device_frontports', kwargs={'pk': device.pk})
        self.assertHttpStatus(self.client.get(url), 200)

    @override_settings(EXEMPT_VIEW_PERMISSIONS=['*'])
    def test_device_devicebays(self):
        device = Device.objects.first()
        device_bays = (
            DeviceBay(device=device, name='Device Bay 1'),
            DeviceBay(device=device, name='Device Bay 2'),
            DeviceBay(device=device, name='Device Bay 3'),
        )
        DeviceBay.objects.bulk_create(device_bays)

        url = reverse('dcim:device_devicebays', kwargs={'pk': device.pk})
        self.assertHttpStatus(self.client.get(url), 200)

    @override_settings(EXEMPT_VIEW_PERMISSIONS=['*'])
    def test_device_inventory(self):
        device = Device.objects.first()
        inventory_items = (
            InventoryItem(device=device, name='Inventory Item 1'),
            InventoryItem(device=device, name='Inventory Item 2'),
            InventoryItem(device=device, name='Inventory Item 3'),
        )
        for item in inventory_items:
            item.save()

        url = reverse('dcim:device_inventory', kwargs={'pk': device.pk})
        self.assertHttpStatus(self.client.get(url), 200)


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

        tags = cls.create_tags('Alpha', 'Bravo', 'Charlie')

        cls.form_data = {
            'device': device.pk,
            'name': 'Console Port X',
            'type': ConsolePortTypeChoices.TYPE_RJ45,
            'description': 'A console port',
            'tags': sorted([t.pk for t in tags]),
        }

        cls.bulk_create_data = {
            'device': device.pk,
            'name_pattern': 'Console Port [4-6]',
            # Test that a label can be applied to each generated console ports
            'label_pattern': 'Serial[3-5]',
            'type': ConsolePortTypeChoices.TYPE_RJ45,
            'description': 'A console port',
            'tags': sorted([t.pk for t in tags]),
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

    @override_settings(EXEMPT_VIEW_PERMISSIONS=['*'])
    def test_trace(self):
        consoleport = ConsolePort.objects.first()
        consoleserverport = ConsoleServerPort.objects.create(
            device=consoleport.device,
            name='Console Server Port 1'
        )
        Cable(termination_a=consoleport, termination_b=consoleserverport).save()

        response = self.client.get(reverse('dcim:consoleport_trace', kwargs={'pk': consoleport.pk}))
        self.assertHttpStatus(response, 200)


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

        tags = cls.create_tags('Alpha', 'Bravo', 'Charlie')

        cls.form_data = {
            'device': device.pk,
            'name': 'Console Server Port X',
            'type': ConsolePortTypeChoices.TYPE_RJ45,
            'description': 'A console server port',
            'tags': [t.pk for t in tags],
        }

        cls.bulk_create_data = {
            'device': device.pk,
            'name_pattern': 'Console Server Port [4-6]',
            'type': ConsolePortTypeChoices.TYPE_RJ45,
            'description': 'A console server port',
            'tags': [t.pk for t in tags],
        }

        cls.bulk_edit_data = {
            'type': ConsolePortTypeChoices.TYPE_RJ11,
            'description': 'New description',
        }

        cls.csv_data = (
            "device,name",
            "Device 1,Console Server Port 4",
            "Device 1,Console Server Port 5",
            "Device 1,Console Server Port 6",
        )

    @override_settings(EXEMPT_VIEW_PERMISSIONS=['*'])
    def test_trace(self):
        consoleserverport = ConsoleServerPort.objects.first()
        consoleport = ConsolePort.objects.create(
            device=consoleserverport.device,
            name='Console Port 1'
        )
        Cable(termination_a=consoleserverport, termination_b=consoleport).save()

        response = self.client.get(reverse('dcim:consoleserverport_trace', kwargs={'pk': consoleserverport.pk}))
        self.assertHttpStatus(response, 200)


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

        tags = cls.create_tags('Alpha', 'Bravo', 'Charlie')

        cls.form_data = {
            'device': device.pk,
            'name': 'Power Port X',
            'type': PowerPortTypeChoices.TYPE_IEC_C14,
            'maximum_draw': 100,
            'allocated_draw': 50,
            'description': 'A power port',
            'tags': [t.pk for t in tags],
        }

        cls.bulk_create_data = {
            'device': device.pk,
            'name_pattern': 'Power Port [4-6]]',
            'type': PowerPortTypeChoices.TYPE_IEC_C14,
            'maximum_draw': 100,
            'allocated_draw': 50,
            'description': 'A power port',
            'tags': [t.pk for t in tags],
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

    @override_settings(EXEMPT_VIEW_PERMISSIONS=['*'])
    def test_trace(self):
        powerport = PowerPort.objects.first()
        poweroutlet = PowerOutlet.objects.create(
            device=powerport.device,
            name='Power Outlet 1'
        )
        Cable(termination_a=powerport, termination_b=poweroutlet).save()

        response = self.client.get(reverse('dcim:powerport_trace', kwargs={'pk': powerport.pk}))
        self.assertHttpStatus(response, 200)


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

        tags = cls.create_tags('Alpha', 'Bravo', 'Charlie')

        cls.form_data = {
            'device': device.pk,
            'name': 'Power Outlet X',
            'type': PowerOutletTypeChoices.TYPE_IEC_C13,
            'power_port': powerports[1].pk,
            'feed_leg': PowerOutletFeedLegChoices.FEED_LEG_B,
            'description': 'A power outlet',
            'tags': [t.pk for t in tags],
        }

        cls.bulk_create_data = {
            'device': device.pk,
            'name_pattern': 'Power Outlet [4-6]',
            'type': PowerOutletTypeChoices.TYPE_IEC_C13,
            'power_port': powerports[1].pk,
            'feed_leg': PowerOutletFeedLegChoices.FEED_LEG_B,
            'description': 'A power outlet',
            'tags': [t.pk for t in tags],
        }

        cls.bulk_edit_data = {
            'type': PowerOutletTypeChoices.TYPE_IEC_C15,
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

    @override_settings(EXEMPT_VIEW_PERMISSIONS=['*'])
    def test_trace(self):
        poweroutlet = PowerOutlet.objects.first()
        powerport = PowerPort.objects.first()
        Cable(termination_a=poweroutlet, termination_b=powerport).save()

        response = self.client.get(reverse('dcim:poweroutlet_trace', kwargs={'pk': poweroutlet.pk}))
        self.assertHttpStatus(response, 200)


class InterfaceTestCase(ViewTestCases.DeviceComponentViewTestCase):
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

        tags = cls.create_tags('Alpha', 'Bravo', 'Charlie')

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
            'tags': [t.pk for t in tags],
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
            'tags': [t.pk for t in tags],
        }

        cls.bulk_edit_data = {
            'type': InterfaceTypeChoices.TYPE_1GE_FIXED,
            'enabled': True,
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
            "Device 1,Interface 4,1000base-t",
            "Device 1,Interface 5,1000base-t",
            "Device 1,Interface 6,1000base-t",
        )

    @override_settings(EXEMPT_VIEW_PERMISSIONS=['*'])
    def test_trace(self):
        interface1, interface2 = Interface.objects.all()[:2]
        Cable(termination_a=interface1, termination_b=interface2).save()

        response = self.client.get(reverse('dcim:interface_trace', kwargs={'pk': interface1.pk}))
        self.assertHttpStatus(response, 200)


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

        tags = cls.create_tags('Alpha', 'Bravo', 'Charlie')

        cls.form_data = {
            'device': device.pk,
            'name': 'Front Port X',
            'type': PortTypeChoices.TYPE_8P8C,
            'rear_port': rearports[3].pk,
            'rear_port_position': 1,
            'description': 'New description',
            'tags': [t.pk for t in tags],
        }

        cls.bulk_create_data = {
            'device': device.pk,
            'name_pattern': 'Front Port [4-6]',
            'type': PortTypeChoices.TYPE_8P8C,
            'rear_port_set': [
                '{}:1'.format(rp.pk) for rp in rearports[3:6]
            ],
            'description': 'New description',
            'tags': [t.pk for t in tags],
        }

        cls.bulk_edit_data = {
            'type': PortTypeChoices.TYPE_8P8C,
            'description': 'New description',
        }

        cls.csv_data = (
            "device,name,type,rear_port,rear_port_position",
            "Device 1,Front Port 4,8p8c,Rear Port 4,1",
            "Device 1,Front Port 5,8p8c,Rear Port 5,1",
            "Device 1,Front Port 6,8p8c,Rear Port 6,1",
        )

    @override_settings(EXEMPT_VIEW_PERMISSIONS=['*'])
    def test_trace(self):
        frontport = FrontPort.objects.first()
        interface = Interface.objects.create(
            device=frontport.device,
            name='Interface 1'
        )
        Cable(termination_a=frontport, termination_b=interface).save()

        response = self.client.get(reverse('dcim:frontport_trace', kwargs={'pk': frontport.pk}))
        self.assertHttpStatus(response, 200)


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

        tags = cls.create_tags('Alpha', 'Bravo', 'Charlie')

        cls.form_data = {
            'device': device.pk,
            'name': 'Rear Port X',
            'type': PortTypeChoices.TYPE_8P8C,
            'positions': 3,
            'description': 'A rear port',
            'tags': [t.pk for t in tags],
        }

        cls.bulk_create_data = {
            'device': device.pk,
            'name_pattern': 'Rear Port [4-6]',
            'type': PortTypeChoices.TYPE_8P8C,
            'positions': 3,
            'description': 'A rear port',
            'tags': [t.pk for t in tags],
        }

        cls.bulk_edit_data = {
            'type': PortTypeChoices.TYPE_8P8C,
            'description': 'New description',
        }

        cls.csv_data = (
            "device,name,type,positions",
            "Device 1,Rear Port 4,8p8c,1",
            "Device 1,Rear Port 5,8p8c,1",
            "Device 1,Rear Port 6,8p8c,1",
        )

    @override_settings(EXEMPT_VIEW_PERMISSIONS=['*'])
    def test_trace(self):
        rearport = RearPort.objects.first()
        interface = Interface.objects.create(
            device=rearport.device,
            name='Interface 1'
        )
        Cable(termination_a=rearport, termination_b=interface).save()

        response = self.client.get(reverse('dcim:rearport_trace', kwargs={'pk': rearport.pk}))
        self.assertHttpStatus(response, 200)


class DeviceBayTestCase(ViewTestCases.DeviceComponentViewTestCase):
    model = DeviceBay

    @classmethod
    def setUpTestData(cls):
        device = create_test_device('Device 1')

        # Update the DeviceType subdevice role to allow adding DeviceBays
        DeviceType.objects.update(subdevice_role=SubdeviceRoleChoices.ROLE_PARENT)

        DeviceBay.objects.bulk_create([
            DeviceBay(device=device, name='Device Bay 1'),
            DeviceBay(device=device, name='Device Bay 2'),
            DeviceBay(device=device, name='Device Bay 3'),
        ])

        tags = cls.create_tags('Alpha', 'Bravo', 'Charlie')

        cls.form_data = {
            'device': device.pk,
            'name': 'Device Bay X',
            'description': 'A device bay',
            'tags': [t.pk for t in tags],
        }

        cls.bulk_create_data = {
            'device': device.pk,
            'name_pattern': 'Device Bay [4-6]',
            'description': 'A device bay',
            'tags': [t.pk for t in tags],
        }

        cls.bulk_edit_data = {
            'description': 'New description',
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

        InventoryItem.objects.create(device=device, name='Inventory Item 1')
        InventoryItem.objects.create(device=device, name='Inventory Item 2')
        InventoryItem.objects.create(device=device, name='Inventory Item 3')

        tags = cls.create_tags('Alpha', 'Bravo', 'Charlie')

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
            'tags': [t.pk for t in tags],
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
            'tags': [t.pk for t in tags],
        }

        cls.bulk_edit_data = {
            'part_id': '123456',
            'description': 'New description',
        }

        cls.csv_data = (
            "device,name",
            "Device 1,Inventory Item 4",
            "Device 1,Inventory Item 5",
            "Device 1,Inventory Item 6",
        )


# TODO: Change base class to PrimaryObjectViewTestCase
# Blocked by lack of common creation view for cables (termination A must be initialized)
class CableTestCase(
    ViewTestCases.GetObjectViewTestCase,
    ViewTestCases.GetObjectChangelogViewTestCase,
    ViewTestCases.EditObjectViewTestCase,
    ViewTestCases.DeleteObjectViewTestCase,
    ViewTestCases.ListObjectsViewTestCase,
    ViewTestCases.BulkImportObjectsViewTestCase,
    ViewTestCases.BulkEditObjectsViewTestCase,
    ViewTestCases.BulkDeleteObjectsViewTestCase
):
    model = Cable

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

        tags = cls.create_tags('Alpha', 'Bravo', 'Charlie')

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
            'tags': [t.pk for t in tags],
        }

        cls.csv_data = (
            "side_a_device,side_a_type,side_a_name,side_b_device,side_b_type,side_b_name",
            "Device 3,dcim.interface,Interface 1,Device 4,dcim.interface,Interface 1",
            "Device 3,dcim.interface,Interface 2,Device 4,dcim.interface,Interface 2",
            "Device 3,dcim.interface,Interface 3,Device 4,dcim.interface,Interface 3",
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

        devices = (
            Device(device_type=device_type, device_role=device_role, name='Device 1', site=site),
            Device(device_type=device_type, device_role=device_role, name='Device 2', site=site),
            Device(device_type=device_type, device_role=device_role, name='Device 3', site=site),
            Device(device_type=device_type, device_role=device_role, name='Device 4', site=site),
            Device(device_type=device_type, device_role=device_role, name='Device 5', site=site),
            Device(device_type=device_type, device_role=device_role, name='Device 6', site=site),
            Device(device_type=device_type, device_role=device_role, name='Device 7', site=site),
            Device(device_type=device_type, device_role=device_role, name='Device 8', site=site),
            Device(device_type=device_type, device_role=device_role, name='Device 9', site=site),
            Device(device_type=device_type, device_role=device_role, name='Device 10', site=site),
            Device(device_type=device_type, device_role=device_role, name='Device 11', site=site),
            Device(device_type=device_type, device_role=device_role, name='Device 12', site=site),
        )
        Device.objects.bulk_create(devices)

        # Create three VirtualChassis with three members each
        vc1 = VirtualChassis.objects.create(name='VC1', master=devices[0], domain='domain-1')
        Device.objects.filter(pk=devices[0].pk).update(virtual_chassis=vc1, vc_position=1)
        Device.objects.filter(pk=devices[1].pk).update(virtual_chassis=vc1, vc_position=2)
        Device.objects.filter(pk=devices[2].pk).update(virtual_chassis=vc1, vc_position=3)
        vc2 = VirtualChassis.objects.create(name='VC2', master=devices[3], domain='domain-2')
        Device.objects.filter(pk=devices[3].pk).update(virtual_chassis=vc2, vc_position=1)
        Device.objects.filter(pk=devices[4].pk).update(virtual_chassis=vc2, vc_position=2)
        Device.objects.filter(pk=devices[5].pk).update(virtual_chassis=vc2, vc_position=3)
        vc3 = VirtualChassis.objects.create(name='VC3', master=devices[6], domain='domain-3')
        Device.objects.filter(pk=devices[6].pk).update(virtual_chassis=vc3, vc_position=1)
        Device.objects.filter(pk=devices[7].pk).update(virtual_chassis=vc3, vc_position=2)
        Device.objects.filter(pk=devices[8].pk).update(virtual_chassis=vc3, vc_position=3)

        cls.form_data = {
            'name': 'VC4',
            'domain': 'domain-4',
            # Management form data for VC members
            'form-TOTAL_FORMS': 0,
            'form-INITIAL_FORMS': 3,
            'form-MIN_NUM_FORMS': 0,
            'form-MAX_NUM_FORMS': 1000,
        }

        cls.csv_data = (
            "name,domain,master",
            "VC4,Domain 4,Device 10",
            "VC5,Domain 5,Device 11",
            "VC6,Domain 6,Device 12",
        )

        cls.bulk_edit_data = {
            'domain': 'domain-x',
        }


class PowerPanelTestCase(ViewTestCases.PrimaryObjectViewTestCase):
    model = PowerPanel

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

        PowerPanel.objects.bulk_create((
            PowerPanel(site=sites[0], location=locations[0], name='Power Panel 1'),
            PowerPanel(site=sites[0], location=locations[0], name='Power Panel 2'),
            PowerPanel(site=sites[0], location=locations[0], name='Power Panel 3'),
        ))

        tags = cls.create_tags('Alpha', 'Bravo', 'Charlie')

        cls.form_data = {
            'site': sites[1].pk,
            'location': locations[1].pk,
            'name': 'Power Panel X',
            'tags': [t.pk for t in tags],
        }

        cls.csv_data = (
            "site,location,name",
            "Site 1,Location 1,Power Panel 4",
            "Site 1,Location 1,Power Panel 5",
            "Site 1,Location 1,Power Panel 6",
        )

        cls.bulk_edit_data = {
            'site': sites[1].pk,
            'location': locations[1].pk,
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

        tags = cls.create_tags('Alpha', 'Bravo', 'Charlie')

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
            'tags': [t.pk for t in tags],
        }

        cls.csv_data = (
            "site,power_panel,name,voltage,amperage,max_utilization",
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

    @override_settings(EXEMPT_VIEW_PERMISSIONS=['*'])
    def test_trace(self):
        manufacturer = Manufacturer.objects.create(name='Manufacturer', slug='manufacturer-1')
        device_type = DeviceType.objects.create(
            manufacturer=manufacturer, model='Device Type 1', slug='device-type-1'
        )
        device_role = DeviceRole.objects.create(
            name='Device Role', slug='device-role-1'
        )
        device = Device.objects.create(
            site=Site.objects.first(), device_type=device_type, device_role=device_role
        )

        powerfeed = PowerFeed.objects.first()
        powerport = PowerPort.objects.create(
            device=device,
            name='Power Port 1'
        )
        Cable(termination_a=powerfeed, termination_b=powerport).save()

        response = self.client.get(reverse('dcim:powerfeed_trace', kwargs={'pk': powerfeed.pk}))
        self.assertHttpStatus(response, 200)
