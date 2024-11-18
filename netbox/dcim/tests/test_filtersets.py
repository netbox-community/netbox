from django.test import TestCase

from circuits.models import Circuit, CircuitTermination, CircuitType, Provider
from dcim.choices import *
from dcim.filtersets import *
from dcim.models import *
from ipam.choices import VLANQinQRoleChoices
from ipam.models import ASN, IPAddress, RIR, VLAN, VLANTranslationPolicy, VRF
from netbox.choices import ColorChoices, WeightUnitChoices
from tenancy.models import Tenant, TenantGroup
from users.models import User
from utilities.testing import ChangeLoggedFilterSetTests, create_test_device, create_test_virtualmachine
from virtualization.models import Cluster, ClusterType, ClusterGroup, VMInterface, VirtualMachine
from wireless.choices import WirelessChannelChoices, WirelessRoleChoices


class DeviceComponentFilterSetTests:

    def test_q(self):
        params = {'q': 'First'}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_description(self):
        params = {'description': ['First', 'Second']}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_device_type(self):
        device_types = DeviceType.objects.all()[:2]
        params = {'device_type_id': [device_types[0].pk, device_types[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {'device_type': [device_types[0].model, device_types[1].model]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_device_role(self):
        role = DeviceRole.objects.all()[:2]
        params = {'device_role_id': [role[0].pk, role[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {'device_role': [role[0].slug, role[1].slug]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_device_status(self):
        params = {'device_status': ['active', 'planned']}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)


class DeviceComponentTemplateFilterSetTests:

    def test_q(self):
        params = {'q': 'foobar1'}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_description(self):
        params = {'description': ['foobar1', 'foobar2']}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_device_type_id(self):
        device_types = DeviceType.objects.all()[:2]
        params = {'device_type_id': [device_types[0].pk, device_types[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)


class RegionTestCase(TestCase, ChangeLoggedFilterSetTests):
    queryset = Region.objects.all()
    filterset = RegionFilterSet

    @classmethod
    def setUpTestData(cls):

        parent_regions = (
            Region(name='Region 1', slug='region-1', description='foobar1'),
            Region(name='Region 2', slug='region-2', description='foobar2'),
            Region(name='Region 3', slug='region-3', description='foobar3'),
        )
        for region in parent_regions:
            region.save()

        regions = (
            Region(name='Region 1A', slug='region-1a', parent=parent_regions[0]),
            Region(name='Region 1B', slug='region-1b', parent=parent_regions[0]),
            Region(name='Region 2A', slug='region-2a', parent=parent_regions[1]),
            Region(name='Region 2B', slug='region-2b', parent=parent_regions[1]),
            Region(name='Region 3A', slug='region-3a', parent=parent_regions[2]),
            Region(name='Region 3B', slug='region-3b', parent=parent_regions[2]),
        )
        for region in regions:
            region.save()

        child_regions = (
            Region(name='Region 1A1', slug='region-1a1', parent=regions[0]),
            Region(name='Region 1B1', slug='region-1b1', parent=regions[1]),
            Region(name='Region 2A1', slug='region-2a1', parent=regions[2]),
            Region(name='Region 2B1', slug='region-2b1', parent=regions[3]),
            Region(name='Region 3A1', slug='region-3a1', parent=regions[4]),
            Region(name='Region 3B1', slug='region-3b1', parent=regions[5]),
        )
        for region in child_regions:
            region.save()

    def test_q(self):
        params = {'q': 'foobar1'}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_name(self):
        params = {'name': ['Region 1', 'Region 2']}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_slug(self):
        params = {'slug': ['region-1', 'region-2']}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_description(self):
        params = {'description': ['foobar1', 'foobar2']}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_parent(self):
        regions = Region.objects.filter(parent__isnull=True)[:2]
        params = {'parent_id': [regions[0].pk, regions[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 4)
        params = {'parent': [regions[0].slug, regions[1].slug]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 4)

    def test_ancestor(self):
        regions = Region.objects.filter(parent__isnull=True)[:2]
        params = {'ancestor_id': [regions[0].pk, regions[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 8)
        params = {'ancestor': [regions[0].slug, regions[1].slug]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 8)


class SiteGroupTestCase(TestCase, ChangeLoggedFilterSetTests):
    queryset = SiteGroup.objects.all()
    filterset = SiteGroupFilterSet

    @classmethod
    def setUpTestData(cls):

        parent_groups = (
            SiteGroup(name='Site Group 1', slug='site-group-1', description='foobar1'),
            SiteGroup(name='Site Group 2', slug='site-group-2', description='foobar2'),
            SiteGroup(name='Site Group 3', slug='site-group-3', description='foobar3'),
        )
        for site_group in parent_groups:
            site_group.save()

        groups = (
            SiteGroup(name='Site Group 1A', slug='site-group-1a', parent=parent_groups[0]),
            SiteGroup(name='Site Group 1B', slug='site-group-1b', parent=parent_groups[0]),
            SiteGroup(name='Site Group 2A', slug='site-group-2a', parent=parent_groups[1]),
            SiteGroup(name='Site Group 2B', slug='site-group-2b', parent=parent_groups[1]),
            SiteGroup(name='Site Group 3A', slug='site-group-3a', parent=parent_groups[2]),
            SiteGroup(name='Site Group 3B', slug='site-group-3b', parent=parent_groups[2]),
        )
        for site_group in groups:
            site_group.save()

        child_groups = (
            SiteGroup(name='Site Group 1A1', slug='site-group-1a1', parent=groups[0]),
            SiteGroup(name='Site Group 1B1', slug='site-group-1b1', parent=groups[1]),
            SiteGroup(name='Site Group 2A1', slug='site-group-2a1', parent=groups[2]),
            SiteGroup(name='Site Group 2B1', slug='site-group-2b1', parent=groups[3]),
            SiteGroup(name='Site Group 3A1', slug='site-group-3a1', parent=groups[4]),
            SiteGroup(name='Site Group 3B1', slug='site-group-3b1', parent=groups[5]),
        )
        for site_group in child_groups:
            site_group.save()

    def test_q(self):
        params = {'q': 'foobar1'}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_name(self):
        params = {'name': ['Site Group 1', 'Site Group 2']}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_slug(self):
        params = {'slug': ['site-group-1', 'site-group-2']}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_description(self):
        params = {'description': ['foobar1', 'foobar2']}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_parent(self):
        site_groups = SiteGroup.objects.filter(parent__isnull=True)[:2]
        params = {'parent_id': [site_groups[0].pk, site_groups[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 4)
        params = {'parent': [site_groups[0].slug, site_groups[1].slug]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 4)

    def test_ancestor(self):
        site_groups = SiteGroup.objects.filter(parent__isnull=True)[:2]
        params = {'ancestor_id': [site_groups[0].pk, site_groups[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 8)
        params = {'ancestor': [site_groups[0].slug, site_groups[1].slug]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 8)


class SiteTestCase(TestCase, ChangeLoggedFilterSetTests):
    queryset = Site.objects.all()
    filterset = SiteFilterSet
    ignore_fields = ('physical_address', 'shipping_address')

    @classmethod
    def setUpTestData(cls):

        regions = (
            Region(name='Region 1', slug='region-1'),
            Region(name='Region 2', slug='region-2'),
            Region(name='Region 3', slug='region-3'),
        )
        for region in regions:
            region.save()

        groups = (
            SiteGroup(name='Site Group 1', slug='site-group-1'),
            SiteGroup(name='Site Group 2', slug='site-group-2'),
            SiteGroup(name='Site Group 3', slug='site-group-3'),
        )
        for group in groups:
            group.save()

        tenant_groups = (
            TenantGroup(name='Tenant group 1', slug='tenant-group-1'),
            TenantGroup(name='Tenant group 2', slug='tenant-group-2'),
            TenantGroup(name='Tenant group 3', slug='tenant-group-3'),
        )
        for tenantgroup in tenant_groups:
            tenantgroup.save()

        tenants = (
            Tenant(name='Tenant 1', slug='tenant-1', group=tenant_groups[0]),
            Tenant(name='Tenant 2', slug='tenant-2', group=tenant_groups[1]),
            Tenant(name='Tenant 3', slug='tenant-3', group=tenant_groups[2]),
        )
        Tenant.objects.bulk_create(tenants)

        rir = RIR.objects.create(name='RFC 6996', is_private=True)
        asns = (
            ASN(asn=64512, rir=rir, tenant=tenants[0]),
            ASN(asn=64513, rir=rir, tenant=tenants[0]),
            ASN(asn=64514, rir=rir, tenant=tenants[0]),
        )
        ASN.objects.bulk_create(asns)

        sites = (
            Site(name='Site 1', slug='site-1', region=regions[0], group=groups[0], tenant=tenants[0], status=SiteStatusChoices.STATUS_ACTIVE, facility='Facility 1', latitude=10, longitude=10, description='foobar1'),
            Site(name='Site 2', slug='site-2', region=regions[1], group=groups[1], tenant=tenants[1], status=SiteStatusChoices.STATUS_PLANNED, facility='Facility 2', latitude=20, longitude=20, description='foobar2'),
            Site(name='Site 3', slug='site-3', region=regions[2], group=groups[2], tenant=tenants[2], status=SiteStatusChoices.STATUS_RETIRED, facility='Facility 3', latitude=30, longitude=30),
        )
        Site.objects.bulk_create(sites)
        sites[0].asns.set([asns[0]])
        sites[1].asns.set([asns[1]])
        sites[2].asns.set([asns[2]])

    def test_q(self):
        params = {'q': 'foobar1'}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_name(self):
        params = {'name': ['Site 1', 'Site 2']}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_slug(self):
        params = {'slug': ['site-1', 'site-2']}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_facility(self):
        params = {'facility': ['Facility 1', 'Facility 2']}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_asn(self):
        params = {'asn': ['64512', '64513']}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_asn_id(self):
        asns = ASN.objects.all()[:2]
        params = {'asn_id': [asns[0].pk, asns[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_latitude(self):
        params = {'latitude': [10, 20]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_longitude(self):
        params = {'longitude': [10, 20]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_description(self):
        params = {'description': ['foobar1', 'foobar2']}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_status(self):
        params = {'status': [SiteStatusChoices.STATUS_ACTIVE, SiteStatusChoices.STATUS_PLANNED]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_region(self):
        regions = Region.objects.all()[:2]
        params = {'region_id': [regions[0].pk, regions[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {'region': [regions[0].slug, regions[1].slug]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_site_group(self):
        groups = SiteGroup.objects.all()[:2]
        params = {'group_id': [groups[0].pk, groups[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {'group': [groups[0].slug, groups[1].slug]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_tenant(self):
        tenants = Tenant.objects.all()[:2]
        params = {'tenant_id': [tenants[0].pk, tenants[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {'tenant': [tenants[0].slug, tenants[1].slug]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_tenant_group(self):
        tenant_groups = TenantGroup.objects.all()[:2]
        params = {'tenant_group_id': [tenant_groups[0].pk, tenant_groups[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {'tenant_group': [tenant_groups[0].slug, tenant_groups[1].slug]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)


class LocationTestCase(TestCase, ChangeLoggedFilterSetTests):
    queryset = Location.objects.all()
    filterset = LocationFilterSet

    @classmethod
    def setUpTestData(cls):

        regions = (
            Region(name='Region 1', slug='region-1'),
            Region(name='Region 2', slug='region-2'),
            Region(name='Region 3', slug='region-3'),
        )
        for region in regions:
            region.save()

        groups = (
            SiteGroup(name='Site Group 1', slug='site-group-1'),
            SiteGroup(name='Site Group 2', slug='site-group-2'),
            SiteGroup(name='Site Group 3', slug='site-group-3'),
        )
        for group in groups:
            group.save()

        sites = (
            Site(name='Site 1', slug='site-1', region=regions[0], group=groups[0]),
            Site(name='Site 2', slug='site-2', region=regions[1], group=groups[1]),
            Site(name='Site 3', slug='site-3', region=regions[2], group=groups[2]),
        )
        Site.objects.bulk_create(sites)

        parent_locations = (
            Location(name='Location 1', slug='location-1', site=sites[0]),
            Location(name='Location 2', slug='location-2', site=sites[1]),
            Location(name='Location 3', slug='location-3', site=sites[2]),
        )
        for location in parent_locations:
            location.save()

        locations = (
            Location(name='Location 1A', slug='location-1a', site=sites[0], parent=parent_locations[0], status=LocationStatusChoices.STATUS_PLANNED, facility='Facility 1', description='foobar1'),
            Location(name='Location 2A', slug='location-2a', site=sites[1], parent=parent_locations[1], status=LocationStatusChoices.STATUS_STAGING, facility='Facility 2', description='foobar2'),
            Location(name='Location 3A', slug='location-3a', site=sites[2], parent=parent_locations[2], status=LocationStatusChoices.STATUS_DECOMMISSIONING, facility='Facility 3', description='foobar3'),
        )
        for location in locations:
            location.save()

        child_locations = (
            Location(name='Location 1A1', slug='location-1a1', site=sites[0], parent=locations[0]),
            Location(name='Location 2A1', slug='location-2a1', site=sites[1], parent=locations[1]),
            Location(name='Location 3A1', slug='location-3a1', site=sites[2], parent=locations[2]),
        )
        for location in child_locations:
            location.save()

    def test_q(self):
        params = {'q': 'foobar1'}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_name(self):
        params = {'name': ['Location 1', 'Location 2']}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_slug(self):
        params = {'slug': ['location-1', 'location-2']}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_status(self):
        params = {'status': [LocationStatusChoices.STATUS_PLANNED, LocationStatusChoices.STATUS_STAGING]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_facility(self):
        params = {'facility': ['Facility 1', 'Facility 2']}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_description(self):
        params = {'description': ['foobar1', 'foobar2']}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_region(self):
        regions = Region.objects.all()[:2]
        params = {'region_id': [regions[0].pk, regions[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 6)
        params = {'region': [regions[0].slug, regions[1].slug]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 6)

    def test_site_group(self):
        site_groups = SiteGroup.objects.all()[:2]
        params = {'site_group_id': [site_groups[0].pk, site_groups[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 6)
        params = {'site_group': [site_groups[0].slug, site_groups[1].slug]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 6)

    def test_site(self):
        sites = Site.objects.all()[:2]
        params = {'site_id': [sites[0].pk, sites[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 6)
        params = {'site': [sites[0].slug, sites[1].slug]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 6)

    def test_parent(self):
        locations = Location.objects.filter(parent__isnull=True)[:2]
        params = {'parent_id': [locations[0].pk, locations[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {'parent': [locations[0].slug, locations[1].slug]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_ancestor(self):
        locations = Location.objects.filter(parent__isnull=True)[:2]
        params = {'ancestor_id': [locations[0].pk, locations[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 4)
        params = {'ancestor': [locations[0].slug, locations[1].slug]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 4)


class RackRoleTestCase(TestCase, ChangeLoggedFilterSetTests):
    queryset = RackRole.objects.all()
    filterset = RackRoleFilterSet

    @classmethod
    def setUpTestData(cls):

        rack_roles = (
            RackRole(name='Rack Role 1', slug='rack-role-1', color='ff0000', description='foobar1'),
            RackRole(name='Rack Role 2', slug='rack-role-2', color='00ff00', description='foobar2'),
            RackRole(name='Rack Role 3', slug='rack-role-3', color='0000ff'),
        )
        RackRole.objects.bulk_create(rack_roles)

    def test_q(self):
        params = {'q': 'foobar1'}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_name(self):
        params = {'name': ['Rack Role 1', 'Rack Role 2']}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_slug(self):
        params = {'slug': ['rack-role-1', 'rack-role-2']}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_color(self):
        params = {'color': ['ff0000', '00ff00']}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_description(self):
        params = {'description': ['foobar1', 'foobar2']}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)


class RackTypeTestCase(TestCase, ChangeLoggedFilterSetTests):
    queryset = RackType.objects.all()
    filterset = RackTypeFilterSet

    @classmethod
    def setUpTestData(cls):
        manufacturers = (
            Manufacturer(name='Manufacturer 1', slug='manufacturer-1'),
            Manufacturer(name='Manufacturer 2', slug='manufacturer-2'),
            Manufacturer(name='Manufacturer 3', slug='manufacturer-3'),
        )
        Manufacturer.objects.bulk_create(manufacturers)

        racks = (
            RackType(
                manufacturer=manufacturers[0],
                model='RackType 1',
                slug='rack-type-1',
                form_factor=RackFormFactorChoices.TYPE_2POST,
                width=RackWidthChoices.WIDTH_19IN,
                u_height=42,
                starting_unit=1,
                desc_units=False,
                outer_width=100,
                outer_depth=100,
                outer_unit=RackDimensionUnitChoices.UNIT_MILLIMETER,
                mounting_depth=100,
                weight=10,
                max_weight=1000,
                weight_unit=WeightUnitChoices.UNIT_POUND,
                description='foobar1',
            ),
            RackType(
                manufacturer=manufacturers[1],
                model='RackType 2',
                slug='rack-type-2',
                form_factor=RackFormFactorChoices.TYPE_4POST,
                width=RackWidthChoices.WIDTH_21IN,
                u_height=43,
                starting_unit=2,
                desc_units=False,
                outer_width=200,
                outer_depth=200,
                outer_unit=RackDimensionUnitChoices.UNIT_MILLIMETER,
                mounting_depth=200,
                weight=20,
                max_weight=2000,
                weight_unit=WeightUnitChoices.UNIT_POUND,
                description='foobar2',
            ),
            RackType(
                manufacturer=manufacturers[2],
                model='RackType 3',
                slug='rack-type-3',
                form_factor=RackFormFactorChoices.TYPE_CABINET,
                width=RackWidthChoices.WIDTH_23IN,
                u_height=44,
                starting_unit=3,
                desc_units=True,
                outer_width=300,
                outer_depth=300,
                outer_unit=RackDimensionUnitChoices.UNIT_INCH,
                mounting_depth=300,
                weight=30,
                max_weight=3000,
                weight_unit=WeightUnitChoices.UNIT_KILOGRAM,
                description='foobar3'
            ),
        )
        RackType.objects.bulk_create(racks)

    def test_q(self):
        params = {'q': 'foobar1'}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_manufacturer(self):
        manufacturers = Manufacturer.objects.all()[:2]
        params = {'manufacturer_id': [manufacturers[0].pk, manufacturers[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {'manufacturer': [manufacturers[0].slug, manufacturers[1].slug]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_model(self):
        params = {'model': ['RackType 1', 'RackType 2']}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_slug(self):
        params = {'slug': ['rack-type-1', 'rack-type-2']}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_description(self):
        params = {'description': ['foobar1', 'foobar2']}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_form_factor(self):
        params = {'form_factor': [RackFormFactorChoices.TYPE_2POST, RackFormFactorChoices.TYPE_4POST]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_width(self):
        params = {'width': [RackWidthChoices.WIDTH_19IN, RackWidthChoices.WIDTH_21IN]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_u_height(self):
        params = {'u_height': [42, 43]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_starting_unit(self):
        params = {'starting_unit': [1, 2]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_desc_units(self):
        params = {'desc_units': 'true'}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)
        params = {'desc_units': 'false'}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_outer_width(self):
        params = {'outer_width': [100, 200]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_outer_depth(self):
        params = {'outer_depth': [100, 200]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_outer_unit(self):
        self.assertEqual(RackType.objects.filter(outer_unit__isnull=False).count(), 3)
        params = {'outer_unit': RackDimensionUnitChoices.UNIT_MILLIMETER}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_mounting_depth(self):
        params = {'mounting_depth': [100, 200]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_weight(self):
        params = {'weight': [10, 20]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_max_weight(self):
        params = {'max_weight': [1000, 2000]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_weight_unit(self):
        params = {'weight_unit': WeightUnitChoices.UNIT_POUND}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)


class RackTestCase(TestCase, ChangeLoggedFilterSetTests):
    queryset = Rack.objects.all()
    filterset = RackFilterSet
    ignore_fields = ('units',)

    @classmethod
    def setUpTestData(cls):

        regions = (
            Region(name='Region 1', slug='region-1'),
            Region(name='Region 2', slug='region-2'),
            Region(name='Region 3', slug='region-3'),
        )
        for region in regions:
            region.save()

        groups = (
            SiteGroup(name='Site Group 1', slug='site-group-1'),
            SiteGroup(name='Site Group 2', slug='site-group-2'),
            SiteGroup(name='Site Group 3', slug='site-group-3'),
        )
        for group in groups:
            group.save()

        sites = (
            Site(name='Site 1', slug='site-1', region=regions[0], group=groups[0]),
            Site(name='Site 2', slug='site-2', region=regions[1], group=groups[1]),
            Site(name='Site 3', slug='site-3', region=regions[2], group=groups[2]),
        )
        Site.objects.bulk_create(sites)

        locations = (
            Location(name='Location 1', slug='location-1', site=sites[0]),
            Location(name='Location 2', slug='location-2', site=sites[1]),
            Location(name='Location 3', slug='location-3', site=sites[2]),
        )
        for location in locations:
            location.save()

        manufacturers = (
            Manufacturer(name='Manufacturer 1', slug='manufacturer-1'),
            Manufacturer(name='Manufacturer 2', slug='manufacturer-2'),
            Manufacturer(name='Manufacturer 3', slug='manufacturer-3'),
        )
        Manufacturer.objects.bulk_create(manufacturers)

        rack_types = (
            RackType(
                manufacturer=manufacturers[0],
                model='RackType 1',
                slug='rack-type-1',
                form_factor=RackFormFactorChoices.TYPE_2POST,
                width=RackWidthChoices.WIDTH_19IN,
                u_height=42,
                starting_unit=1,
                desc_units=False,
                outer_width=100,
                outer_depth=100,
                outer_unit=RackDimensionUnitChoices.UNIT_MILLIMETER,
                mounting_depth=100,
                weight=10,
                max_weight=1000,
                weight_unit=WeightUnitChoices.UNIT_POUND,
                description='foobar1'
            ),
            RackType(
                manufacturer=manufacturers[1],
                model='RackType 2',
                slug='rack-type-2',
                form_factor=RackFormFactorChoices.TYPE_4POST,
                width=RackWidthChoices.WIDTH_21IN,
                u_height=43,
                starting_unit=2,
                desc_units=False,
                outer_width=200,
                outer_depth=200,
                outer_unit=RackDimensionUnitChoices.UNIT_MILLIMETER,
                mounting_depth=200,
                weight=20,
                max_weight=2000,
                weight_unit=WeightUnitChoices.UNIT_POUND,
                description='foobar2'
            ),
        )
        RackType.objects.bulk_create(rack_types)

        rack_roles = (
            RackRole(name='Rack Role 1', slug='rack-role-1'),
            RackRole(name='Rack Role 2', slug='rack-role-2'),
            RackRole(name='Rack Role 3', slug='rack-role-3'),
        )
        RackRole.objects.bulk_create(rack_roles)

        tenant_groups = (
            TenantGroup(name='Tenant group 1', slug='tenant-group-1'),
            TenantGroup(name='Tenant group 2', slug='tenant-group-2'),
            TenantGroup(name='Tenant group 3', slug='tenant-group-3'),
        )
        for tenantgroup in tenant_groups:
            tenantgroup.save()

        tenants = (
            Tenant(name='Tenant 1', slug='tenant-1', group=tenant_groups[0]),
            Tenant(name='Tenant 2', slug='tenant-2', group=tenant_groups[1]),
            Tenant(name='Tenant 3', slug='tenant-3', group=tenant_groups[2]),
        )
        Tenant.objects.bulk_create(tenants)

        racks = (
            Rack(
                name='Rack 1',
                facility_id='rack-1',
                site=sites[0],
                location=locations[0],
                tenant=tenants[0],
                status=RackStatusChoices.STATUS_ACTIVE,
                role=rack_roles[0],
                serial='ABC',
                asset_tag='1001',
                form_factor=RackFormFactorChoices.TYPE_2POST,
                width=RackWidthChoices.WIDTH_19IN,
                u_height=42,
                desc_units=False,
                outer_width=100,
                outer_depth=100,
                outer_unit=RackDimensionUnitChoices.UNIT_MILLIMETER,
                weight=10,
                max_weight=1000,
                weight_unit=WeightUnitChoices.UNIT_POUND,
                description='foobar1',
                airflow=RackAirflowChoices.FRONT_TO_REAR
            ),
            Rack(
                name='Rack 2',
                facility_id='rack-2',
                site=sites[1],
                location=locations[1],
                tenant=tenants[1],
                status=RackStatusChoices.STATUS_PLANNED,
                role=rack_roles[1],
                serial='DEF',
                asset_tag='1002',
                form_factor=RackFormFactorChoices.TYPE_4POST,
                width=RackWidthChoices.WIDTH_21IN,
                u_height=43,
                desc_units=False,
                outer_width=200,
                outer_depth=200,
                outer_unit=RackDimensionUnitChoices.UNIT_MILLIMETER,
                weight=20,
                max_weight=2000,
                weight_unit=WeightUnitChoices.UNIT_POUND,
                description='foobar2',
                airflow=RackAirflowChoices.REAR_TO_FRONT
            ),
            Rack(
                name='Rack 3',
                facility_id='rack-3',
                site=sites[2],
                location=locations[2],
                tenant=tenants[2],
                status=RackStatusChoices.STATUS_RESERVED,
                role=rack_roles[2],
                serial='GHI',
                asset_tag='1003',
                form_factor=RackFormFactorChoices.TYPE_CABINET,
                width=RackWidthChoices.WIDTH_23IN,
                u_height=44,
                desc_units=True,
                outer_width=300,
                outer_depth=300,
                outer_unit=RackDimensionUnitChoices.UNIT_INCH,
                weight=30,
                max_weight=3000,
                weight_unit=WeightUnitChoices.UNIT_KILOGRAM,
                description='foobar3'
            ),
            Rack(
                name='Rack 4',
                facility_id='rack-4',
                site=sites[2],
                location=locations[2],
                tenant=tenants[2],
                status=RackStatusChoices.STATUS_PLANNED,
                role=rack_roles[2],
                rack_type=rack_types[0],
                description='foobar4'
            ),
            Rack(
                name='Rack 5',
                facility_id='rack-5',
                site=sites[2],
                location=locations[2],
                tenant=tenants[2],
                status=RackStatusChoices.STATUS_PLANNED,
                role=rack_roles[2],
                rack_type=rack_types[1],
                description='foobar5'
            ),
        )
        Rack.objects.bulk_create(racks)

    def test_q(self):
        params = {'q': 'foobar1'}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_name(self):
        params = {'name': ['Rack 1', 'Rack 2']}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_facility_id(self):
        params = {'facility_id': ['rack-1', 'rack-2']}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_asset_tag(self):
        params = {'asset_tag': ['1001', '1002']}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_description(self):
        params = {'description': ['foobar1', 'foobar2']}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_form_factor(self):
        params = {'form_factor': [RackFormFactorChoices.TYPE_2POST, RackFormFactorChoices.TYPE_4POST]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_width(self):
        params = {'width': [RackWidthChoices.WIDTH_19IN, RackWidthChoices.WIDTH_21IN]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 4)

    def test_u_height(self):
        params = {'u_height': [42, 43]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 4)

    def test_starting_unit(self):
        params = {'starting_unit': [1]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 5)
        params = {'starting_unit': [2]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 0)

    def test_desc_units(self):
        params = {'desc_units': 'true'}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)
        params = {'desc_units': 'false'}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 4)

    def test_outer_width(self):
        params = {'outer_width': [100, 200]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_outer_depth(self):
        params = {'outer_depth': [100, 200]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_outer_unit(self):
        params = {'outer_unit': RackDimensionUnitChoices.UNIT_MILLIMETER}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_region(self):
        regions = Region.objects.all()[:2]
        params = {'region_id': [regions[0].pk, regions[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {'region': [regions[0].slug, regions[1].slug]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_site_group(self):
        site_groups = SiteGroup.objects.all()[:2]
        params = {'site_group_id': [site_groups[0].pk, site_groups[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {'site_group': [site_groups[0].slug, site_groups[1].slug]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_site(self):
        sites = Site.objects.all()[:2]
        params = {'site_id': [sites[0].pk, sites[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {'site': [sites[0].slug, sites[1].slug]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_location(self):
        locations = Location.objects.all()[:2]
        params = {'location_id': [locations[0].pk, locations[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {'location': [locations[0].slug, locations[1].slug]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_status(self):
        params = {'status': [RackStatusChoices.STATUS_ACTIVE, RackStatusChoices.STATUS_PLANNED]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 4)

    def test_role(self):
        roles = RackRole.objects.all()[:2]
        params = {'role_id': [roles[0].pk, roles[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {'role': [roles[0].slug, roles[1].slug]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_serial(self):
        params = {'serial': ['ABC', 'DEF']}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {'serial': ['abc', 'def']}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_tenant(self):
        tenants = Tenant.objects.all()[:2]
        params = {'tenant_id': [tenants[0].pk, tenants[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {'tenant': [tenants[0].slug, tenants[1].slug]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_tenant_group(self):
        tenant_groups = TenantGroup.objects.all()[:2]
        params = {'tenant_group_id': [tenant_groups[0].pk, tenant_groups[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {'tenant_group': [tenant_groups[0].slug, tenant_groups[1].slug]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_weight(self):
        params = {'weight': [10, 20]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_max_weight(self):
        params = {'max_weight': [1000, 2000]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_weight_unit(self):
        params = {'weight_unit': WeightUnitChoices.UNIT_POUND}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_manufacturer(self):
        manufacturers = Manufacturer.objects.all()[:2]
        params = {'manufacturer_id': [manufacturers[0].pk, manufacturers[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {'manufacturer': [manufacturers[0].slug, manufacturers[1].slug]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_rack_type(self):
        rack_types = RackType.objects.all()[:2]
        params = {'rack_type_id': [rack_types[0].pk, rack_types[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {'rack_type': [rack_types[0].slug, rack_types[1].slug]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_airflow(self):
        params = {'airflow': RackAirflowChoices.FRONT_TO_REAR}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)


class RackReservationTestCase(TestCase, ChangeLoggedFilterSetTests):
    queryset = RackReservation.objects.all()
    filterset = RackReservationFilterSet
    ignore_fields = ('units',)

    @classmethod
    def setUpTestData(cls):

        regions = (
            Region(name='Region 1', slug='region-1'),
            Region(name='Region 2', slug='region-2'),
            Region(name='Region 3', slug='region-3'),
        )
        for region in regions:
            region.save()

        groups = (
            SiteGroup(name='Site Group 1', slug='site-group-1'),
            SiteGroup(name='Site Group 2', slug='site-group-2'),
            SiteGroup(name='Site Group 3', slug='site-group-3'),
        )
        for group in groups:
            group.save()

        sites = (
            Site(name='Site 1', slug='site-1', region=regions[0], group=groups[0]),
            Site(name='Site 2', slug='site-2', region=regions[1], group=groups[1]),
            Site(name='Site 3', slug='site-3', region=regions[2], group=groups[2]),
        )
        Site.objects.bulk_create(sites)

        locations = (
            Location(name='Location 1', slug='location-1', site=sites[0]),
            Location(name='Location 2', slug='location-2', site=sites[1]),
            Location(name='Location 3', slug='location-3', site=sites[2]),
        )
        for location in locations:
            location.save()

        racks = (
            Rack(name='Rack 1', site=sites[0], location=locations[0]),
            Rack(name='Rack 2', site=sites[1], location=locations[1]),
            Rack(name='Rack 3', site=sites[2], location=locations[2]),
        )
        Rack.objects.bulk_create(racks)

        users = (
            User(username='User 1'),
            User(username='User 2'),
            User(username='User 3'),
        )
        User.objects.bulk_create(users)

        tenant_groups = (
            TenantGroup(name='Tenant group 1', slug='tenant-group-1'),
            TenantGroup(name='Tenant group 2', slug='tenant-group-2'),
            TenantGroup(name='Tenant group 3', slug='tenant-group-3'),
        )
        for tenantgroup in tenant_groups:
            tenantgroup.save()

        tenants = (
            Tenant(name='Tenant 1', slug='tenant-1', group=tenant_groups[0]),
            Tenant(name='Tenant 2', slug='tenant-2', group=tenant_groups[1]),
            Tenant(name='Tenant 3', slug='tenant-3', group=tenant_groups[2]),
        )
        Tenant.objects.bulk_create(tenants)

        reservations = (
            RackReservation(rack=racks[0], units=[1, 2, 3], user=users[0], tenant=tenants[0], description='foobar1'),
            RackReservation(rack=racks[1], units=[4, 5, 6], user=users[1], tenant=tenants[1], description='foobar2'),
            RackReservation(rack=racks[2], units=[7, 8, 9], user=users[2], tenant=tenants[2], description='foobar3'),
        )
        RackReservation.objects.bulk_create(reservations)

    def test_q(self):
        params = {'q': 'foobar1'}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_region(self):
        regions = Region.objects.all()[:2]
        params = {'region_id': [regions[0].pk, regions[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {'region': [regions[0].slug, regions[1].slug]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_site_group(self):
        site_groups = SiteGroup.objects.all()[:2]
        params = {'site_group_id': [site_groups[0].pk, site_groups[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {'site_group': [site_groups[0].slug, site_groups[1].slug]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_site(self):
        sites = Site.objects.all()[:2]
        params = {'site_id': [sites[0].pk, sites[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {'site': [sites[0].slug, sites[1].slug]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_location(self):
        locations = Location.objects.all()[:2]
        params = {'location_id': [locations[0].pk, locations[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {'location': [locations[0].slug, locations[1].slug]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_user(self):
        users = User.objects.all()[:2]
        params = {'user_id': [users[0].pk, users[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {'user': [users[0].username, users[1].username]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_tenant(self):
        tenants = Tenant.objects.all()[:2]
        params = {'tenant_id': [tenants[0].pk, tenants[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {'tenant': [tenants[0].slug, tenants[1].slug]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_description(self):
        params = {'description': ['foobar1', 'foobar2']}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_tenant_group(self):
        tenant_groups = TenantGroup.objects.all()[:2]
        params = {'tenant_group_id': [tenant_groups[0].pk, tenant_groups[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {'tenant_group': [tenant_groups[0].slug, tenant_groups[1].slug]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)


class ManufacturerTestCase(TestCase, ChangeLoggedFilterSetTests):
    queryset = Manufacturer.objects.all()
    filterset = ManufacturerFilterSet

    @classmethod
    def setUpTestData(cls):

        manufacturers = (
            Manufacturer(name='Manufacturer 1', slug='manufacturer-1', description='foobar1'),
            Manufacturer(name='Manufacturer 2', slug='manufacturer-2', description='foobar2'),
            Manufacturer(name='Manufacturer 3', slug='manufacturer-3', description='foobar3'),
        )
        Manufacturer.objects.bulk_create(manufacturers)

    def test_q(self):
        params = {'q': 'foobar1'}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_name(self):
        params = {'name': ['Manufacturer 1', 'Manufacturer 2']}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_slug(self):
        params = {'slug': ['manufacturer-1', 'manufacturer-2']}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_description(self):
        params = {'description': ['foobar1', 'foobar2']}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)


class DeviceTypeTestCase(TestCase, ChangeLoggedFilterSetTests):
    queryset = DeviceType.objects.all()
    filterset = DeviceTypeFilterSet
    ignore_fields = ('front_image', 'rear_image')

    @classmethod
    def setUpTestData(cls):

        manufacturers = (
            Manufacturer(name='Manufacturer 1', slug='manufacturer-1'),
            Manufacturer(name='Manufacturer 2', slug='manufacturer-2'),
            Manufacturer(name='Manufacturer 3', slug='manufacturer-3'),
        )
        Manufacturer.objects.bulk_create(manufacturers)

        platforms = (
            Platform(name='Platform 1', slug='platform-1', manufacturer=manufacturers[0]),
            Platform(name='Platform 2', slug='platform-2', manufacturer=manufacturers[1]),
            Platform(name='Platform 3', slug='platform-3', manufacturer=manufacturers[2]),
        )
        Platform.objects.bulk_create(platforms)

        device_types = (
            DeviceType(
                manufacturer=manufacturers[0],
                default_platform=platforms[0],
                model='Model 1',
                slug='model-1',
                part_number='Part Number 1',
                u_height=1,
                is_full_depth=True,
                front_image='front.png',
                rear_image='rear.png',
                weight=10,
                weight_unit=WeightUnitChoices.UNIT_POUND,
                description='foobar1'
            ),
            DeviceType(
                manufacturer=manufacturers[1],
                default_platform=platforms[1],
                model='Model 2',
                slug='model-2',
                part_number='Part Number 2',
                u_height=2,
                is_full_depth=True,
                subdevice_role=SubdeviceRoleChoices.ROLE_PARENT,
                airflow=DeviceAirflowChoices.AIRFLOW_FRONT_TO_REAR,
                weight=20,
                weight_unit=WeightUnitChoices.UNIT_POUND,
                description='foobar2'
            ),
            DeviceType(
                manufacturer=manufacturers[2],
                model='Model 3',
                slug='model-3',
                part_number='Part Number 3',
                u_height=3,
                is_full_depth=False,
                subdevice_role=SubdeviceRoleChoices.ROLE_CHILD,
                airflow=DeviceAirflowChoices.AIRFLOW_REAR_TO_FRONT,
                weight=30,
                weight_unit=WeightUnitChoices.UNIT_KILOGRAM,
                description='foobar3'
            ),
        )
        DeviceType.objects.bulk_create(device_types)

        # Add component templates for filtering
        ConsolePortTemplate.objects.bulk_create((
            ConsolePortTemplate(device_type=device_types[0], name='Console Port 1'),
            ConsolePortTemplate(device_type=device_types[1], name='Console Port 2'),
        ))
        ConsoleServerPortTemplate.objects.bulk_create((
            ConsoleServerPortTemplate(device_type=device_types[0], name='Console Server Port 1'),
            ConsoleServerPortTemplate(device_type=device_types[1], name='Console Server Port 2'),
        ))
        PowerPortTemplate.objects.bulk_create((
            PowerPortTemplate(device_type=device_types[0], name='Power Port 1'),
            PowerPortTemplate(device_type=device_types[1], name='Power Port 2'),
        ))
        PowerOutletTemplate.objects.bulk_create((
            PowerOutletTemplate(device_type=device_types[0], name='Power Outlet 1'),
            PowerOutletTemplate(device_type=device_types[1], name='Power Outlet 2'),
        ))
        InterfaceTemplate.objects.bulk_create((
            InterfaceTemplate(device_type=device_types[0], name='Interface 1'),
            InterfaceTemplate(device_type=device_types[1], name='Interface 2'),
        ))
        rear_ports = (
            RearPortTemplate(device_type=device_types[0], name='Rear Port 1', type=PortTypeChoices.TYPE_8P8C),
            RearPortTemplate(device_type=device_types[1], name='Rear Port 2', type=PortTypeChoices.TYPE_8P8C),
        )
        RearPortTemplate.objects.bulk_create(rear_ports)
        FrontPortTemplate.objects.bulk_create((
            FrontPortTemplate(device_type=device_types[0], name='Front Port 1', type=PortTypeChoices.TYPE_8P8C, rear_port=rear_ports[0]),
            FrontPortTemplate(device_type=device_types[1], name='Front Port 2', type=PortTypeChoices.TYPE_8P8C, rear_port=rear_ports[1]),
        ))
        ModuleBayTemplate.objects.bulk_create((
            ModuleBayTemplate(device_type=device_types[0], name='Module Bay 1'),
            ModuleBayTemplate(device_type=device_types[1], name='Module Bay 2'),
        ))
        DeviceBayTemplate.objects.bulk_create((
            DeviceBayTemplate(device_type=device_types[0], name='Device Bay 1'),
            DeviceBayTemplate(device_type=device_types[1], name='Device Bay 2'),
        ))
        # Assigned DeviceType must have parent subdevice_role
        inventory_item = InventoryItemTemplate(device_type=device_types[1], name='Inventory Item 1')
        inventory_item.save()

    def test_q(self):
        params = {'q': 'foobar1'}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_model(self):
        params = {'model': ['Model 1', 'Model 2']}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_slug(self):
        params = {'slug': ['model-1', 'model-2']}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_part_number(self):
        params = {'part_number': ['Part Number 1', 'Part Number 2']}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_description(self):
        params = {'description': ['foobar1', 'foobar2']}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_u_height(self):
        params = {'u_height': [1, 2]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_is_full_depth(self):
        params = {'is_full_depth': True}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {'is_full_depth': False}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_subdevice_role(self):
        params = {'subdevice_role': SubdeviceRoleChoices.ROLE_PARENT}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_airflow(self):
        params = {'airflow': DeviceAirflowChoices.AIRFLOW_FRONT_TO_REAR}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_manufacturer(self):
        manufacturers = Manufacturer.objects.all()[:2]
        params = {'manufacturer_id': [manufacturers[0].pk, manufacturers[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {'manufacturer': [manufacturers[0].slug, manufacturers[1].slug]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_default_platform(self):
        platforms = Platform.objects.all()[:2]
        params = {'default_platform_id': [platforms[0].pk, platforms[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {'default_platform': [platforms[0].slug, platforms[1].slug]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_has_front_image(self):
        params = {'has_front_image': True}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)
        params = {'has_front_image': False}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_has_rear_image(self):
        params = {'has_rear_image': True}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)
        params = {'has_rear_image': False}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_console_ports(self):
        params = {'console_ports': 'true'}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {'console_ports': 'false'}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_console_server_ports(self):
        params = {'console_server_ports': 'true'}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {'console_server_ports': 'false'}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_power_ports(self):
        params = {'power_ports': 'true'}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {'power_ports': 'false'}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_power_outlets(self):
        params = {'power_outlets': 'true'}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {'power_outlets': 'false'}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_interfaces(self):
        params = {'interfaces': 'true'}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {'interfaces': 'false'}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_pass_through_ports(self):
        params = {'pass_through_ports': 'true'}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {'pass_through_ports': 'false'}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_device_bays(self):
        params = {'device_bays': 'true'}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {'device_bays': 'false'}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_module_bays(self):
        params = {'module_bays': 'true'}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {'module_bays': 'false'}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_inventory_items(self):
        params = {'inventory_items': 'true'}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)
        params = {'inventory_items': 'false'}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_weight(self):
        params = {'weight': [10, 20]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_weight_unit(self):
        params = {'weight_unit': WeightUnitChoices.UNIT_POUND}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)


class ModuleTypeTestCase(TestCase, ChangeLoggedFilterSetTests):
    queryset = ModuleType.objects.all()
    filterset = ModuleTypeFilterSet

    @classmethod
    def setUpTestData(cls):

        manufacturers = (
            Manufacturer(name='Manufacturer 1', slug='manufacturer-1'),
            Manufacturer(name='Manufacturer 2', slug='manufacturer-2'),
            Manufacturer(name='Manufacturer 3', slug='manufacturer-3'),
        )
        Manufacturer.objects.bulk_create(manufacturers)

        module_types = (
            ModuleType(
                manufacturer=manufacturers[0],
                model='Model 1',
                part_number='Part Number 1',
                weight=10,
                weight_unit=WeightUnitChoices.UNIT_POUND,
                description='foobar1',
                airflow=ModuleAirflowChoices.FRONT_TO_REAR
            ),
            ModuleType(
                manufacturer=manufacturers[1],
                model='Model 2',
                part_number='Part Number 2',
                weight=20,
                weight_unit=WeightUnitChoices.UNIT_POUND,
                description='foobar2',
                airflow=ModuleAirflowChoices.REAR_TO_FRONT
            ),
            ModuleType(
                manufacturer=manufacturers[2],
                model='Model 3',
                part_number='Part Number 3',
                weight=30,
                weight_unit=WeightUnitChoices.UNIT_KILOGRAM,
                description='foobar3'
            ),
        )
        ModuleType.objects.bulk_create(module_types)

        # Add component templates for filtering
        ConsolePortTemplate.objects.bulk_create((
            ConsolePortTemplate(module_type=module_types[0], name='Console Port 1'),
            ConsolePortTemplate(module_type=module_types[1], name='Console Port 2'),
        ))
        ConsoleServerPortTemplate.objects.bulk_create((
            ConsoleServerPortTemplate(module_type=module_types[0], name='Console Server Port 1'),
            ConsoleServerPortTemplate(module_type=module_types[1], name='Console Server Port 2'),
        ))
        PowerPortTemplate.objects.bulk_create((
            PowerPortTemplate(module_type=module_types[0], name='Power Port 1'),
            PowerPortTemplate(module_type=module_types[1], name='Power Port 2'),
        ))
        PowerOutletTemplate.objects.bulk_create((
            PowerOutletTemplate(module_type=module_types[0], name='Power Outlet 1'),
            PowerOutletTemplate(module_type=module_types[1], name='Power Outlet 2'),
        ))
        InterfaceTemplate.objects.bulk_create((
            InterfaceTemplate(module_type=module_types[0], name='Interface 1'),
            InterfaceTemplate(module_type=module_types[1], name='Interface 2'),
        ))
        rear_ports = (
            RearPortTemplate(module_type=module_types[0], name='Rear Port 1', type=PortTypeChoices.TYPE_8P8C),
            RearPortTemplate(module_type=module_types[1], name='Rear Port 2', type=PortTypeChoices.TYPE_8P8C),
        )
        RearPortTemplate.objects.bulk_create(rear_ports)
        FrontPortTemplate.objects.bulk_create((
            FrontPortTemplate(module_type=module_types[0], name='Front Port 1', type=PortTypeChoices.TYPE_8P8C, rear_port=rear_ports[0]),
            FrontPortTemplate(module_type=module_types[1], name='Front Port 2', type=PortTypeChoices.TYPE_8P8C, rear_port=rear_ports[1]),
        ))

    def test_q(self):
        params = {'q': 'foobar1'}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_model(self):
        params = {'model': ['Model 1', 'Model 2']}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_part_number(self):
        params = {'part_number': ['Part Number 1', 'Part Number 2']}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_description(self):
        params = {'description': ['foobar1', 'foobar2']}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_manufacturer(self):
        manufacturers = Manufacturer.objects.all()[:2]
        params = {'manufacturer_id': [manufacturers[0].pk, manufacturers[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {'manufacturer': [manufacturers[0].slug, manufacturers[1].slug]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_console_ports(self):
        params = {'console_ports': 'true'}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {'console_ports': 'false'}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_console_server_ports(self):
        params = {'console_server_ports': 'true'}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {'console_server_ports': 'false'}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_power_ports(self):
        params = {'power_ports': 'true'}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {'power_ports': 'false'}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_power_outlets(self):
        params = {'power_outlets': 'true'}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {'power_outlets': 'false'}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_interfaces(self):
        params = {'interfaces': 'true'}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {'interfaces': 'false'}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_pass_through_ports(self):
        params = {'pass_through_ports': 'true'}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {'pass_through_ports': 'false'}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_weight(self):
        params = {'weight': [10, 20]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_weight_unit(self):
        params = {'weight_unit': WeightUnitChoices.UNIT_POUND}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_airflow(self):
        params = {'airflow': RackAirflowChoices.FRONT_TO_REAR}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)


class ConsolePortTemplateTestCase(TestCase, DeviceComponentTemplateFilterSetTests, ChangeLoggedFilterSetTests):
    queryset = ConsolePortTemplate.objects.all()
    filterset = ConsolePortTemplateFilterSet

    @classmethod
    def setUpTestData(cls):

        manufacturer = Manufacturer.objects.create(name='Manufacturer 1', slug='manufacturer-1')

        device_types = (
            DeviceType(manufacturer=manufacturer, model='Model 1', slug='model-1'),
            DeviceType(manufacturer=manufacturer, model='Model 2', slug='model-2'),
            DeviceType(manufacturer=manufacturer, model='Model 3', slug='model-3'),
        )
        DeviceType.objects.bulk_create(device_types)

        ConsolePortTemplate.objects.bulk_create((
            ConsolePortTemplate(device_type=device_types[0], name='Console Port 1', description='foobar1'),
            ConsolePortTemplate(device_type=device_types[1], name='Console Port 2', description='foobar2'),
            ConsolePortTemplate(device_type=device_types[2], name='Console Port 3', description='foobar3'),
        ))

    def test_name(self):
        params = {'name': ['Console Port 1', 'Console Port 2']}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)


class ConsoleServerPortTemplateTestCase(TestCase, DeviceComponentTemplateFilterSetTests, ChangeLoggedFilterSetTests):
    queryset = ConsoleServerPortTemplate.objects.all()
    filterset = ConsoleServerPortTemplateFilterSet

    @classmethod
    def setUpTestData(cls):

        manufacturer = Manufacturer.objects.create(name='Manufacturer 1', slug='manufacturer-1')

        device_types = (
            DeviceType(manufacturer=manufacturer, model='Model 1', slug='model-1'),
            DeviceType(manufacturer=manufacturer, model='Model 2', slug='model-2'),
            DeviceType(manufacturer=manufacturer, model='Model 3', slug='model-3'),
        )
        DeviceType.objects.bulk_create(device_types)

        ConsoleServerPortTemplate.objects.bulk_create((
            ConsoleServerPortTemplate(device_type=device_types[0], name='Console Server Port 1', description='foobar1'),
            ConsoleServerPortTemplate(device_type=device_types[1], name='Console Server Port 2', description='foobar2'),
            ConsoleServerPortTemplate(device_type=device_types[2], name='Console Server Port 3', description='foobar3'),
        ))

    def test_name(self):
        params = {'name': ['Console Server Port 1', 'Console Server Port 2']}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)


class PowerPortTemplateTestCase(TestCase, DeviceComponentTemplateFilterSetTests, ChangeLoggedFilterSetTests):
    queryset = PowerPortTemplate.objects.all()
    filterset = PowerPortTemplateFilterSet

    @classmethod
    def setUpTestData(cls):

        manufacturer = Manufacturer.objects.create(name='Manufacturer 1', slug='manufacturer-1')

        device_types = (
            DeviceType(manufacturer=manufacturer, model='Model 1', slug='model-1'),
            DeviceType(manufacturer=manufacturer, model='Model 2', slug='model-2'),
            DeviceType(manufacturer=manufacturer, model='Model 3', slug='model-3'),
        )
        DeviceType.objects.bulk_create(device_types)

        PowerPortTemplate.objects.bulk_create((
            PowerPortTemplate(
                device_type=device_types[0],
                name='Power Port 1',
                maximum_draw=100,
                allocated_draw=50,
                description='foobar1'
            ),
            PowerPortTemplate(
                device_type=device_types[1],
                name='Power Port 2',
                maximum_draw=200,
                allocated_draw=100,
                description='foobar2'
            ),
            PowerPortTemplate(
                device_type=device_types[2],
                name='Power Port 3',
                maximum_draw=300,
                allocated_draw=150,
                description='foobar3'
            ),
        ))

    def test_name(self):
        params = {'name': ['Power Port 1', 'Power Port 2']}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_maximum_draw(self):
        params = {'maximum_draw': [100, 200]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_allocated_draw(self):
        params = {'allocated_draw': [50, 100]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)


class PowerOutletTemplateTestCase(TestCase, DeviceComponentTemplateFilterSetTests, ChangeLoggedFilterSetTests):
    queryset = PowerOutletTemplate.objects.all()
    filterset = PowerOutletTemplateFilterSet

    @classmethod
    def setUpTestData(cls):

        manufacturer = Manufacturer.objects.create(name='Manufacturer 1', slug='manufacturer-1')

        device_types = (
            DeviceType(manufacturer=manufacturer, model='Model 1', slug='model-1'),
            DeviceType(manufacturer=manufacturer, model='Model 2', slug='model-2'),
            DeviceType(manufacturer=manufacturer, model='Model 3', slug='model-3'),
        )
        DeviceType.objects.bulk_create(device_types)

        PowerOutletTemplate.objects.bulk_create((
            PowerOutletTemplate(
                device_type=device_types[0],
                name='Power Outlet 1',
                feed_leg=PowerOutletFeedLegChoices.FEED_LEG_A,
                description='foobar1'
            ),
            PowerOutletTemplate(
                device_type=device_types[1],
                name='Power Outlet 2',
                feed_leg=PowerOutletFeedLegChoices.FEED_LEG_B,
                description='foobar2'
            ),
            PowerOutletTemplate(
                device_type=device_types[2],
                name='Power Outlet 3',
                feed_leg=PowerOutletFeedLegChoices.FEED_LEG_C,
                description='foobar3'
            ),
        ))

    def test_name(self):
        params = {'name': ['Power Outlet 1', 'Power Outlet 2']}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_feed_leg(self):
        params = {'feed_leg': [PowerOutletFeedLegChoices.FEED_LEG_A, PowerOutletFeedLegChoices.FEED_LEG_B]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)


class InterfaceTemplateTestCase(TestCase, DeviceComponentTemplateFilterSetTests, ChangeLoggedFilterSetTests):
    queryset = InterfaceTemplate.objects.all()
    filterset = InterfaceTemplateFilterSet

    @classmethod
    def setUpTestData(cls):

        manufacturer = Manufacturer.objects.create(name='Manufacturer 1', slug='manufacturer-1')

        device_types = (
            DeviceType(manufacturer=manufacturer, model='Model 1', slug='model-1'),
            DeviceType(manufacturer=manufacturer, model='Model 2', slug='model-2'),
            DeviceType(manufacturer=manufacturer, model='Model 3', slug='model-3'),
        )
        DeviceType.objects.bulk_create(device_types)

        interface_templates = (
            InterfaceTemplate(
                device_type=device_types[0],
                name='Interface 1',
                type=InterfaceTypeChoices.TYPE_1GE_FIXED,
                enabled=True,
                mgmt_only=True,
                poe_mode=InterfacePoEModeChoices.MODE_PD,
                poe_type=InterfacePoETypeChoices.TYPE_1_8023AF,
                description='foobar1'
            ),
            InterfaceTemplate(
                device_type=device_types[1],
                name='Interface 2',
                type=InterfaceTypeChoices.TYPE_1GE_GBIC,
                enabled=False,
                mgmt_only=False,
                poe_mode=InterfacePoEModeChoices.MODE_PSE,
                poe_type=InterfacePoETypeChoices.TYPE_2_8023AT,
                description='foobar2'
            ),
            InterfaceTemplate(
                device_type=device_types[2],
                name='Interface 3',
                type=InterfaceTypeChoices.TYPE_1GE_SFP,
                mgmt_only=False,
                description='foobar3'
            ),
        )
        InterfaceTemplate.objects.bulk_create(interface_templates)
        interface_templates[0].bridge = interface_templates[1]
        interface_templates[1].bridge = interface_templates[0]
        InterfaceTemplate.objects.bulk_update(interface_templates, ['bridge'])

    def test_name(self):
        params = {'name': ['Interface 1', 'Interface 2']}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_type(self):
        params = {'type': [InterfaceTypeChoices.TYPE_1GE_FIXED, InterfaceTypeChoices.TYPE_1GE_GBIC]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_enabled(self):
        params = {'enabled': 'true'}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {'enabled': 'false'}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_mgmt_only(self):
        params = {'mgmt_only': 'true'}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)
        params = {'mgmt_only': 'false'}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_bridge(self):
        params = {'bridge_id': [InterfaceTemplate.objects.filter(bridge__isnull=False).first().bridge_id]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_poe_mode(self):
        params = {'poe_mode': [InterfacePoEModeChoices.MODE_PD, InterfacePoEModeChoices.MODE_PSE]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_poe_type(self):
        params = {'poe_type': [InterfacePoETypeChoices.TYPE_1_8023AF, InterfacePoETypeChoices.TYPE_2_8023AT]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)


class FrontPortTemplateTestCase(TestCase, DeviceComponentTemplateFilterSetTests, ChangeLoggedFilterSetTests):
    queryset = FrontPortTemplate.objects.all()
    filterset = FrontPortTemplateFilterSet

    @classmethod
    def setUpTestData(cls):

        manufacturer = Manufacturer.objects.create(name='Manufacturer 1', slug='manufacturer-1')

        device_types = (
            DeviceType(manufacturer=manufacturer, model='Model 1', slug='model-1'),
            DeviceType(manufacturer=manufacturer, model='Model 2', slug='model-2'),
            DeviceType(manufacturer=manufacturer, model='Model 3', slug='model-3'),
        )
        DeviceType.objects.bulk_create(device_types)

        rear_ports = (
            RearPortTemplate(device_type=device_types[0], name='Rear Port 1', type=PortTypeChoices.TYPE_8P8C),
            RearPortTemplate(device_type=device_types[1], name='Rear Port 2', type=PortTypeChoices.TYPE_8P8C),
            RearPortTemplate(device_type=device_types[2], name='Rear Port 3', type=PortTypeChoices.TYPE_8P8C),
        )
        RearPortTemplate.objects.bulk_create(rear_ports)

        FrontPortTemplate.objects.bulk_create((
            FrontPortTemplate(
                device_type=device_types[0],
                name='Front Port 1',
                rear_port=rear_ports[0],
                type=PortTypeChoices.TYPE_8P8C,
                color=ColorChoices.COLOR_RED,
                description='foobar1'
            ),
            FrontPortTemplate(
                device_type=device_types[1],
                name='Front Port 2',
                rear_port=rear_ports[1],
                type=PortTypeChoices.TYPE_110_PUNCH,
                color=ColorChoices.COLOR_GREEN,
                description='foobar2'
            ),
            FrontPortTemplate(
                device_type=device_types[2],
                name='Front Port 3',
                rear_port=rear_ports[2],
                type=PortTypeChoices.TYPE_BNC,
                color=ColorChoices.COLOR_BLUE,
                description='foobar3'
            ),
        ))

    def test_name(self):
        params = {'name': ['Front Port 1', 'Front Port 2']}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_type(self):
        params = {'type': [PortTypeChoices.TYPE_8P8C, PortTypeChoices.TYPE_110_PUNCH]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_color(self):
        params = {'color': [ColorChoices.COLOR_RED, ColorChoices.COLOR_GREEN]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)


class RearPortTemplateTestCase(TestCase, DeviceComponentTemplateFilterSetTests, ChangeLoggedFilterSetTests):
    queryset = RearPortTemplate.objects.all()
    filterset = RearPortTemplateFilterSet

    @classmethod
    def setUpTestData(cls):

        manufacturer = Manufacturer.objects.create(name='Manufacturer 1', slug='manufacturer-1')

        device_types = (
            DeviceType(manufacturer=manufacturer, model='Model 1', slug='model-1'),
            DeviceType(manufacturer=manufacturer, model='Model 2', slug='model-2'),
            DeviceType(manufacturer=manufacturer, model='Model 3', slug='model-3'),
        )
        DeviceType.objects.bulk_create(device_types)

        RearPortTemplate.objects.bulk_create((
            RearPortTemplate(
                device_type=device_types[0],
                name='Rear Port 1',
                type=PortTypeChoices.TYPE_8P8C,
                color=ColorChoices.COLOR_RED,
                positions=1,
                description='foobar1'
            ),
            RearPortTemplate(
                device_type=device_types[1],
                name='Rear Port 2',
                type=PortTypeChoices.TYPE_110_PUNCH,
                color=ColorChoices.COLOR_GREEN,
                positions=2,
                description='foobar2'
            ),
            RearPortTemplate(
                device_type=device_types[2],
                name='Rear Port 3',
                type=PortTypeChoices.TYPE_BNC,
                color=ColorChoices.COLOR_BLUE,
                positions=3,
                description='foobar3'
            ),
        ))

    def test_name(self):
        params = {'name': ['Rear Port 1', 'Rear Port 2']}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_type(self):
        params = {'type': [PortTypeChoices.TYPE_8P8C, PortTypeChoices.TYPE_110_PUNCH]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_color(self):
        params = {'color': [ColorChoices.COLOR_RED, ColorChoices.COLOR_GREEN]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_positions(self):
        params = {'positions': [1, 2]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)


class ModuleBayTemplateTestCase(TestCase, DeviceComponentTemplateFilterSetTests, ChangeLoggedFilterSetTests):
    queryset = ModuleBayTemplate.objects.all()
    filterset = ModuleBayTemplateFilterSet

    @classmethod
    def setUpTestData(cls):

        manufacturer = Manufacturer.objects.create(name='Manufacturer 1', slug='manufacturer-1')

        device_types = (
            DeviceType(manufacturer=manufacturer, model='Model 1', slug='model-1'),
            DeviceType(manufacturer=manufacturer, model='Model 2', slug='model-2'),
            DeviceType(manufacturer=manufacturer, model='Model 3', slug='model-3'),
        )
        DeviceType.objects.bulk_create(device_types)

        module_types = (
            ModuleType(manufacturer=manufacturer, model='Module Type 1'),
            ModuleType(manufacturer=manufacturer, model='Module Type 2'),
        )
        ModuleType.objects.bulk_create(module_types)

        ModuleBayTemplate.objects.bulk_create((
            ModuleBayTemplate(device_type=device_types[0], name='Module Bay 1', description='foobar1'),
            ModuleBayTemplate(device_type=device_types[1], name='Module Bay 2', description='foobar2', module_type=module_types[0]),
            ModuleBayTemplate(device_type=device_types[2], name='Module Bay 3', description='foobar3', module_type=module_types[1]),
        ))

    def test_name(self):
        params = {'name': ['Module Bay 1', 'Module Bay 2']}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_module_type(self):
        module_types = ModuleType.objects.all()[:2]
        params = {'module_type_id': [module_types[0].pk, module_types[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)


class DeviceBayTemplateTestCase(TestCase, DeviceComponentTemplateFilterSetTests, ChangeLoggedFilterSetTests):
    queryset = DeviceBayTemplate.objects.all()
    filterset = DeviceBayTemplateFilterSet

    @classmethod
    def setUpTestData(cls):

        manufacturer = Manufacturer.objects.create(name='Manufacturer 1', slug='manufacturer-1')

        device_types = (
            DeviceType(manufacturer=manufacturer, model='Model 1', slug='model-1'),
            DeviceType(manufacturer=manufacturer, model='Model 2', slug='model-2'),
            DeviceType(manufacturer=manufacturer, model='Model 3', slug='model-3'),
        )
        DeviceType.objects.bulk_create(device_types)

        DeviceBayTemplate.objects.bulk_create((
            DeviceBayTemplate(device_type=device_types[0], name='Device Bay 1', description='foobar1'),
            DeviceBayTemplate(device_type=device_types[1], name='Device Bay 2', description='foobar2'),
            DeviceBayTemplate(device_type=device_types[2], name='Device Bay 3', description='foobar3'),
        ))

    def test_name(self):
        params = {'name': ['Device Bay 1', 'Device Bay 2']}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)


class InventoryItemTemplateTestCase(TestCase, DeviceComponentTemplateFilterSetTests, ChangeLoggedFilterSetTests):
    queryset = InventoryItemTemplate.objects.all()
    filterset = InventoryItemTemplateFilterSet

    @classmethod
    def setUpTestData(cls):
        manufacturers = (
            Manufacturer(name='Manufacturer 1', slug='manufacturer-1'),
            Manufacturer(name='Manufacturer 2', slug='manufacturer-2'),
            Manufacturer(name='Manufacturer 3', slug='manufacturer-3'),
        )
        Manufacturer.objects.bulk_create(manufacturers)

        device_types = (
            DeviceType(manufacturer=manufacturers[0], model='Model 1', slug='model-1'),
            DeviceType(manufacturer=manufacturers[0], model='Model 2', slug='model-2'),
            DeviceType(manufacturer=manufacturers[0], model='Model 3', slug='model-3'),
        )
        DeviceType.objects.bulk_create(device_types)

        inventory_item_roles = (
            InventoryItemRole(name='Inventory Item Role 1', slug='inventory-item-role-1'),
            InventoryItemRole(name='Inventory Item Role 2', slug='inventory-item-role-2'),
            InventoryItemRole(name='Inventory Item Role 3', slug='inventory-item-role-3'),
        )
        InventoryItemRole.objects.bulk_create(inventory_item_roles)

        inventory_item_templates = (
            InventoryItemTemplate(
                device_type=device_types[0],
                name='Inventory Item 1',
                label='A',
                role=inventory_item_roles[0],
                manufacturer=manufacturers[0],
                part_id='1001',
                description='foobar1'
            ),
            InventoryItemTemplate(
                device_type=device_types[1],
                name='Inventory Item 2',
                label='B',
                role=inventory_item_roles[1],
                manufacturer=manufacturers[1],
                part_id='1002',
                description='foobar2'
            ),
            InventoryItemTemplate(
                device_type=device_types[2],
                name='Inventory Item 3',
                label='C',
                role=inventory_item_roles[2],
                manufacturer=manufacturers[2],
                part_id='1003',
                description='foobar3'
            ),
        )
        for item in inventory_item_templates:
            item.save()

        child_inventory_item_templates = (
            InventoryItemTemplate(device_type=device_types[0], name='Inventory Item 1A', parent=inventory_item_templates[0]),
            InventoryItemTemplate(device_type=device_types[1], name='Inventory Item 2A', parent=inventory_item_templates[1]),
            InventoryItemTemplate(device_type=device_types[2], name='Inventory Item 3A', parent=inventory_item_templates[2]),
        )
        for item in child_inventory_item_templates:
            item.save()

    def test_name(self):
        params = {'name': ['Inventory Item 1', 'Inventory Item 2']}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_device_type_id(self):
        device_types = DeviceType.objects.all()[:2]
        params = {'device_type_id': [device_types[0].pk, device_types[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 4)

    def test_label(self):
        params = {'label': ['A', 'B']}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_part_id(self):
        params = {'part_id': ['1001', '1002']}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_parent_id(self):
        parent_items = InventoryItemTemplate.objects.filter(parent__isnull=True)[:2]
        params = {'parent_id': [parent_items[0].pk, parent_items[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_role(self):
        roles = InventoryItemRole.objects.all()[:2]
        params = {'role_id': [roles[0].pk, roles[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {'role': [roles[0].slug, roles[1].slug]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_manufacturer(self):
        manufacturers = Manufacturer.objects.all()[:2]
        params = {'manufacturer_id': [manufacturers[0].pk, manufacturers[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {'manufacturer': [manufacturers[0].slug, manufacturers[1].slug]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)


class DeviceRoleTestCase(TestCase, ChangeLoggedFilterSetTests):
    queryset = DeviceRole.objects.all()
    filterset = DeviceRoleFilterSet

    @classmethod
    def setUpTestData(cls):

        roles = (
            DeviceRole(name='Device Role 1', slug='device-role-1', color='ff0000', vm_role=True, description='foobar1'),
            DeviceRole(name='Device Role 2', slug='device-role-2', color='00ff00', vm_role=True, description='foobar2'),
            DeviceRole(name='Device Role 3', slug='device-role-3', color='0000ff', vm_role=False),
        )
        DeviceRole.objects.bulk_create(roles)

    def test_q(self):
        params = {'q': 'foobar1'}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_name(self):
        params = {'name': ['Device Role 1', 'Device Role 2']}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_slug(self):
        params = {'slug': ['device-role-1', 'device-role-2']}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_color(self):
        params = {'color': ['ff0000', '00ff00']}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_vm_role(self):
        params = {'vm_role': 'true'}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {'vm_role': 'false'}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_description(self):
        params = {'description': ['foobar1', 'foobar2']}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)


class PlatformTestCase(TestCase, ChangeLoggedFilterSetTests):
    queryset = Platform.objects.all()
    filterset = PlatformFilterSet

    @classmethod
    def setUpTestData(cls):

        manufacturers = (
            Manufacturer(name='Manufacturer 1', slug='manufacturer-1'),
            Manufacturer(name='Manufacturer 2', slug='manufacturer-2'),
            Manufacturer(name='Manufacturer 3', slug='manufacturer-3'),
        )
        Manufacturer.objects.bulk_create(manufacturers)

        platforms = (
            Platform(name='Platform 1', slug='platform-1', manufacturer=manufacturers[0], description='foobar1'),
            Platform(name='Platform 2', slug='platform-2', manufacturer=manufacturers[1], description='foobar2'),
            Platform(name='Platform 3', slug='platform-3', manufacturer=manufacturers[2], description='foobar3'),
            Platform(name='Platform 4', slug='platform-4'),
        )
        Platform.objects.bulk_create(platforms)

    def test_q(self):
        params = {'q': 'foobar1'}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_name(self):
        params = {'name': ['Platform 1', 'Platform 2']}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_slug(self):
        params = {'slug': ['platform-1', 'platform-2']}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_description(self):
        params = {'description': ['foobar1', 'foobar2']}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_manufacturer(self):
        manufacturers = Manufacturer.objects.all()[:2]
        params = {'manufacturer_id': [manufacturers[0].pk, manufacturers[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {'manufacturer': [manufacturers[0].slug, manufacturers[1].slug]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_available_for_device_type(self):
        manufacturers = Manufacturer.objects.all()[:2]
        device_type = DeviceType.objects.create(
            manufacturer=manufacturers[0],
            model='Device Type 1',
            slug='device-type-1',
            u_height=1
        )
        params = {'available_for_device_type': device_type.pk}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)


class DeviceTestCase(TestCase, ChangeLoggedFilterSetTests):
    queryset = Device.objects.all()
    filterset = DeviceFilterSet
    ignore_fields = ('local_context_data', 'oob_ip', 'primary_ip4', 'primary_ip6', 'vc_master_for')

    @classmethod
    def setUpTestData(cls):

        manufacturers = (
            Manufacturer(name='Manufacturer 1', slug='manufacturer-1'),
            Manufacturer(name='Manufacturer 2', slug='manufacturer-2'),
            Manufacturer(name='Manufacturer 3', slug='manufacturer-3'),
        )
        Manufacturer.objects.bulk_create(manufacturers)

        device_types = (
            DeviceType(manufacturer=manufacturers[0], model='Model 1', slug='model-1', is_full_depth=True),
            DeviceType(manufacturer=manufacturers[1], model='Model 2', slug='model-2', is_full_depth=True),
            DeviceType(manufacturer=manufacturers[2], model='Model 3', slug='model-3', is_full_depth=False),
        )
        DeviceType.objects.bulk_create(device_types)

        roles = (
            DeviceRole(name='Device Role 1', slug='device-role-1'),
            DeviceRole(name='Device Role 2', slug='device-role-2'),
            DeviceRole(name='Device Role 3', slug='device-role-3'),
        )
        DeviceRole.objects.bulk_create(roles)

        platforms = (
            Platform(name='Platform 1', slug='platform-1'),
            Platform(name='Platform 2', slug='platform-2'),
            Platform(name='Platform 3', slug='platform-3'),
        )
        Platform.objects.bulk_create(platforms)

        regions = (
            Region(name='Region 1', slug='region-1'),
            Region(name='Region 2', slug='region-2'),
            Region(name='Region 3', slug='region-3'),
        )
        for region in regions:
            region.save()

        groups = (
            SiteGroup(name='Site Group 1', slug='site-group-1'),
            SiteGroup(name='Site Group 2', slug='site-group-2'),
            SiteGroup(name='Site Group 3', slug='site-group-3'),
        )
        for group in groups:
            group.save()

        sites = (
            Site(name='Site 1', slug='site-1', region=regions[0], group=groups[0]),
            Site(name='Site 2', slug='site-2', region=regions[1], group=groups[1]),
            Site(name='Site 3', slug='site-3', region=regions[2], group=groups[2]),
        )
        Site.objects.bulk_create(sites)

        locations = (
            Location(name='Location 1', slug='location-1', site=sites[0]),
            Location(name='Location 2', slug='location-2', site=sites[1]),
            Location(name='Location 3', slug='location-3', site=sites[2]),
        )
        for location in locations:
            location.save()

        racks = (
            Rack(name='Rack 1', site=sites[0], location=locations[0]),
            Rack(name='Rack 2', site=sites[1], location=locations[1]),
            Rack(name='Rack 3', site=sites[2], location=locations[2]),
        )
        Rack.objects.bulk_create(racks)

        cluster_type = ClusterType.objects.create(name='Cluster Type 1', slug='cluster-type-1')
        cluster_groups = (
            ClusterGroup(name='Cluster Group 1', slug='cluster-group-1'),
            ClusterGroup(name='Cluster Group 2', slug='cluster-group-2'),
            ClusterGroup(name='Cluster Group 3', slug='cluster-group-3'),
        )
        ClusterGroup.objects.bulk_create(cluster_groups)
        clusters = (
            Cluster(name='Cluster 1', type=cluster_type, group=cluster_groups[0]),
            Cluster(name='Cluster 2', type=cluster_type, group=cluster_groups[1]),
            Cluster(name='Cluster 3', type=cluster_type, group=cluster_groups[2]),
        )
        Cluster.objects.bulk_create(clusters)

        tenant_groups = (
            TenantGroup(name='Tenant group 1', slug='tenant-group-1'),
            TenantGroup(name='Tenant group 2', slug='tenant-group-2'),
            TenantGroup(name='Tenant group 3', slug='tenant-group-3'),
        )
        for tenantgroup in tenant_groups:
            tenantgroup.save()

        tenants = (
            Tenant(name='Tenant 1', slug='tenant-1', group=tenant_groups[0]),
            Tenant(name='Tenant 2', slug='tenant-2', group=tenant_groups[1]),
            Tenant(name='Tenant 3', slug='tenant-3', group=tenant_groups[2]),
        )
        Tenant.objects.bulk_create(tenants)

        devices = (
            Device(
                name='Device 1',
                device_type=device_types[0],
                role=roles[0],
                platform=platforms[0],
                tenant=tenants[0],
                serial='ABC',
                asset_tag='1001',
                site=sites[0],
                location=locations[0],
                rack=racks[0],
                position=1,
                face=DeviceFaceChoices.FACE_FRONT,
                latitude=10,
                longitude=10,
                status=DeviceStatusChoices.STATUS_ACTIVE,
                cluster=clusters[0],
                local_context_data={"foo": 123},
                description='foobar1'
            ),
            Device(
                name='Device 2',
                device_type=device_types[1],
                role=roles[1],
                platform=platforms[1],
                tenant=tenants[1],
                serial='DEF',
                asset_tag='1002',
                site=sites[1],
                location=locations[1],
                rack=racks[1],
                position=2,
                face=DeviceFaceChoices.FACE_FRONT,
                latitude=20,
                longitude=20,
                status=DeviceStatusChoices.STATUS_STAGED,
                airflow=DeviceAirflowChoices.AIRFLOW_FRONT_TO_REAR,
                cluster=clusters[1],
                description='foobar2'
            ),
            Device(
                name='Device 3',
                device_type=device_types[2],
                role=roles[2],
                platform=platforms[2],
                tenant=tenants[2],
                serial='GHI',
                asset_tag='1003',
                site=sites[2],
                location=locations[2],
                rack=racks[2],
                position=3,
                face=DeviceFaceChoices.FACE_REAR,
                latitude=30,
                longitude=30,
                status=DeviceStatusChoices.STATUS_FAILED,
                airflow=DeviceAirflowChoices.AIRFLOW_REAR_TO_FRONT,
                cluster=clusters[2],
                description='foobar3'
            ),
        )
        Device.objects.bulk_create(devices)

        # Add components for filtering
        ConsolePort.objects.bulk_create((
            ConsolePort(device=devices[0], name='Console Port 1'),
            ConsolePort(device=devices[1], name='Console Port 2'),
        ))
        ConsoleServerPort.objects.bulk_create((
            ConsoleServerPort(device=devices[0], name='Console Server Port 1'),
            ConsoleServerPort(device=devices[1], name='Console Server Port 2'),
        ))
        PowerPort.objects.bulk_create((
            PowerPort(device=devices[0], name='Power Port 1'),
            PowerPort(device=devices[1], name='Power Port 2'),
        ))
        PowerOutlet.objects.bulk_create((
            PowerOutlet(device=devices[0], name='Power Outlet 1'),
            PowerOutlet(device=devices[1], name='Power Outlet 2'),
        ))
        interfaces = (
            Interface(device=devices[0], name='Interface 1'),
            Interface(device=devices[1], name='Interface 2'),
        )
        Interface.objects.bulk_create(interfaces)
        mac_addresses = (
            MACAddress(mac_address='00-00-00-00-00-01'),
            MACAddress(mac_address='00-00-00-00-00-02'),
        )
        MACAddress.objects.bulk_create(mac_addresses)
        interfaces[0].mac_addresses.set([mac_addresses[0]])
        interfaces[1].mac_addresses.set([mac_addresses[1]])
        rear_ports = (
            RearPort(device=devices[0], name='Rear Port 1', type=PortTypeChoices.TYPE_8P8C),
            RearPort(device=devices[1], name='Rear Port 2', type=PortTypeChoices.TYPE_8P8C),
        )
        RearPort.objects.bulk_create(rear_ports)
        FrontPort.objects.bulk_create((
            FrontPort(device=devices[0], name='Front Port 1', type=PortTypeChoices.TYPE_8P8C, rear_port=rear_ports[0]),
            FrontPort(device=devices[1], name='Front Port 2', type=PortTypeChoices.TYPE_8P8C, rear_port=rear_ports[1]),
        ))
        ModuleBay.objects.create(device=devices[0], name='Module Bay 1')
        ModuleBay.objects.create(device=devices[1], name='Module Bay 2')
        DeviceBay.objects.bulk_create((
            DeviceBay(device=devices[0], name='Device Bay 1'),
            DeviceBay(device=devices[1], name='Device Bay 2'),
        ))

        # Assign primary IPs for filtering
        ipaddresses = (
            IPAddress(address='192.0.2.1/24', assigned_object=interfaces[0]),
            IPAddress(address='192.0.2.2/24', assigned_object=interfaces[1]),
            IPAddress(address='192.0.2.3/24', assigned_object=None),
            IPAddress(address='2001:db8::1/64', assigned_object=interfaces[0]),
            IPAddress(address='2001:db8::2/64', assigned_object=interfaces[1]),
            IPAddress(address='2001:db8::3/64', assigned_object=None),
        )
        IPAddress.objects.bulk_create(ipaddresses)
        Device.objects.filter(pk=devices[0].pk).update(primary_ip4=ipaddresses[0], primary_ip6=ipaddresses[3])
        Device.objects.filter(pk=devices[1].pk).update(primary_ip4=ipaddresses[1], primary_ip6=ipaddresses[4])

        # VirtualChassis assignment for filtering
        virtual_chassis = VirtualChassis.objects.create(master=devices[0])
        Device.objects.filter(pk=devices[0].pk).update(virtual_chassis=virtual_chassis, vc_position=1, vc_priority=1)
        Device.objects.filter(pk=devices[1].pk).update(virtual_chassis=virtual_chassis, vc_position=2, vc_priority=2)

        # VirtualDeviceContext assignment for filtering
        VirtualDeviceContext.objects.create(device=devices[0], name="VDC 1", identifier=1, status='active')

    def test_q(self):
        params = {'q': 'foobar1'}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_name(self):
        params = {'name': ['Device 1', 'Device 2']}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        # Test case insensitivity
        params = {'name': ['DEVICE 1', 'DEVICE 2']}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_description(self):
        params = {'description': ['foobar1', 'foobar2']}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_asset_tag(self):
        params = {'asset_tag': ['1001', '1002']}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_face(self):
        params = {'face': DeviceFaceChoices.FACE_FRONT}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_position(self):
        params = {'position': [1, 2]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_latitude(self):
        params = {'latitude': [10, 20]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_longitude(self):
        params = {'longitude': [10, 20]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_vc_position(self):
        params = {'vc_position': [1, 2]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_vc_priority(self):
        params = {'vc_priority': [1, 2]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_manufacturer(self):
        manufacturers = Manufacturer.objects.all()[:2]
        params = {'manufacturer_id': [manufacturers[0].pk, manufacturers[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {'manufacturer': [manufacturers[0].slug, manufacturers[1].slug]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_devicetype(self):
        device_types = DeviceType.objects.all()[:2]
        params = {'device_type_id': [device_types[0].pk, device_types[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {'device_type': [device_types[0].slug, device_types[1].slug]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_devicerole(self):
        roles = DeviceRole.objects.all()[:2]
        params = {'role_id': [roles[0].pk, roles[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {'role': [roles[0].slug, roles[1].slug]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_platform(self):
        platforms = Platform.objects.all()[:2]
        params = {'platform_id': [platforms[0].pk, platforms[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {'platform': [platforms[0].slug, platforms[1].slug]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_region(self):
        regions = Region.objects.all()[:2]
        params = {'region_id': [regions[0].pk, regions[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {'region': [regions[0].slug, regions[1].slug]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_site_group(self):
        site_groups = SiteGroup.objects.all()[:2]
        params = {'site_group_id': [site_groups[0].pk, site_groups[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {'site_group': [site_groups[0].slug, site_groups[1].slug]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_site(self):
        sites = Site.objects.all()[:2]
        params = {'site_id': [sites[0].pk, sites[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {'site': [sites[0].slug, sites[1].slug]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_location(self):
        locations = Location.objects.all()[:2]
        params = {'location_id': [locations[0].pk, locations[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_rack(self):
        racks = Rack.objects.all()[:2]
        params = {'rack_id': [racks[0].pk, racks[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_cluster(self):
        clusters = Cluster.objects.all()[:2]
        params = {'cluster_id': [clusters[0].pk, clusters[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_cluster_group(self):
        cluster_groups = ClusterGroup.objects.all()[:2]
        params = {'cluster_group_id': [cluster_groups[0].pk, cluster_groups[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {'cluster_group': [cluster_groups[0].slug, cluster_groups[1].slug]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_model(self):
        params = {'model': ['model-1', 'model-2']}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_status(self):
        params = {'status': [DeviceStatusChoices.STATUS_ACTIVE, DeviceStatusChoices.STATUS_STAGED]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_is_full_depth(self):
        params = {'is_full_depth': 'true'}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {'is_full_depth': 'false'}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_airflow(self):
        params = {'airflow': DeviceAirflowChoices.AIRFLOW_FRONT_TO_REAR}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_mac_address(self):
        params = {'mac_address': ['00-00-00-00-00-01', '00-00-00-00-00-02']}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_serial(self):
        params = {'serial': ['ABC', 'DEF']}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {'serial': ['abc', 'def']}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_has_primary_ip(self):
        params = {'has_primary_ip': 'true'}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {'has_primary_ip': 'false'}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_primary_ip4(self):
        addresses = IPAddress.objects.filter(address__family=4)
        params = {'primary_ip4_id': [addresses[0].pk, addresses[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {'primary_ip4_id': [addresses[2].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 0)

    def test_primary_ip6(self):
        addresses = IPAddress.objects.filter(address__family=6)
        params = {'primary_ip6_id': [addresses[0].pk, addresses[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {'primary_ip6_id': [addresses[2].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 0)

    def test_virtual_chassis_id(self):
        params = {'virtual_chassis_id': [VirtualChassis.objects.first().pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_virtual_chassis_member(self):
        params = {'virtual_chassis_member': 'true'}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {'virtual_chassis_member': 'false'}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_console_ports(self):
        params = {'console_ports': 'true'}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {'console_ports': 'false'}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_console_server_ports(self):
        params = {'console_server_ports': 'true'}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {'console_server_ports': 'false'}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_power_ports(self):
        params = {'power_ports': 'true'}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {'power_ports': 'false'}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_power_outlets(self):
        params = {'power_outlets': 'true'}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {'power_outlets': 'false'}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_interfaces(self):
        params = {'interfaces': 'true'}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {'interfaces': 'false'}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_pass_through_ports(self):
        params = {'pass_through_ports': 'true'}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {'pass_through_ports': 'false'}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_module_bays(self):
        params = {'module_bays': 'true'}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {'module_bays': 'false'}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_device_bays(self):
        params = {'device_bays': 'true'}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {'device_bays': 'false'}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_local_context_data(self):
        params = {'local_context_data': 'true'}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)
        params = {'local_context_data': 'false'}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_tenant(self):
        tenants = Tenant.objects.all()[:2]
        params = {'tenant_id': [tenants[0].pk, tenants[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {'tenant': [tenants[0].slug, tenants[1].slug]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_tenant_group(self):
        tenant_groups = TenantGroup.objects.all()[:2]
        params = {'tenant_group_id': [tenant_groups[0].pk, tenant_groups[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {'tenant_group': [tenant_groups[0].slug, tenant_groups[1].slug]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_has_virtual_device_context(self):
        params = {'has_virtual_device_context': 'true'}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)
        params = {'has_virtual_device_context': 'false'}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)


class ModuleTestCase(TestCase, ChangeLoggedFilterSetTests):
    queryset = Module.objects.all()
    filterset = ModuleFilterSet
    ignore_fields = ('local_context_data',)

    @classmethod
    def setUpTestData(cls):
        manufacturers = (
            Manufacturer(name='Manufacturer 1', slug='manufacturer-1'),
            Manufacturer(name='Manufacturer 2', slug='manufacturer-2'),
            Manufacturer(name='Manufacturer 3', slug='manufacturer-3'),
        )
        Manufacturer.objects.bulk_create(manufacturers)

        devices = (
            create_test_device('Test Device 1'),
            create_test_device('Test Device 2'),
            create_test_device('Test Device 3'),
        )

        module_types = (
            ModuleType(manufacturer=manufacturers[0], model='Module Type 1'),
            ModuleType(manufacturer=manufacturers[1], model='Module Type 2'),
            ModuleType(manufacturer=manufacturers[2], model='Module Type 3'),
        )
        ModuleType.objects.bulk_create(module_types)

        module_bays = (
            ModuleBay(device=devices[0], name='Module Bay 1'),
            ModuleBay(device=devices[0], name='Module Bay 2'),
            ModuleBay(device=devices[0], name='Module Bay 3'),
            ModuleBay(device=devices[1], name='Module Bay 1'),
            ModuleBay(device=devices[1], name='Module Bay 2'),
            ModuleBay(device=devices[1], name='Module Bay 3'),
            ModuleBay(device=devices[2], name='Module Bay 1'),
            ModuleBay(device=devices[2], name='Module Bay 2'),
            ModuleBay(device=devices[2], name='Module Bay 3'),
        )
        for module_bay in module_bays:
            module_bay.save()

        modules = (
            Module(
                device=devices[0],
                module_bay=module_bays[0],
                module_type=module_types[0],
                status=ModuleStatusChoices.STATUS_ACTIVE,
                serial='A',
                asset_tag='A',
                description='foobar1'
            ),
            Module(
                device=devices[0],
                module_bay=module_bays[1],
                module_type=module_types[1],
                status=ModuleStatusChoices.STATUS_ACTIVE,
                serial='B',
                asset_tag='B',
                description='foobar2'
            ),
            Module(
                device=devices[0],
                module_bay=module_bays[2],
                module_type=module_types[2],
                status=ModuleStatusChoices.STATUS_ACTIVE,
                serial='C',
                asset_tag='C',
                description='foobar3'
            ),
            Module(
                device=devices[1],
                module_bay=module_bays[3],
                module_type=module_types[0],
                status=ModuleStatusChoices.STATUS_ACTIVE,
                serial='D',
                asset_tag='D'
            ),
            Module(
                device=devices[1],
                module_bay=module_bays[4],
                module_type=module_types[1],
                status=ModuleStatusChoices.STATUS_ACTIVE,
                serial='E',
                asset_tag='E'
            ),
            Module(
                device=devices[1],
                module_bay=module_bays[5],
                module_type=module_types[2],
                status=ModuleStatusChoices.STATUS_ACTIVE,
                serial='F',
                asset_tag='F'
            ),
            Module(
                device=devices[2],
                module_bay=module_bays[6],
                module_type=module_types[0],
                status=ModuleStatusChoices.STATUS_ACTIVE,
                serial='G',
                asset_tag='G'
            ),
            Module(
                device=devices[2],
                module_bay=module_bays[7],
                module_type=module_types[1],
                status=ModuleStatusChoices.STATUS_PLANNED,
                serial='H',
                asset_tag='H'
            ),
            Module(
                device=devices[2],
                module_bay=module_bays[8],
                module_type=module_types[2],
                status=ModuleStatusChoices.STATUS_FAILED,
                serial='I',
                asset_tag='I'
            ),
        )
        Module.objects.bulk_create(modules)

    def test_q(self):
        params = {'q': 'foobar1'}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_manufacturer(self):
        manufacturers = Manufacturer.objects.all()[:2]
        params = {'manufacturer_id': [manufacturers[0].pk, manufacturers[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 6)
        params = {'manufacturer': [manufacturers[0].slug, manufacturers[1].slug]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 6)

    def test_module_type(self):
        module_types = ModuleType.objects.all()[:2]
        params = {'module_type_id': [module_types[0].pk, module_types[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 6)
        params = {'module_type': [module_types[0].model, module_types[1].model]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 6)

    def test_description(self):
        params = {'description': ['foobar1', 'foobar2']}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_module_bay(self):
        module_bays = ModuleBay.objects.all()[:2]
        params = {'module_bay_id': [module_bays[0].pk, module_bays[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_device(self):
        device_types = Device.objects.all()[:2]
        params = {'device_id': [device_types[0].pk, device_types[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 6)

    def test_status(self):
        params = {'status': [ModuleStatusChoices.STATUS_PLANNED, ModuleStatusChoices.STATUS_FAILED]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_serial(self):
        params = {'serial': ['A', 'B']}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {'serial': ['a', 'b']}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_asset_tag(self):
        params = {'asset_tag': ['A', 'B']}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)


class ConsolePortTestCase(TestCase, DeviceComponentFilterSetTests, ChangeLoggedFilterSetTests):
    queryset = ConsolePort.objects.all()
    filterset = ConsolePortFilterSet

    @classmethod
    def setUpTestData(cls):

        regions = (
            Region(name='Region 1', slug='region-1'),
            Region(name='Region 2', slug='region-2'),
            Region(name='Region 3', slug='region-3'),
        )
        for region in regions:
            region.save()

        groups = (
            SiteGroup(name='Site Group 1', slug='site-group-1'),
            SiteGroup(name='Site Group 2', slug='site-group-2'),
            SiteGroup(name='Site Group 3', slug='site-group-3'),
        )
        for group in groups:
            group.save()

        sites = Site.objects.bulk_create((
            Site(name='Site 1', slug='site-1', region=regions[0], group=groups[0]),
            Site(name='Site 2', slug='site-2', region=regions[1], group=groups[1]),
            Site(name='Site 3', slug='site-3', region=regions[2], group=groups[2]),
            Site(name='Site X', slug='site-x'),
        ))

        manufacturer = Manufacturer.objects.create(name='Manufacturer 1', slug='manufacturer-1')
        device_types = (
            DeviceType(manufacturer=manufacturer, model='Device Type 1', slug='device-type-1'),
            DeviceType(manufacturer=manufacturer, model='Device Type 2', slug='device-type-2'),
            DeviceType(manufacturer=manufacturer, model='Device Type 3', slug='device-type-3'),
        )
        DeviceType.objects.bulk_create(device_types)

        module_type = ModuleType.objects.create(manufacturer=manufacturer, model='Module Type 1')

        roles = (
            DeviceRole(name='Device Role 1', slug='device-role-1'),
            DeviceRole(name='Device Role 2', slug='device-role-2'),
            DeviceRole(name='Device Role 3', slug='device-role-3'),
        )
        DeviceRole.objects.bulk_create(roles)

        locations = (
            Location(name='Location 1', slug='location-1', site=sites[0]),
            Location(name='Location 2', slug='location-2', site=sites[1]),
            Location(name='Location 3', slug='location-3', site=sites[2]),
        )
        for location in locations:
            location.save()

        racks = (
            Rack(name='Rack 1', site=sites[0]),
            Rack(name='Rack 2', site=sites[1]),
            Rack(name='Rack 3', site=sites[2]),
        )
        Rack.objects.bulk_create(racks)

        devices = (
            Device(name='Device 1', device_type=device_types[0], role=roles[0], site=sites[0], location=locations[0], rack=racks[0], status='active'),
            Device(name='Device 2', device_type=device_types[1], role=roles[1], site=sites[1], location=locations[1], rack=racks[1], status='planned'),
            Device(name='Device 3', device_type=device_types[2], role=roles[2], site=sites[2], location=locations[2], rack=racks[2], status='offline'),
            Device(name=None, device_type=device_types[0], role=roles[0], site=sites[3], status='offline'),  # For cable connections
        )
        Device.objects.bulk_create(devices)

        module_bays = (
            ModuleBay(device=devices[0], name='Module Bay 1'),
            ModuleBay(device=devices[1], name='Module Bay 2'),
            ModuleBay(device=devices[2], name='Module Bay 3'),
        )
        for module_bay in module_bays:
            module_bay.save()

        modules = (
            Module(device=devices[0], module_bay=module_bays[0], module_type=module_type),
            Module(device=devices[1], module_bay=module_bays[1], module_type=module_type),
            Module(device=devices[2], module_bay=module_bays[2], module_type=module_type),
        )
        Module.objects.bulk_create(modules)

        console_server_ports = (
            ConsoleServerPort(device=devices[3], name='Console Server Port 1'),
            ConsoleServerPort(device=devices[3], name='Console Server Port 2'),
        )
        ConsoleServerPort.objects.bulk_create(console_server_ports)

        console_ports = (
            ConsolePort(device=devices[0], module=modules[0], name='Console Port 1', label='A', description='First'),
            ConsolePort(device=devices[1], module=modules[1], name='Console Port 2', label='B', description='Second'),
            ConsolePort(device=devices[2], module=modules[2], name='Console Port 3', label='C', description='Third'),
        )
        ConsolePort.objects.bulk_create(console_ports)

        # Cables
        Cable(a_terminations=[console_ports[0]], b_terminations=[console_server_ports[0]]).save()
        Cable(a_terminations=[console_ports[1]], b_terminations=[console_server_ports[1]]).save()
        # Third port is not connected

    def test_name(self):
        params = {'name': ['Console Port 1', 'Console Port 2']}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_label(self):
        params = {'label': ['A', 'B']}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_description(self):
        params = {'description': ['First', 'Second']}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_region(self):
        regions = Region.objects.all()[:2]
        params = {'region_id': [regions[0].pk, regions[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {'region': [regions[0].slug, regions[1].slug]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_site_group(self):
        site_groups = SiteGroup.objects.all()[:2]
        params = {'site_group_id': [site_groups[0].pk, site_groups[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {'site_group': [site_groups[0].slug, site_groups[1].slug]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_site(self):
        sites = Site.objects.all()[:2]
        params = {'site_id': [sites[0].pk, sites[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {'site': [sites[0].slug, sites[1].slug]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_location(self):
        locations = Location.objects.all()[:2]
        params = {'location_id': [locations[0].pk, locations[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {'location': [locations[0].slug, locations[1].slug]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_rack(self):
        racks = Rack.objects.all()[:2]
        params = {'rack_id': [racks[0].pk, racks[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {'rack': [racks[0].name, racks[1].name]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_device(self):
        devices = Device.objects.all()[:2]
        params = {'device_id': [devices[0].pk, devices[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {'device': [devices[0].name, devices[1].name]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_module(self):
        modules = Module.objects.all()[:2]
        params = {'module_id': [modules[0].pk, modules[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_cabled(self):
        params = {'cabled': True}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {'cabled': False}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_occupied(self):
        params = {'occupied': True}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {'occupied': False}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_connected(self):
        params = {'connected': True}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {'connected': False}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)


class ConsoleServerPortTestCase(TestCase, DeviceComponentFilterSetTests, ChangeLoggedFilterSetTests):
    queryset = ConsoleServerPort.objects.all()
    filterset = ConsoleServerPortFilterSet

    @classmethod
    def setUpTestData(cls):

        regions = (
            Region(name='Region 1', slug='region-1'),
            Region(name='Region 2', slug='region-2'),
            Region(name='Region 3', slug='region-3'),
        )
        for region in regions:
            region.save()

        groups = (
            SiteGroup(name='Site Group 1', slug='site-group-1'),
            SiteGroup(name='Site Group 2', slug='site-group-2'),
            SiteGroup(name='Site Group 3', slug='site-group-3'),
        )
        for group in groups:
            group.save()

        sites = Site.objects.bulk_create((
            Site(name='Site 1', slug='site-1', region=regions[0], group=groups[0]),
            Site(name='Site 2', slug='site-2', region=regions[1], group=groups[1]),
            Site(name='Site 3', slug='site-3', region=regions[2], group=groups[2]),
            Site(name='Site X', slug='site-x'),
        ))

        manufacturer = Manufacturer.objects.create(name='Manufacturer 1', slug='manufacturer-1')
        device_types = (
            DeviceType(manufacturer=manufacturer, model='Device Type 1', slug='device-type-1'),
            DeviceType(manufacturer=manufacturer, model='Device Type 2', slug='device-type-2'),
            DeviceType(manufacturer=manufacturer, model='Device Type 3', slug='device-type-3'),
        )
        DeviceType.objects.bulk_create(device_types)

        module_type = ModuleType.objects.create(manufacturer=manufacturer, model='Module Type 1')

        roles = (
            DeviceRole(name='Device Role 1', slug='device-role-1'),
            DeviceRole(name='Device Role 2', slug='device-role-2'),
            DeviceRole(name='Device Role 3', slug='device-role-3'),
        )
        DeviceRole.objects.bulk_create(roles)

        locations = (
            Location(name='Location 1', slug='location-1', site=sites[0]),
            Location(name='Location 2', slug='location-2', site=sites[1]),
            Location(name='Location 3', slug='location-3', site=sites[2]),
        )
        for location in locations:
            location.save()

        racks = (
            Rack(name='Rack 1', site=sites[0]),
            Rack(name='Rack 2', site=sites[1]),
            Rack(name='Rack 3', site=sites[2]),
        )
        Rack.objects.bulk_create(racks)

        devices = (
            Device(name='Device 1', device_type=device_types[0], role=roles[0], site=sites[0], location=locations[0], rack=racks[0], status='active'),
            Device(name='Device 2', device_type=device_types[1], role=roles[1], site=sites[1], location=locations[1], rack=racks[1], status='planned'),
            Device(name='Device 3', device_type=device_types[2], role=roles[2], site=sites[2], location=locations[2], rack=racks[2], status='offline'),
            Device(name=None, device_type=device_types[2], role=roles[2], site=sites[3], status='offline'),  # For cable connections
        )
        Device.objects.bulk_create(devices)

        module_bays = (
            ModuleBay(device=devices[0], name='Module Bay 1'),
            ModuleBay(device=devices[1], name='Module Bay 2'),
            ModuleBay(device=devices[2], name='Module Bay 3'),
        )
        for module_bay in module_bays:
            module_bay.save()

        modules = (
            Module(device=devices[0], module_bay=module_bays[0], module_type=module_type),
            Module(device=devices[1], module_bay=module_bays[1], module_type=module_type),
            Module(device=devices[2], module_bay=module_bays[2], module_type=module_type),
        )
        Module.objects.bulk_create(modules)

        console_ports = (
            ConsolePort(device=devices[3], name='Console Server Port 1'),
            ConsolePort(device=devices[3], name='Console Server Port 2'),
        )
        ConsolePort.objects.bulk_create(console_ports)

        console_server_ports = (
            ConsoleServerPort(device=devices[0], module=modules[0], name='Console Server Port 1', label='A', description='First'),
            ConsoleServerPort(device=devices[1], module=modules[1], name='Console Server Port 2', label='B', description='Second'),
            ConsoleServerPort(device=devices[2], module=modules[2], name='Console Server Port 3', label='C', description='Third'),
        )
        ConsoleServerPort.objects.bulk_create(console_server_ports)

        # Cables
        Cable(a_terminations=[console_server_ports[0]], b_terminations=[console_ports[0]]).save()
        Cable(a_terminations=[console_server_ports[1]], b_terminations=[console_ports[1]]).save()
        # Third port is not connected

    def test_name(self):
        params = {'name': ['Console Server Port 1', 'Console Server Port 2']}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_label(self):
        params = {'label': ['A', 'B']}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_description(self):
        params = {'description': ['First', 'Second']}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_region(self):
        regions = Region.objects.all()[:2]
        params = {'region_id': [regions[0].pk, regions[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {'region': [regions[0].slug, regions[1].slug]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_site_group(self):
        site_groups = SiteGroup.objects.all()[:2]
        params = {'site_group_id': [site_groups[0].pk, site_groups[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {'site_group': [site_groups[0].slug, site_groups[1].slug]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_site(self):
        sites = Site.objects.all()[:2]
        params = {'site_id': [sites[0].pk, sites[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {'site': [sites[0].slug, sites[1].slug]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_location(self):
        locations = Location.objects.all()[:2]
        params = {'location_id': [locations[0].pk, locations[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {'location': [locations[0].slug, locations[1].slug]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_rack(self):
        racks = Rack.objects.all()[:2]
        params = {'rack_id': [racks[0].pk, racks[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {'rack': [racks[0].name, racks[1].name]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_device(self):
        devices = Device.objects.all()[:2]
        params = {'device_id': [devices[0].pk, devices[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {'device': [devices[0].name, devices[1].name]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_module(self):
        modules = Module.objects.all()[:2]
        params = {'module_id': [modules[0].pk, modules[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_cabled(self):
        params = {'cabled': True}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {'cabled': False}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_occupied(self):
        params = {'occupied': True}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {'occupied': False}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_connected(self):
        params = {'connected': True}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {'connected': False}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)


class PowerPortTestCase(TestCase, DeviceComponentFilterSetTests, ChangeLoggedFilterSetTests):
    queryset = PowerPort.objects.all()
    filterset = PowerPortFilterSet

    @classmethod
    def setUpTestData(cls):

        regions = (
            Region(name='Region 1', slug='region-1'),
            Region(name='Region 2', slug='region-2'),
            Region(name='Region 3', slug='region-3'),
        )
        for region in regions:
            region.save()

        groups = (
            SiteGroup(name='Site Group 1', slug='site-group-1'),
            SiteGroup(name='Site Group 2', slug='site-group-2'),
            SiteGroup(name='Site Group 3', slug='site-group-3'),
        )
        for group in groups:
            group.save()

        sites = Site.objects.bulk_create((
            Site(name='Site 1', slug='site-1', region=regions[0], group=groups[0]),
            Site(name='Site 2', slug='site-2', region=regions[1], group=groups[1]),
            Site(name='Site 3', slug='site-3', region=regions[2], group=groups[2]),
            Site(name='Site X', slug='site-x'),
        ))

        manufacturer = Manufacturer.objects.create(name='Manufacturer 1', slug='manufacturer-1')
        device_types = (
            DeviceType(manufacturer=manufacturer, model='Device Type 1', slug='device-type-1'),
            DeviceType(manufacturer=manufacturer, model='Device Type 2', slug='device-type-2'),
            DeviceType(manufacturer=manufacturer, model='Device Type 3', slug='device-type-3'),
        )
        DeviceType.objects.bulk_create(device_types)

        module_type = ModuleType.objects.create(manufacturer=manufacturer, model='Module Type 1')

        roles = (
            DeviceRole(name='Device Role 1', slug='device-role-1'),
            DeviceRole(name='Device Role 2', slug='device-role-2'),
            DeviceRole(name='Device Role 3', slug='device-role-3'),
        )
        DeviceRole.objects.bulk_create(roles)

        locations = (
            Location(name='Location 1', slug='location-1', site=sites[0]),
            Location(name='Location 2', slug='location-2', site=sites[1]),
            Location(name='Location 3', slug='location-3', site=sites[2]),
        )
        for location in locations:
            location.save()

        racks = (
            Rack(name='Rack 1', site=sites[0]),
            Rack(name='Rack 2', site=sites[1]),
            Rack(name='Rack 3', site=sites[2]),
        )
        Rack.objects.bulk_create(racks)

        devices = (
            Device(name='Device 1', device_type=device_types[0], role=roles[0], site=sites[0], location=locations[0], rack=racks[0], status='active'),
            Device(name='Device 2', device_type=device_types[1], role=roles[1], site=sites[1], location=locations[1], rack=racks[1], status='planned'),
            Device(name='Device 3', device_type=device_types[2], role=roles[2], site=sites[2], location=locations[2], rack=racks[2], status='offline'),
            Device(name=None, device_type=device_types[2], role=roles[2], site=sites[3], status='offline'),  # For cable connections
        )
        Device.objects.bulk_create(devices)

        module_bays = (
            ModuleBay(device=devices[0], name='Module Bay 1'),
            ModuleBay(device=devices[1], name='Module Bay 2'),
            ModuleBay(device=devices[2], name='Module Bay 3'),
        )
        for module_bay in module_bays:
            module_bay.save()

        modules = (
            Module(device=devices[0], module_bay=module_bays[0], module_type=module_type),
            Module(device=devices[1], module_bay=module_bays[1], module_type=module_type),
            Module(device=devices[2], module_bay=module_bays[2], module_type=module_type),
        )
        Module.objects.bulk_create(modules)

        power_outlets = (
            PowerOutlet(device=devices[3], name='Power Outlet 1'),
            PowerOutlet(device=devices[3], name='Power Outlet 2'),
        )
        PowerOutlet.objects.bulk_create(power_outlets)

        power_ports = (
            PowerPort(device=devices[0], module=modules[0], name='Power Port 1', label='A', maximum_draw=100, allocated_draw=50, description='First'),
            PowerPort(device=devices[1], module=modules[1], name='Power Port 2', label='B', maximum_draw=200, allocated_draw=100, description='Second'),
            PowerPort(device=devices[2], module=modules[2], name='Power Port 3', label='C', maximum_draw=300, allocated_draw=150, description='Third'),
        )
        PowerPort.objects.bulk_create(power_ports)

        # Cables
        Cable(a_terminations=[power_ports[0]], b_terminations=[power_outlets[0]]).save()
        Cable(a_terminations=[power_ports[1]], b_terminations=[power_outlets[1]]).save()
        # Third port is not connected

    def test_name(self):
        params = {'name': ['Power Port 1', 'Power Port 2']}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_label(self):
        params = {'label': ['A', 'B']}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_description(self):
        params = {'description': ['First', 'Second']}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_maximum_draw(self):
        params = {'maximum_draw': [100, 200]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_allocated_draw(self):
        params = {'allocated_draw': [50, 100]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_region(self):
        regions = Region.objects.all()[:2]
        params = {'region_id': [regions[0].pk, regions[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {'region': [regions[0].slug, regions[1].slug]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_site_group(self):
        site_groups = SiteGroup.objects.all()[:2]
        params = {'site_group_id': [site_groups[0].pk, site_groups[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {'site_group': [site_groups[0].slug, site_groups[1].slug]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_site(self):
        sites = Site.objects.all()[:2]
        params = {'site_id': [sites[0].pk, sites[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {'site': [sites[0].slug, sites[1].slug]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_location(self):
        locations = Location.objects.all()[:2]
        params = {'location_id': [locations[0].pk, locations[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {'location': [locations[0].slug, locations[1].slug]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_rack(self):
        racks = Rack.objects.all()[:2]
        params = {'rack_id': [racks[0].pk, racks[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {'rack': [racks[0].name, racks[1].name]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_device(self):
        devices = Device.objects.all()[:2]
        params = {'device_id': [devices[0].pk, devices[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {'device': [devices[0].name, devices[1].name]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_module(self):
        modules = Module.objects.all()[:2]
        params = {'module_id': [modules[0].pk, modules[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_cabled(self):
        params = {'cabled': True}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {'cabled': False}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_occupied(self):
        params = {'occupied': True}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {'occupied': False}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_connected(self):
        params = {'connected': True}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {'connected': False}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)


class PowerOutletTestCase(TestCase, DeviceComponentFilterSetTests, ChangeLoggedFilterSetTests):
    queryset = PowerOutlet.objects.all()
    filterset = PowerOutletFilterSet

    @classmethod
    def setUpTestData(cls):

        regions = (
            Region(name='Region 1', slug='region-1'),
            Region(name='Region 2', slug='region-2'),
            Region(name='Region 3', slug='region-3'),
        )
        for region in regions:
            region.save()

        groups = (
            SiteGroup(name='Site Group 1', slug='site-group-1'),
            SiteGroup(name='Site Group 2', slug='site-group-2'),
            SiteGroup(name='Site Group 3', slug='site-group-3'),
        )
        for group in groups:
            group.save()

        sites = Site.objects.bulk_create((
            Site(name='Site 1', slug='site-1', region=regions[0], group=groups[0]),
            Site(name='Site 2', slug='site-2', region=regions[1], group=groups[1]),
            Site(name='Site 3', slug='site-3', region=regions[2], group=groups[2]),
            Site(name='Site X', slug='site-x'),
        ))

        manufacturer = Manufacturer.objects.create(name='Manufacturer 1', slug='manufacturer-1')
        device_types = (
            DeviceType(manufacturer=manufacturer, model='Device Type 1', slug='device-type-1'),
            DeviceType(manufacturer=manufacturer, model='Device Type 2', slug='device-type-2'),
            DeviceType(manufacturer=manufacturer, model='Device Type 3', slug='device-type-3'),
        )
        DeviceType.objects.bulk_create(device_types)

        module_type = ModuleType.objects.create(manufacturer=manufacturer, model='Module Type 1')

        roles = (
            DeviceRole(name='Device Role 1', slug='device-role-1'),
            DeviceRole(name='Device Role 2', slug='device-role-2'),
            DeviceRole(name='Device Role 3', slug='device-role-3'),
        )
        DeviceRole.objects.bulk_create(roles)

        locations = (
            Location(name='Location 1', slug='location-1', site=sites[0]),
            Location(name='Location 2', slug='location-2', site=sites[1]),
            Location(name='Location 3', slug='location-3', site=sites[2]),
        )
        for location in locations:
            location.save()

        racks = (
            Rack(name='Rack 1', site=sites[0]),
            Rack(name='Rack 2', site=sites[1]),
            Rack(name='Rack 3', site=sites[2]),
        )
        Rack.objects.bulk_create(racks)

        devices = (
            Device(name='Device 1', device_type=device_types[0], role=roles[0], site=sites[0], location=locations[0], rack=racks[0], status='active'),
            Device(name='Device 2', device_type=device_types[1], role=roles[1], site=sites[1], location=locations[1], rack=racks[1], status='planned'),
            Device(name='Device 3', device_type=device_types[2], role=roles[2], site=sites[2], location=locations[2], rack=racks[2], status='offline'),
            Device(name=None, device_type=device_types[2], role=roles[2], site=sites[3], status='offline'),  # For cable connections
        )
        Device.objects.bulk_create(devices)

        module_bays = (
            ModuleBay(device=devices[0], name='Module Bay 1'),
            ModuleBay(device=devices[1], name='Module Bay 2'),
            ModuleBay(device=devices[2], name='Module Bay 3'),
        )
        for module_bay in module_bays:
            module_bay.save()

        modules = (
            Module(device=devices[0], module_bay=module_bays[0], module_type=module_type),
            Module(device=devices[1], module_bay=module_bays[1], module_type=module_type),
            Module(device=devices[2], module_bay=module_bays[2], module_type=module_type),
        )
        Module.objects.bulk_create(modules)

        power_ports = (
            PowerPort(device=devices[3], name='Power Outlet 1'),
            PowerPort(device=devices[3], name='Power Outlet 2'),
        )
        PowerPort.objects.bulk_create(power_ports)

        power_outlets = (
            PowerOutlet(device=devices[0], module=modules[0], name='Power Outlet 1', label='A', feed_leg=PowerOutletFeedLegChoices.FEED_LEG_A, description='First', color='ff0000'),
            PowerOutlet(device=devices[1], module=modules[1], name='Power Outlet 2', label='B', feed_leg=PowerOutletFeedLegChoices.FEED_LEG_B, description='Second', color='00ff00'),
            PowerOutlet(device=devices[2], module=modules[2], name='Power Outlet 3', label='C', feed_leg=PowerOutletFeedLegChoices.FEED_LEG_C, description='Third', color='0000ff'),
        )
        PowerOutlet.objects.bulk_create(power_outlets)

        # Cables
        Cable(a_terminations=[power_outlets[0]], b_terminations=[power_ports[0]]).save()
        Cable(a_terminations=[power_outlets[1]], b_terminations=[power_ports[1]]).save()
        # Third port is not connected

    def test_name(self):
        params = {'name': ['Power Outlet 1', 'Power Outlet 2']}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_label(self):
        params = {'label': ['A', 'B']}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_description(self):
        params = {'description': ['First', 'Second']}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_color(self):
        params = {'color': ['ff0000', '00ff00']}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_feed_leg(self):
        params = {'feed_leg': [PowerOutletFeedLegChoices.FEED_LEG_A, PowerOutletFeedLegChoices.FEED_LEG_B]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_region(self):
        regions = Region.objects.all()[:2]
        params = {'region_id': [regions[0].pk, regions[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {'region': [regions[0].slug, regions[1].slug]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_site_group(self):
        site_groups = SiteGroup.objects.all()[:2]
        params = {'site_group_id': [site_groups[0].pk, site_groups[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {'site_group': [site_groups[0].slug, site_groups[1].slug]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_site(self):
        sites = Site.objects.all()[:2]
        params = {'site_id': [sites[0].pk, sites[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {'site': [sites[0].slug, sites[1].slug]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_location(self):
        locations = Location.objects.all()[:2]
        params = {'location_id': [locations[0].pk, locations[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {'location': [locations[0].slug, locations[1].slug]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_rack(self):
        racks = Rack.objects.all()[:2]
        params = {'rack_id': [racks[0].pk, racks[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {'rack': [racks[0].name, racks[1].name]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_device(self):
        devices = Device.objects.all()[:2]
        params = {'device_id': [devices[0].pk, devices[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {'device': [devices[0].name, devices[1].name]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_module(self):
        modules = Module.objects.all()[:2]
        params = {'module_id': [modules[0].pk, modules[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_cabled(self):
        params = {'cabled': True}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {'cabled': False}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_occupied(self):
        params = {'occupied': True}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {'occupied': False}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_connected(self):
        params = {'connected': True}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {'connected': False}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)


class InterfaceTestCase(TestCase, DeviceComponentFilterSetTests, ChangeLoggedFilterSetTests):
    queryset = Interface.objects.all()
    filterset = InterfaceFilterSet
    ignore_fields = ('tagged_vlans', 'untagged_vlan', 'qinq_svlan', 'vdcs')

    @classmethod
    def setUpTestData(cls):

        regions = (
            Region(name='Region 1', slug='region-1'),
            Region(name='Region 2', slug='region-2'),
            Region(name='Region 3', slug='region-3'),
        )
        for region in regions:
            region.save()

        groups = (
            SiteGroup(name='Site Group 1', slug='site-group-1'),
            SiteGroup(name='Site Group 2', slug='site-group-2'),
            SiteGroup(name='Site Group 3', slug='site-group-3'),
        )
        for group in groups:
            group.save()

        sites = Site.objects.bulk_create((
            Site(name='Site 1', slug='site-1', region=regions[0], group=groups[0]),
            Site(name='Site 2', slug='site-2', region=regions[1], group=groups[1]),
            Site(name='Site 3', slug='site-3', region=regions[2], group=groups[2]),
            Site(name='Site X', slug='site-x'),
        ))

        manufacturer = Manufacturer.objects.create(name='Manufacturer 1', slug='manufacturer-1')
        device_types = (
            DeviceType(manufacturer=manufacturer, model='Device Type 1', slug='device-type-1'),
            DeviceType(manufacturer=manufacturer, model='Device Type 2', slug='device-type-2'),
            DeviceType(manufacturer=manufacturer, model='Device Type 3', slug='device-type-3'),
        )
        DeviceType.objects.bulk_create(device_types)

        module_type = ModuleType.objects.create(manufacturer=manufacturer, model='Module Type 1')

        roles = (
            DeviceRole(name='Device Role 1', slug='device-role-1'),
            DeviceRole(name='Device Role 2', slug='device-role-2'),
            DeviceRole(name='Device Role 3', slug='device-role-3'),
        )
        DeviceRole.objects.bulk_create(roles)

        locations = (
            Location(name='Location 1', slug='location-1', site=sites[0]),
            Location(name='Location 2', slug='location-2', site=sites[1]),
            Location(name='Location 3', slug='location-3', site=sites[2]),
        )
        for location in locations:
            location.save()

        racks = (
            Rack(name='Rack 1', site=sites[0]),
            Rack(name='Rack 2', site=sites[1]),
            Rack(name='Rack 3', site=sites[2]),
        )
        Rack.objects.bulk_create(racks)

        # VirtualChassis assignment for filtering
        virtual_chassis = VirtualChassis(name='Virtual Chassis')
        virtual_chassis.save()

        devices = (
            Device(
                name='Device 1A',
                device_type=device_types[0],
                role=roles[0],
                site=sites[0],
                location=locations[0],
                rack=racks[0],
                virtual_chassis=virtual_chassis,
                vc_position=1,
                vc_priority=1,
                status='active',
            ),
            Device(
                name='Device 1B',
                device_type=device_types[2],
                role=roles[2],
                site=sites[2],
                location=locations[2],
                rack=racks[2],
                virtual_chassis=virtual_chassis,
                vc_position=2,
                vc_priority=1,
                status='planned',
            ),
            Device(
                name='Device 2',
                device_type=device_types[1],
                role=roles[1],
                site=sites[1],
                location=locations[1],
                rack=racks[1],
                status='offline',
            ),
            Device(
                name='Device 3',
                device_type=device_types[2],
                role=roles[2],
                site=sites[2],
                location=locations[2],
                rack=racks[2],
                status='offline',
            ),
            # For cable connections
            Device(
                name=None,
                device_type=device_types[2],
                role=roles[2],
                site=sites[3],
                status='offline',
            ),
        )
        Device.objects.bulk_create(devices)

        module_bays = (
            ModuleBay(device=devices[0], name='Module Bay 1'),
            ModuleBay(device=devices[1], name='Module Bay 2'),
            ModuleBay(device=devices[2], name='Module Bay 3'),
            ModuleBay(device=devices[3], name='Module Bay 4'),
        )
        for module_bay in module_bays:
            module_bay.save()

        modules = (
            Module(device=devices[0], module_bay=module_bays[0], module_type=module_type),
            Module(device=devices[1], module_bay=module_bays[1], module_type=module_type),
            Module(device=devices[2], module_bay=module_bays[2], module_type=module_type),
            Module(device=devices[3], module_bay=module_bays[3], module_type=module_type),
        )
        Module.objects.bulk_create(modules)

        vrfs = (
            VRF(name='VRF 1', rd='65000:1'),
            VRF(name='VRF 2', rd='65000:2'),
            VRF(name='VRF 3', rd='65000:3'),
        )
        VRF.objects.bulk_create(vrfs)

        # Virtual Device Context Creation
        vdcs = (
            VirtualDeviceContext(device=devices[4], name='VDC 1', identifier=1, status=VirtualDeviceContextStatusChoices.STATUS_ACTIVE),
            VirtualDeviceContext(device=devices[4], name='VDC 2', identifier=2, status=VirtualDeviceContextStatusChoices.STATUS_PLANNED),
        )
        VirtualDeviceContext.objects.bulk_create(vdcs)

        mac_addresses = (
            MACAddress(mac_address='00-00-00-00-00-01'),
            MACAddress(mac_address='00-00-00-00-00-02'),
            MACAddress(mac_address='00-00-00-00-00-03'),
        )
        MACAddress.objects.bulk_create(mac_addresses)

        vlans = (
            VLAN(name='SVLAN 1', vid=1001, qinq_role=VLANQinQRoleChoices.ROLE_SERVICE),
            VLAN(name='SVLAN 2', vid=1002, qinq_role=VLANQinQRoleChoices.ROLE_SERVICE),
            VLAN(name='SVLAN 3', vid=1003, qinq_role=VLANQinQRoleChoices.ROLE_SERVICE),
        )
        VLAN.objects.bulk_create(vlans)

        vlan_translation_policies = (
            VLANTranslationPolicy(name='Policy 1'),
            VLANTranslationPolicy(name='Policy 2'),
            VLANTranslationPolicy(name='Policy 3'),
        )
        VLANTranslationPolicy.objects.bulk_create(vlan_translation_policies)

        interfaces = (
            Interface(
                device=devices[0],
                module=modules[0],
                name='Interface 1',
                label='A',
                type=InterfaceTypeChoices.TYPE_1GE_SFP,
                enabled=True,
                mgmt_only=True,
                mtu=100,
                mode=InterfaceModeChoices.MODE_ACCESS,
                description='First',
                vrf=vrfs[0],
                speed=1000000,
                duplex='half',
                poe_mode=InterfacePoEModeChoices.MODE_PSE,
                poe_type=InterfacePoETypeChoices.TYPE_1_8023AF,
                vlan_translation_policy=vlan_translation_policies[0],
            ),
            Interface(
                device=devices[1],
                module=modules[1],
                name='VC Chassis Interface',
                type=InterfaceTypeChoices.TYPE_1GE_SFP,
                enabled=True
            ),
            Interface(
                device=devices[2],
                module=modules[2],
                name='Interface 2',
                label='B',
                type=InterfaceTypeChoices.TYPE_1GE_GBIC,
                enabled=True,
                mgmt_only=True,
                mtu=200,
                mode=InterfaceModeChoices.MODE_TAGGED,
                description='Second',
                vrf=vrfs[1],
                speed=1000000,
                duplex='full',
                poe_mode=InterfacePoEModeChoices.MODE_PD,
                poe_type=InterfacePoETypeChoices.TYPE_1_8023AF,
                vlan_translation_policy=vlan_translation_policies[0],
            ),
            Interface(
                device=devices[3],
                module=modules[3],
                name='Interface 3',
                label='C',
                type=InterfaceTypeChoices.TYPE_1GE_FIXED,
                enabled=False,
                mgmt_only=False,
                mtu=300,
                mode=InterfaceModeChoices.MODE_TAGGED_ALL,
                description='Third',
                vrf=vrfs[2],
                speed=100000,
                duplex='half',
                poe_mode=InterfacePoEModeChoices.MODE_PSE,
                poe_type=InterfacePoETypeChoices.TYPE_2_8023AT,
                vlan_translation_policy=vlan_translation_policies[1],
            ),
            Interface(
                device=devices[4],
                name='Interface 4',
                label='D',
                type=InterfaceTypeChoices.TYPE_OTHER,
                enabled=True,
                mgmt_only=True,
                tx_power=40,
                speed=100000,
                duplex='full',
                poe_mode=InterfacePoEModeChoices.MODE_PD,
                poe_type=InterfacePoETypeChoices.TYPE_2_8023AT,
                mode=InterfaceModeChoices.MODE_Q_IN_Q,
                qinq_svlan=vlans[0],
                vlan_translation_policy=vlan_translation_policies[1],
            ),
            Interface(
                device=devices[4],
                name='Interface 5',
                label='E',
                type=InterfaceTypeChoices.TYPE_OTHER,
                enabled=True,
                mgmt_only=True,
                tx_power=40,
                mode=InterfaceModeChoices.MODE_Q_IN_Q,
                qinq_svlan=vlans[1]
            ),
            Interface(
                device=devices[4],
                name='Interface 6',
                label='F',
                type=InterfaceTypeChoices.TYPE_OTHER,
                enabled=False,
                mgmt_only=False,
                tx_power=40,
                mode=InterfaceModeChoices.MODE_Q_IN_Q,
                qinq_svlan=vlans[2]
            ),
            Interface(
                device=devices[4],
                name='Interface 7',
                type=InterfaceTypeChoices.TYPE_80211AC,
                rf_role=WirelessRoleChoices.ROLE_AP,
                rf_channel=WirelessChannelChoices.CHANNEL_24G_1,
                rf_channel_frequency=2412,
                rf_channel_width=22
            ),
            Interface(
                device=devices[4],
                name='Interface 8',
                type=InterfaceTypeChoices.TYPE_80211AC,
                rf_role=WirelessRoleChoices.ROLE_STATION,
                rf_channel=WirelessChannelChoices.CHANNEL_5G_32,
                rf_channel_frequency=5160,
                rf_channel_width=20
            ),
        )
        Interface.objects.bulk_create(interfaces)

        interfaces[3].vdcs.set([vdcs[0], vdcs[1]])
        interfaces[4].vdcs.set([vdcs[0], vdcs[1]])
        interfaces[5].vdcs.set([vdcs[0]])
        interfaces[6].vdcs.set([vdcs[0]])
        interfaces[7].vdcs.set([vdcs[1]])

        interfaces[0].mac_addresses.set([mac_addresses[0]])
        interfaces[2].mac_addresses.set([mac_addresses[1]])
        interfaces[3].mac_addresses.set([mac_addresses[2]])

        # Cables
        Cable(a_terminations=[interfaces[0]], b_terminations=[interfaces[5]]).save()
        Cable(a_terminations=[interfaces[1]], b_terminations=[interfaces[6]]).save()
        # Third pair is not connected

    def test_name(self):
        params = {'name': ['Interface 1', 'Interface 2']}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_label(self):
        params = {'label': ['A', 'B']}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_enabled(self):
        params = {'enabled': 'true'}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 7)
        params = {'enabled': 'false'}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_mtu(self):
        params = {'mtu': [100, 200]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_speed(self):
        params = {'speed': [1000000, 100000]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 4)

    def test_duplex(self):
        params = {'duplex': ['half', 'full']}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 4)

    def test_mgmt_only(self):
        params = {'mgmt_only': 'true'}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 4)
        params = {'mgmt_only': 'false'}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 5)

    def test_poe_mode(self):
        params = {'poe_mode': [InterfacePoEModeChoices.MODE_PD, InterfacePoEModeChoices.MODE_PSE]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 4)

    def test_poe_type(self):
        params = {'poe_type': [InterfacePoETypeChoices.TYPE_1_8023AF, InterfacePoETypeChoices.TYPE_2_8023AT]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 4)

    def test_mode(self):
        params = {'mode': InterfaceModeChoices.MODE_ACCESS}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_description(self):
        params = {'description': ['First', 'Second']}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_parent(self):
        # Create child interfaces
        parent_interface = Interface.objects.first()
        child_interfaces = (
            Interface(device=parent_interface.device, name='Child 1', parent=parent_interface, type=InterfaceTypeChoices.TYPE_VIRTUAL),
            Interface(device=parent_interface.device, name='Child 2', parent=parent_interface, type=InterfaceTypeChoices.TYPE_VIRTUAL),
            Interface(device=parent_interface.device, name='Child 3', parent=parent_interface, type=InterfaceTypeChoices.TYPE_VIRTUAL),
        )
        Interface.objects.bulk_create(child_interfaces)

        params = {'parent_id': [parent_interface.pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 3)

    def test_bridge(self):
        # Create bridged interfaces
        bridge_interface = Interface.objects.first()
        bridged_interfaces = (
            Interface(device=bridge_interface.device, name='Bridged 1', bridge=bridge_interface, type=InterfaceTypeChoices.TYPE_1GE_FIXED),
            Interface(device=bridge_interface.device, name='Bridged 2', bridge=bridge_interface, type=InterfaceTypeChoices.TYPE_1GE_FIXED),
            Interface(device=bridge_interface.device, name='Bridged 3', bridge=bridge_interface, type=InterfaceTypeChoices.TYPE_1GE_FIXED),
        )
        Interface.objects.bulk_create(bridged_interfaces)

        params = {'bridge_id': [bridge_interface.pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 3)

    def test_lag(self):
        # Create LAG members
        device = Device.objects.first()
        lag_interface = Interface(device=device, name='LAG', type=InterfaceTypeChoices.TYPE_LAG)
        lag_interface.save()
        lag_members = (
            Interface(device=device, name='Member 1', lag=lag_interface, type=InterfaceTypeChoices.TYPE_1GE_FIXED),
            Interface(device=device, name='Member 2', lag=lag_interface, type=InterfaceTypeChoices.TYPE_1GE_FIXED),
            Interface(device=device, name='Member 3', lag=lag_interface, type=InterfaceTypeChoices.TYPE_1GE_FIXED),
        )
        Interface.objects.bulk_create(lag_members)

        params = {'lag_id': [lag_interface.pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 3)

    def test_region(self):
        regions = Region.objects.all()[:2]
        params = {'region_id': [regions[0].pk, regions[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {'region': [regions[0].slug, regions[1].slug]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_site_group(self):
        site_groups = SiteGroup.objects.all()[:2]
        params = {'site_group_id': [site_groups[0].pk, site_groups[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {'site_group': [site_groups[0].slug, site_groups[1].slug]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_site(self):
        sites = Site.objects.all()[:2]
        params = {'site_id': [sites[0].pk, sites[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {'site': [sites[0].slug, sites[1].slug]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_location(self):
        locations = Location.objects.all()[:2]
        params = {'location_id': [locations[0].pk, locations[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {'location': [locations[0].slug, locations[1].slug]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_rack(self):
        racks = Rack.objects.all()[:2]
        params = {'rack_id': [racks[0].pk, racks[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {'rack': [racks[0].name, racks[1].name]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_virtual_chassis_id(self):
        params = {'virtual_chassis_id': [VirtualChassis.objects.first().pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_device(self):
        devices = Device.objects.all()[:2]
        params = {'device_id': [devices[0].pk, devices[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {'device': [devices[0].name, devices[1].name]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_virtual_chassis_member(self):
        # Device 1A & 3 have 1 management interface, Device 1B has 1 interfaces
        devices = Device.objects.filter(name__in=['Device 1A', 'Device 3'])
        params = {'virtual_chassis_member_id': [devices[0].pk, devices[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 3)
        params = {'virtual_chassis_member': [devices[0].name, devices[1].name]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 3)

    def test_module(self):
        modules = Module.objects.all()[:2]
        params = {'module_id': [modules[0].pk, modules[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_cabled(self):
        params = {'cabled': True}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 4)
        params = {'cabled': False}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 5)

    def test_occupied(self):
        params = {'occupied': True}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 4)
        params = {'occupied': False}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 5)

    def test_connected(self):
        params = {'connected': True}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 4)
        params = {'connected': False}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 5)

    def test_kind(self):
        params = {'kind': 'physical'}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 7)
        params = {'kind': 'virtual'}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 0)

    def test_mac_address(self):
        params = {'mac_address': ['00-00-00-00-00-01', '00-00-00-00-00-02']}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_type(self):
        params = {'type': [InterfaceTypeChoices.TYPE_1GE_FIXED, InterfaceTypeChoices.TYPE_1GE_GBIC]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_rf_role(self):
        params = {'rf_role': [WirelessRoleChoices.ROLE_AP, WirelessRoleChoices.ROLE_STATION]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_rf_channel(self):
        params = {'rf_channel': [WirelessChannelChoices.CHANNEL_24G_1, WirelessChannelChoices.CHANNEL_5G_32]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_rf_channel_frequency(self):
        params = {'rf_channel_frequency': [2412, 5160]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_rf_channel_width(self):
        params = {'rf_channel_width': [22, 20]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_tx_power(self):
        params = {'tx_power': [40]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 3)

    def test_vrf(self):
        vrfs = VRF.objects.all()[:2]
        params = {'vrf_id': [vrfs[0].pk, vrfs[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {'vrf': [vrfs[0].rd, vrfs[1].rd]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_vdc(self):
        params = {'vdc': ['VDC 1']}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 4)

        devices = Device.objects.last()
        vdc = VirtualDeviceContext.objects.filter(device=devices, name='VDC 2')
        params = {'vdc_id': vdc.values_list('pk', flat=True)}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 3)

    def test_vdc_identifier(self):
        devices = Device.objects.last()
        vdc = VirtualDeviceContext.objects.filter(device=devices, name='VDC 2')
        params = {'vdc_identifier': vdc.values_list('identifier', flat=True)}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 3)

    def test_vlan(self):
        vlan = VLAN.objects.filter(qinq_role=VLANQinQRoleChoices.ROLE_SERVICE).first()
        params = {'vlan_id': vlan.pk}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)
        params = {'vlan': vlan.vid}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_vlan_translation_policy(self):
        vlan_translation_policies = VLANTranslationPolicy.objects.all()[:2]
        params = {'vlan_translation_policy_id': [vlan_translation_policies[0].pk, vlan_translation_policies[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 4)
        params = {'vlan_translation_policy': [vlan_translation_policies[0].name, vlan_translation_policies[1].name]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 4)


class FrontPortTestCase(TestCase, DeviceComponentFilterSetTests, ChangeLoggedFilterSetTests):
    queryset = FrontPort.objects.all()
    filterset = FrontPortFilterSet

    @classmethod
    def setUpTestData(cls):

        regions = (
            Region(name='Region 1', slug='region-1'),
            Region(name='Region 2', slug='region-2'),
            Region(name='Region 3', slug='region-3'),
        )
        for region in regions:
            region.save()

        groups = (
            SiteGroup(name='Site Group 1', slug='site-group-1'),
            SiteGroup(name='Site Group 2', slug='site-group-2'),
            SiteGroup(name='Site Group 3', slug='site-group-3'),
        )
        for group in groups:
            group.save()

        sites = Site.objects.bulk_create((
            Site(name='Site 1', slug='site-1', region=regions[0], group=groups[0]),
            Site(name='Site 2', slug='site-2', region=regions[1], group=groups[1]),
            Site(name='Site 3', slug='site-3', region=regions[2], group=groups[2]),
            Site(name='Site X', slug='site-x'),
        ))

        manufacturer = Manufacturer.objects.create(name='Manufacturer 1', slug='manufacturer-1')
        device_types = (
            DeviceType(manufacturer=manufacturer, model='Device Type 1', slug='device-type-1'),
            DeviceType(manufacturer=manufacturer, model='Device Type 2', slug='device-type-2'),
            DeviceType(manufacturer=manufacturer, model='Device Type 3', slug='device-type-3'),
        )
        DeviceType.objects.bulk_create(device_types)

        module_type = ModuleType.objects.create(manufacturer=manufacturer, model='Module Type 1')

        roles = (
            DeviceRole(name='Device Role 1', slug='device-role-1'),
            DeviceRole(name='Device Role 2', slug='device-role-2'),
            DeviceRole(name='Device Role 3', slug='device-role-3'),
        )
        DeviceRole.objects.bulk_create(roles)

        locations = (
            Location(name='Location 1', slug='location-1', site=sites[0]),
            Location(name='Location 2', slug='location-2', site=sites[1]),
            Location(name='Location 3', slug='location-3', site=sites[2]),
        )
        for location in locations:
            location.save()

        racks = (
            Rack(name='Rack 1', site=sites[0]),
            Rack(name='Rack 2', site=sites[1]),
            Rack(name='Rack 3', site=sites[2]),
        )
        Rack.objects.bulk_create(racks)

        devices = (
            Device(name='Device 1', device_type=device_types[0], role=roles[0], site=sites[0], location=locations[0], rack=racks[0], status='active'),
            Device(name='Device 2', device_type=device_types[1], role=roles[1], site=sites[1], location=locations[1], rack=racks[1], status='planned'),
            Device(name='Device 3', device_type=device_types[2], role=roles[2], site=sites[2], location=locations[2], rack=racks[2], status='offline'),
            Device(name=None, device_type=device_types[2], role=roles[2], site=sites[3], status='offline'),  # For cable connections
        )
        Device.objects.bulk_create(devices)

        module_bays = (
            ModuleBay(device=devices[0], name='Module Bay 1'),
            ModuleBay(device=devices[1], name='Module Bay 2'),
            ModuleBay(device=devices[2], name='Module Bay 3'),
        )
        for module_bay in module_bays:
            module_bay.save()

        modules = (
            Module(device=devices[0], module_bay=module_bays[0], module_type=module_type),
            Module(device=devices[1], module_bay=module_bays[1], module_type=module_type),
            Module(device=devices[2], module_bay=module_bays[2], module_type=module_type),
        )
        Module.objects.bulk_create(modules)

        rear_ports = (
            RearPort(device=devices[0], name='Rear Port 1', type=PortTypeChoices.TYPE_8P8C, positions=6),
            RearPort(device=devices[1], name='Rear Port 2', type=PortTypeChoices.TYPE_8P8C, positions=6),
            RearPort(device=devices[2], name='Rear Port 3', type=PortTypeChoices.TYPE_8P8C, positions=6),
            RearPort(device=devices[3], name='Rear Port 4', type=PortTypeChoices.TYPE_8P8C, positions=6),
            RearPort(device=devices[3], name='Rear Port 5', type=PortTypeChoices.TYPE_8P8C, positions=6),
            RearPort(device=devices[3], name='Rear Port 6', type=PortTypeChoices.TYPE_8P8C, positions=6),
        )
        RearPort.objects.bulk_create(rear_ports)

        front_ports = (
            FrontPort(device=devices[0], module=modules[0], name='Front Port 1', label='A', type=PortTypeChoices.TYPE_8P8C, color=ColorChoices.COLOR_RED, rear_port=rear_ports[0], rear_port_position=1, description='First'),
            FrontPort(device=devices[1], module=modules[1], name='Front Port 2', label='B', type=PortTypeChoices.TYPE_110_PUNCH, color=ColorChoices.COLOR_GREEN, rear_port=rear_ports[1], rear_port_position=2, description='Second'),
            FrontPort(device=devices[2], module=modules[2], name='Front Port 3', label='C', type=PortTypeChoices.TYPE_BNC, color=ColorChoices.COLOR_BLUE, rear_port=rear_ports[2], rear_port_position=3, description='Third'),
            FrontPort(device=devices[3], name='Front Port 4', label='D', type=PortTypeChoices.TYPE_FC, rear_port=rear_ports[3], rear_port_position=1),
            FrontPort(device=devices[3], name='Front Port 5', label='E', type=PortTypeChoices.TYPE_FC, rear_port=rear_ports[4], rear_port_position=1),
            FrontPort(device=devices[3], name='Front Port 6', label='F', type=PortTypeChoices.TYPE_FC, rear_port=rear_ports[5], rear_port_position=1),
        )
        FrontPort.objects.bulk_create(front_ports)

        # Cables
        Cable(a_terminations=[front_ports[0]], b_terminations=[front_ports[3]]).save()
        Cable(a_terminations=[front_ports[1]], b_terminations=[front_ports[4]]).save()
        # Third port is not connected

    def test_name(self):
        params = {'name': ['Front Port 1', 'Front Port 2']}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_label(self):
        params = {'label': ['A', 'B']}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_type(self):
        params = {'type': [PortTypeChoices.TYPE_8P8C, PortTypeChoices.TYPE_110_PUNCH]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_color(self):
        params = {'color': [ColorChoices.COLOR_RED, ColorChoices.COLOR_GREEN]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_description(self):
        params = {'description': ['First', 'Second']}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_region(self):
        regions = Region.objects.all()[:2]
        params = {'region_id': [regions[0].pk, regions[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {'region': [regions[0].slug, regions[1].slug]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_site_group(self):
        site_groups = SiteGroup.objects.all()[:2]
        params = {'site_group_id': [site_groups[0].pk, site_groups[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {'site_group': [site_groups[0].slug, site_groups[1].slug]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_site(self):
        sites = Site.objects.all()[:2]
        params = {'site_id': [sites[0].pk, sites[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {'site': [sites[0].slug, sites[1].slug]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_location(self):
        locations = Location.objects.all()[:2]
        params = {'location_id': [locations[0].pk, locations[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {'location': [locations[0].slug, locations[1].slug]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_rack(self):
        racks = Rack.objects.all()[:2]
        params = {'rack_id': [racks[0].pk, racks[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {'rack': [racks[0].name, racks[1].name]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_device(self):
        devices = Device.objects.all()[:2]
        params = {'device_id': [devices[0].pk, devices[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {'device': [devices[0].name, devices[1].name]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_module(self):
        modules = Module.objects.all()[:2]
        params = {'module_id': [modules[0].pk, modules[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_cabled(self):
        params = {'cabled': True}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 4)
        params = {'cabled': False}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_occupied(self):
        params = {'occupied': True}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 4)
        params = {'occupied': False}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)


class RearPortTestCase(TestCase, DeviceComponentFilterSetTests, ChangeLoggedFilterSetTests):
    queryset = RearPort.objects.all()
    filterset = RearPortFilterSet

    @classmethod
    def setUpTestData(cls):

        regions = (
            Region(name='Region 1', slug='region-1'),
            Region(name='Region 2', slug='region-2'),
            Region(name='Region 3', slug='region-3'),
        )
        for region in regions:
            region.save()

        groups = (
            SiteGroup(name='Site Group 1', slug='site-group-1'),
            SiteGroup(name='Site Group 2', slug='site-group-2'),
            SiteGroup(name='Site Group 3', slug='site-group-3'),
        )
        for group in groups:
            group.save()

        sites = Site.objects.bulk_create((
            Site(name='Site 1', slug='site-1', region=regions[0], group=groups[0]),
            Site(name='Site 2', slug='site-2', region=regions[1], group=groups[1]),
            Site(name='Site 3', slug='site-3', region=regions[2], group=groups[2]),
            Site(name='Site X', slug='site-x'),
        ))

        manufacturer = Manufacturer.objects.create(name='Manufacturer 1', slug='manufacturer-1')
        device_types = (
            DeviceType(manufacturer=manufacturer, model='Device Type 1', slug='device-type-1'),
            DeviceType(manufacturer=manufacturer, model='Device Type 2', slug='device-type-2'),
            DeviceType(manufacturer=manufacturer, model='Device Type 3', slug='device-type-3'),
        )
        DeviceType.objects.bulk_create(device_types)

        module_type = ModuleType.objects.create(manufacturer=manufacturer, model='Module Type 1')

        roles = (
            DeviceRole(name='Device Role 1', slug='device-role-1'),
            DeviceRole(name='Device Role 2', slug='device-role-2'),
            DeviceRole(name='Device Role 3', slug='device-role-3'),
        )
        DeviceRole.objects.bulk_create(roles)

        locations = (
            Location(name='Location 1', slug='location-1', site=sites[0]),
            Location(name='Location 2', slug='location-2', site=sites[1]),
            Location(name='Location 3', slug='location-3', site=sites[2]),
        )
        for location in locations:
            location.save()

        racks = (
            Rack(name='Rack 1', site=sites[0]),
            Rack(name='Rack 2', site=sites[1]),
            Rack(name='Rack 3', site=sites[2]),
        )
        Rack.objects.bulk_create(racks)

        devices = (
            Device(name='Device 1', device_type=device_types[0], role=roles[0], site=sites[0], location=locations[0], rack=racks[0], status='active'),
            Device(name='Device 2', device_type=device_types[1], role=roles[1], site=sites[1], location=locations[1], rack=racks[1], status='planned'),
            Device(name='Device 3', device_type=device_types[2], role=roles[2], site=sites[2], location=locations[2], rack=racks[2], status='offline'),
            Device(name=None, device_type=device_types[2], role=roles[2], site=sites[3], status='offline'),  # For cable connections
        )
        Device.objects.bulk_create(devices)

        module_bays = (
            ModuleBay(device=devices[0], name='Module Bay 1'),
            ModuleBay(device=devices[1], name='Module Bay 2'),
            ModuleBay(device=devices[2], name='Module Bay 3'),
        )
        for module_bay in module_bays:
            module_bay.save()

        modules = (
            Module(device=devices[0], module_bay=module_bays[0], module_type=module_type),
            Module(device=devices[1], module_bay=module_bays[1], module_type=module_type),
            Module(device=devices[2], module_bay=module_bays[2], module_type=module_type),
        )
        Module.objects.bulk_create(modules)

        rear_ports = (
            RearPort(device=devices[0], module=modules[0], name='Rear Port 1', label='A', type=PortTypeChoices.TYPE_8P8C, color=ColorChoices.COLOR_RED, positions=1, description='First'),
            RearPort(device=devices[1], module=modules[1], name='Rear Port 2', label='B', type=PortTypeChoices.TYPE_110_PUNCH, color=ColorChoices.COLOR_GREEN, positions=2, description='Second'),
            RearPort(device=devices[2], module=modules[2], name='Rear Port 3', label='C', type=PortTypeChoices.TYPE_BNC, color=ColorChoices.COLOR_BLUE, positions=3, description='Third'),
            RearPort(device=devices[3], name='Rear Port 4', label='D', type=PortTypeChoices.TYPE_FC, positions=4),
            RearPort(device=devices[3], name='Rear Port 5', label='E', type=PortTypeChoices.TYPE_FC, positions=5),
            RearPort(device=devices[3], name='Rear Port 6', label='F', type=PortTypeChoices.TYPE_FC, positions=6),
        )
        RearPort.objects.bulk_create(rear_ports)

        # Cables
        Cable(a_terminations=[rear_ports[0]], b_terminations=[rear_ports[3]]).save()
        Cable(a_terminations=[rear_ports[1]], b_terminations=[rear_ports[4]]).save()
        # Third port is not connected

    def test_name(self):
        params = {'name': ['Rear Port 1', 'Rear Port 2']}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_label(self):
        params = {'label': ['A', 'B']}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_type(self):
        params = {'type': [PortTypeChoices.TYPE_8P8C, PortTypeChoices.TYPE_110_PUNCH]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_color(self):
        params = {'color': [ColorChoices.COLOR_RED, ColorChoices.COLOR_GREEN]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_positions(self):
        params = {'positions': [1, 2]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_description(self):
        params = {'description': ['First', 'Second']}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_region(self):
        regions = Region.objects.all()[:2]
        params = {'region_id': [regions[0].pk, regions[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {'region': [regions[0].slug, regions[1].slug]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_site_group(self):
        site_groups = SiteGroup.objects.all()[:2]
        params = {'site_group_id': [site_groups[0].pk, site_groups[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {'site_group': [site_groups[0].slug, site_groups[1].slug]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_site(self):
        sites = Site.objects.all()[:2]
        params = {'site_id': [sites[0].pk, sites[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {'site': [sites[0].slug, sites[1].slug]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_location(self):
        locations = Location.objects.all()[:2]
        params = {'location_id': [locations[0].pk, locations[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {'location': [locations[0].slug, locations[1].slug]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_rack(self):
        racks = Rack.objects.all()[:2]
        params = {'rack_id': [racks[0].pk, racks[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {'rack': [racks[0].name, racks[1].name]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_device(self):
        devices = Device.objects.all()[:2]
        params = {'device_id': [devices[0].pk, devices[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {'device': [devices[0].name, devices[1].name]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_module(self):
        modules = Module.objects.all()[:2]
        params = {'module_id': [modules[0].pk, modules[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_cabled(self):
        params = {'cabled': True}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 4)
        params = {'cabled': False}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_occupied(self):
        params = {'occupied': True}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 4)
        params = {'occupied': False}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)


class ModuleBayTestCase(TestCase, DeviceComponentFilterSetTests, ChangeLoggedFilterSetTests):
    queryset = ModuleBay.objects.all()
    filterset = ModuleBayFilterSet

    @classmethod
    def setUpTestData(cls):

        regions = (
            Region(name='Region 1', slug='region-1'),
            Region(name='Region 2', slug='region-2'),
            Region(name='Region 3', slug='region-3'),
        )
        for region in regions:
            region.save()

        groups = (
            SiteGroup(name='Site Group 1', slug='site-group-1'),
            SiteGroup(name='Site Group 2', slug='site-group-2'),
            SiteGroup(name='Site Group 3', slug='site-group-3'),
        )
        for group in groups:
            group.save()

        sites = Site.objects.bulk_create((
            Site(name='Site 1', slug='site-1', region=regions[0], group=groups[0]),
            Site(name='Site 2', slug='site-2', region=regions[1], group=groups[1]),
            Site(name='Site 3', slug='site-3', region=regions[2], group=groups[2]),
            Site(name='Site X', slug='site-x'),
        ))

        manufacturer = Manufacturer.objects.create(name='Manufacturer 1', slug='manufacturer-1')
        device_types = (
            DeviceType(manufacturer=manufacturer, model='Device Type 1', slug='device-type-1'),
            DeviceType(manufacturer=manufacturer, model='Device Type 2', slug='device-type-2'),
            DeviceType(manufacturer=manufacturer, model='Device Type 3', slug='device-type-3'),
        )
        DeviceType.objects.bulk_create(device_types)

        roles = (
            DeviceRole(name='Device Role 1', slug='device-role-1'),
            DeviceRole(name='Device Role 2', slug='device-role-2'),
            DeviceRole(name='Device Role 3', slug='device-role-3'),
        )
        DeviceRole.objects.bulk_create(roles)

        locations = (
            Location(name='Location 1', slug='location-1', site=sites[0]),
            Location(name='Location 2', slug='location-2', site=sites[1]),
            Location(name='Location 3', slug='location-3', site=sites[2]),
        )
        for location in locations:
            location.save()

        racks = (
            Rack(name='Rack 1', site=sites[0]),
            Rack(name='Rack 2', site=sites[1]),
            Rack(name='Rack 3', site=sites[2]),
        )
        Rack.objects.bulk_create(racks)

        devices = (
            Device(name='Device 1', device_type=device_types[0], role=roles[0], site=sites[0], location=locations[0], rack=racks[0], status='active'),
            Device(name='Device 2', device_type=device_types[1], role=roles[1], site=sites[1], location=locations[1], rack=racks[1], status='planned'),
            Device(name='Device 3', device_type=device_types[2], role=roles[2], site=sites[2], location=locations[2], rack=racks[2], status='offline'),
        )
        Device.objects.bulk_create(devices)

        module_bays = (
            ModuleBay(device=devices[0], name='Module Bay 1', label='A', description='First'),
            ModuleBay(device=devices[1], name='Module Bay 2', label='B', description='Second'),
            ModuleBay(device=devices[2], name='Module Bay 3', label='C', description='Third'),
            ModuleBay(device=devices[2], name='Module Bay 4', label='D', description='Fourth'),
            ModuleBay(device=devices[2], name='Module Bay 5', label='E', description='Fifth'),
        )
        for module_bay in module_bays:
            module_bay.save()

        module_type = ModuleType.objects.create(manufacturer=manufacturer, model='Module Type 1')
        modules = (
            Module(device=devices[0], module_bay=module_bays[0], module_type=module_type),
            Module(device=devices[1], module_bay=module_bays[1], module_type=module_type),
        )
        Module.objects.bulk_create(modules)
        module_bays[3].module = modules[0]
        module_bays[3].save()
        module_bays[4].module = modules[1]
        module_bays[4].save()

    def test_name(self):
        params = {'name': ['Module Bay 1', 'Module Bay 2']}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_label(self):
        params = {'label': ['A', 'B']}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_description(self):
        params = {'description': ['First', 'Second']}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_region(self):
        regions = Region.objects.all()[:2]
        params = {'region_id': [regions[0].pk, regions[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {'region': [regions[0].slug, regions[1].slug]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_site_group(self):
        site_groups = SiteGroup.objects.all()[:2]
        params = {'site_group_id': [site_groups[0].pk, site_groups[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {'site_group': [site_groups[0].slug, site_groups[1].slug]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_site(self):
        sites = Site.objects.all()[:2]
        params = {'site_id': [sites[0].pk, sites[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {'site': [sites[0].slug, sites[1].slug]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_location(self):
        locations = Location.objects.all()[:2]
        params = {'location_id': [locations[0].pk, locations[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {'location': [locations[0].slug, locations[1].slug]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_rack(self):
        racks = Rack.objects.all()[:2]
        params = {'rack_id': [racks[0].pk, racks[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {'rack': [racks[0].name, racks[1].name]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_device(self):
        devices = Device.objects.all()[:2]
        params = {'device_id': [devices[0].pk, devices[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {'device': [devices[0].name, devices[1].name]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_module(self):
        modules = Module.objects.all()[:2]
        params = {'module_id': [modules[0].pk, modules[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)


class DeviceBayTestCase(TestCase, DeviceComponentFilterSetTests, ChangeLoggedFilterSetTests):
    queryset = DeviceBay.objects.all()
    filterset = DeviceBayFilterSet

    @classmethod
    def setUpTestData(cls):

        regions = (
            Region(name='Region 1', slug='region-1'),
            Region(name='Region 2', slug='region-2'),
            Region(name='Region 3', slug='region-3'),
        )
        for region in regions:
            region.save()

        groups = (
            SiteGroup(name='Site Group 1', slug='site-group-1'),
            SiteGroup(name='Site Group 2', slug='site-group-2'),
            SiteGroup(name='Site Group 3', slug='site-group-3'),
        )
        for group in groups:
            group.save()

        sites = Site.objects.bulk_create((
            Site(name='Site 1', slug='site-1', region=regions[0], group=groups[0]),
            Site(name='Site 2', slug='site-2', region=regions[1], group=groups[1]),
            Site(name='Site 3', slug='site-3', region=regions[2], group=groups[2]),
            Site(name='Site X', slug='site-x'),
        ))

        manufacturer = Manufacturer.objects.create(name='Manufacturer 1', slug='manufacturer-1')
        device_types = (
            DeviceType(manufacturer=manufacturer, model='Device Type 1', slug='device-type-1'),
            DeviceType(manufacturer=manufacturer, model='Device Type 2', slug='device-type-2'),
            DeviceType(manufacturer=manufacturer, model='Device Type 3', slug='device-type-3'),
        )
        DeviceType.objects.bulk_create(device_types)

        roles = (
            DeviceRole(name='Device Role 1', slug='device-role-1'),
            DeviceRole(name='Device Role 2', slug='device-role-2'),
            DeviceRole(name='Device Role 3', slug='device-role-3'),
        )
        DeviceRole.objects.bulk_create(roles)

        locations = (
            Location(name='Location 1', slug='location-1', site=sites[0]),
            Location(name='Location 2', slug='location-2', site=sites[1]),
            Location(name='Location 3', slug='location-3', site=sites[2]),
        )
        for location in locations:
            location.save()

        racks = (
            Rack(name='Rack 1', site=sites[0]),
            Rack(name='Rack 2', site=sites[1]),
            Rack(name='Rack 3', site=sites[2]),
        )
        Rack.objects.bulk_create(racks)

        devices = (
            Device(name='Device 1', device_type=device_types[0], role=roles[0], site=sites[0], location=locations[0], rack=racks[0], status='active'),
            Device(name='Device 2', device_type=device_types[1], role=roles[1], site=sites[1], location=locations[1], rack=racks[1], status='planned'),
            Device(name='Device 3', device_type=device_types[2], role=roles[2], site=sites[2], location=locations[2], rack=racks[2], status='offline'),
        )
        Device.objects.bulk_create(devices)

        device_bays = (
            DeviceBay(device=devices[0], name='Device Bay 1', label='A', description='First'),
            DeviceBay(device=devices[1], name='Device Bay 2', label='B', description='Second'),
            DeviceBay(device=devices[2], name='Device Bay 3', label='C', description='Third'),
        )
        DeviceBay.objects.bulk_create(device_bays)

    def test_name(self):
        params = {'name': ['Device Bay 1', 'Device Bay 2']}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_label(self):
        params = {'label': ['A', 'B']}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_description(self):
        params = {'description': ['First', 'Second']}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_region(self):
        regions = Region.objects.all()[:2]
        params = {'region_id': [regions[0].pk, regions[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {'region': [regions[0].slug, regions[1].slug]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_site_group(self):
        site_groups = SiteGroup.objects.all()[:2]
        params = {'site_group_id': [site_groups[0].pk, site_groups[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {'site_group': [site_groups[0].slug, site_groups[1].slug]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_site(self):
        sites = Site.objects.all()[:2]
        params = {'site_id': [sites[0].pk, sites[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {'site': [sites[0].slug, sites[1].slug]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_location(self):
        locations = Location.objects.all()[:2]
        params = {'location_id': [locations[0].pk, locations[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {'location': [locations[0].slug, locations[1].slug]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_rack(self):
        racks = Rack.objects.all()[:2]
        params = {'rack_id': [racks[0].pk, racks[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {'rack': [racks[0].name, racks[1].name]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_device(self):
        devices = Device.objects.all()[:2]
        params = {'device_id': [devices[0].pk, devices[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {'device': [devices[0].name, devices[1].name]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)


class InventoryItemTestCase(TestCase, ChangeLoggedFilterSetTests):
    queryset = InventoryItem.objects.all()
    filterset = InventoryItemFilterSet

    @classmethod
    def setUpTestData(cls):
        manufacturers = (
            Manufacturer(name='Manufacturer 1', slug='manufacturer-1'),
            Manufacturer(name='Manufacturer 2', slug='manufacturer-2'),
            Manufacturer(name='Manufacturer 3', slug='manufacturer-3'),
        )
        Manufacturer.objects.bulk_create(manufacturers)

        device_types = (
            DeviceType(manufacturer=manufacturers[0], model='Device Type 1', slug='device-type-1'),
            DeviceType(manufacturer=manufacturers[0], model='Device Type 2', slug='device-type-2'),
            DeviceType(manufacturer=manufacturers[0], model='Device Type 3', slug='device-type-3'),
        )
        DeviceType.objects.bulk_create(device_types)

        roles = (
            DeviceRole(name='Device Role 1', slug='device-role-1'),
            DeviceRole(name='Device Role 2', slug='device-role-2'),
            DeviceRole(name='Device Role 3', slug='device-role-3'),
        )
        DeviceRole.objects.bulk_create(roles)

        regions = (
            Region(name='Region 1', slug='region-1'),
            Region(name='Region 2', slug='region-2'),
            Region(name='Region 3', slug='region-3'),
        )
        for region in regions:
            region.save()

        groups = (
            SiteGroup(name='Site Group 1', slug='site-group-1'),
            SiteGroup(name='Site Group 2', slug='site-group-2'),
            SiteGroup(name='Site Group 3', slug='site-group-3'),
        )
        for group in groups:
            group.save()

        sites = (
            Site(name='Site 1', slug='site-1', region=regions[0], group=groups[0]),
            Site(name='Site 2', slug='site-2', region=regions[1], group=groups[1]),
            Site(name='Site 3', slug='site-3', region=regions[2], group=groups[2]),
        )
        Site.objects.bulk_create(sites)

        locations = (
            Location(name='Location 1', slug='location-1', site=sites[0]),
            Location(name='Location 2', slug='location-2', site=sites[1]),
            Location(name='Location 3', slug='location-3', site=sites[2]),
        )
        for location in locations:
            location.save()

        racks = (
            Rack(name='Rack 1', site=sites[0]),
            Rack(name='Rack 2', site=sites[1]),
            Rack(name='Rack 3', site=sites[2]),
        )
        Rack.objects.bulk_create(racks)

        devices = (
            Device(name='Device 1', device_type=device_types[0], role=roles[0], site=sites[0], location=locations[0], rack=racks[0]),
            Device(name='Device 2', device_type=device_types[1], role=roles[1], site=sites[1], location=locations[1], rack=racks[1]),
            Device(name='Device 3', device_type=device_types[2], role=roles[2], site=sites[2], location=locations[2], rack=racks[2]),
        )
        Device.objects.bulk_create(devices)

        roles = (
            InventoryItemRole(name='Inventory Item Role 1', slug='inventory-item-role-1'),
            InventoryItemRole(name='Inventory Item Role 2', slug='inventory-item-role-2'),
            InventoryItemRole(name='Inventory Item Role 3', slug='inventory-item-role-3'),
        )
        InventoryItemRole.objects.bulk_create(roles)

        components = (
            Interface.objects.create(device=devices[0], name='Interface 1'),
            ConsolePort.objects.create(device=devices[1], name='Console Port 1'),
            ConsoleServerPort.objects.create(device=devices[2], name='Console Server Port 1'),
        )

        inventory_items = (
            InventoryItem(device=devices[0], role=roles[0], manufacturer=manufacturers[0], name='Inventory Item 1', label='A', part_id='1001', serial='ABC', asset_tag='1001', discovered=True, status=ModuleStatusChoices.STATUS_ACTIVE, description='First', component=components[0]),
            InventoryItem(device=devices[1], role=roles[1], manufacturer=manufacturers[1], name='Inventory Item 2', label='B', part_id='1002', serial='DEF', asset_tag='1002', discovered=True, status=ModuleStatusChoices.STATUS_PLANNED, description='Second', component=components[1]),
            InventoryItem(device=devices[2], role=roles[2], manufacturer=manufacturers[2], name='Inventory Item 3', label='C', part_id='1003', serial='GHI', asset_tag='1003', discovered=False, status=ModuleStatusChoices.STATUS_FAILED, description='Third', component=components[2]),
        )
        for i in inventory_items:
            i.save()

        child_inventory_items = (
            InventoryItem(device=devices[0], name='Inventory Item 1A', parent=inventory_items[0]),
            InventoryItem(device=devices[1], name='Inventory Item 2A', parent=inventory_items[1]),
            InventoryItem(device=devices[2], name='Inventory Item 3A', parent=inventory_items[2]),
        )
        for i in child_inventory_items:
            i.save()

    def test_name(self):
        params = {'name': ['Inventory Item 1', 'Inventory Item 2']}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_label(self):
        params = {'label': ['A', 'B']}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_part_id(self):
        params = {'part_id': ['1001', '1002']}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_asset_tag(self):
        params = {'asset_tag': ['1001', '1002']}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_discovered(self):
        # TODO: Fix boolean value
        params = {'discovered': True}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {'discovered': False}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 4)

    def test_region(self):
        regions = Region.objects.all()[:2]
        params = {'region_id': [regions[0].pk, regions[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 4)
        params = {'region': [regions[0].slug, regions[1].slug]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 4)

    def test_site_group(self):
        site_groups = SiteGroup.objects.all()[:2]
        params = {'site_group_id': [site_groups[0].pk, site_groups[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 4)
        params = {'site_group': [site_groups[0].slug, site_groups[1].slug]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 4)

    def test_site(self):
        sites = Site.objects.all()[:2]
        params = {'site_id': [sites[0].pk, sites[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 4)
        params = {'site': [sites[0].slug, sites[1].slug]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 4)

    def test_location(self):
        locations = Location.objects.all()[:2]
        params = {'location_id': [locations[0].pk, locations[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 4)
        params = {'location': [locations[0].slug, locations[1].slug]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 4)

    def test_rack(self):
        racks = Rack.objects.all()[:2]
        params = {'rack_id': [racks[0].pk, racks[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 4)
        params = {'rack': [racks[0].name, racks[1].name]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 4)

    def test_device_type(self):
        device_types = DeviceType.objects.all()[:2]
        params = {'device_type_id': [device_types[0].pk, device_types[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 4)
        params = {'device_type': [device_types[0].model, device_types[1].model]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 4)

    def test_device_role(self):
        role = DeviceRole.objects.all()[:2]
        params = {'device_role_id': [role[0].pk, role[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 4)
        params = {'device_role': [role[0].slug, role[1].slug]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 4)

    def test_device(self):
        devices = Device.objects.all()[:2]
        params = {'device_id': [devices[0].pk, devices[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 4)
        params = {'device': [devices[0].name, devices[1].name]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 4)

    def test_parent_id(self):
        parent_items = InventoryItem.objects.filter(parent__isnull=True)[:2]
        params = {'parent_id': [parent_items[0].pk, parent_items[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_role(self):
        roles = InventoryItemRole.objects.all()[:2]
        params = {'role_id': [roles[0].pk, roles[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {'role': [roles[0].slug, roles[1].slug]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_manufacturer(self):
        manufacturers = Manufacturer.objects.all()[:2]
        params = {'manufacturer_id': [manufacturers[0].pk, manufacturers[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {'manufacturer': [manufacturers[0].slug, manufacturers[1].slug]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_serial(self):
        params = {'serial': ['ABC', 'DEF']}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {'serial': ['abc', 'def']}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_component_type(self):
        params = {'component_type': 'dcim.interface'}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_status(self):
        params = {'status': [InventoryItemStatusChoices.STATUS_PLANNED, InventoryItemStatusChoices.STATUS_FAILED]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)


class InventoryItemRoleTestCase(TestCase, ChangeLoggedFilterSetTests):
    queryset = InventoryItemRole.objects.all()
    filterset = InventoryItemRoleFilterSet

    @classmethod
    def setUpTestData(cls):

        roles = (
            InventoryItemRole(
                name='Inventory Item Role 1',
                slug='inventory-item-role-1',
                color='ff0000',
                description='foobar1'
            ),
            InventoryItemRole(
                name='Inventory Item Role 2',
                slug='inventory-item-role-2',
                color='00ff00',
                description='foobar2'
            ),
            InventoryItemRole(
                name='Inventory Item Role 3',
                slug='inventory-item-role-3',
                color='0000ff',
                description='foobar3'
            ),
        )
        InventoryItemRole.objects.bulk_create(roles)

    def test_q(self):
        params = {'q': 'foobar1'}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_name(self):
        params = {'name': ['Inventory Item Role 1', 'Inventory Item Role 2']}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_slug(self):
        params = {'slug': ['inventory-item-role-1', 'inventory-item-role-2']}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_description(self):
        params = {'description': ['foobar1', 'foobar2']}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_color(self):
        params = {'color': ['ff0000', '00ff00']}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)


class VirtualChassisTestCase(TestCase, ChangeLoggedFilterSetTests):
    queryset = VirtualChassis.objects.all()
    filterset = VirtualChassisFilterSet

    @classmethod
    def setUpTestData(cls):

        manufacturer = Manufacturer.objects.create(name='Manufacturer 1', slug='manufacturer-1')
        device_type = DeviceType.objects.create(manufacturer=manufacturer, model='Model 1', slug='model-1')
        role = DeviceRole.objects.create(name='Device Role 1', slug='device-role-1')

        regions = (
            Region(name='Region 1', slug='region-1'),
            Region(name='Region 2', slug='region-2'),
            Region(name='Region 3', slug='region-3'),
        )
        for region in regions:
            region.save()

        groups = (
            SiteGroup(name='Site Group 1', slug='site-group-1'),
            SiteGroup(name='Site Group 2', slug='site-group-2'),
            SiteGroup(name='Site Group 3', slug='site-group-3'),
        )
        for group in groups:
            group.save()

        sites = (
            Site(name='Site 1', slug='site-1', region=regions[0], group=groups[0]),
            Site(name='Site 2', slug='site-2', region=regions[1], group=groups[1]),
            Site(name='Site 3', slug='site-3', region=regions[2], group=groups[2]),
        )
        Site.objects.bulk_create(sites)

        devices = (
            Device(name='Device 1', device_type=device_type, role=role, site=sites[0], vc_position=1),
            Device(name='Device 2', device_type=device_type, role=role, site=sites[0], vc_position=2),
            Device(name='Device 3', device_type=device_type, role=role, site=sites[1], vc_position=1),
            Device(name='Device 4', device_type=device_type, role=role, site=sites[1], vc_position=2),
            Device(name='Device 5', device_type=device_type, role=role, site=sites[2], vc_position=1),
            Device(name='Device 6', device_type=device_type, role=role, site=sites[2], vc_position=2),
        )
        Device.objects.bulk_create(devices)

        virtual_chassis = (
            VirtualChassis(name='VC 1', master=devices[0], domain='Domain 1', description='foobar1'),
            VirtualChassis(name='VC 2', master=devices[2], domain='Domain 2', description='foobar2'),
            VirtualChassis(name='VC 3', master=devices[4], domain='Domain 3', description='foobar3'),
        )
        VirtualChassis.objects.bulk_create(virtual_chassis)

        Device.objects.filter(pk=devices[1].pk).update(virtual_chassis=virtual_chassis[0])
        Device.objects.filter(pk=devices[3].pk).update(virtual_chassis=virtual_chassis[1])
        Device.objects.filter(pk=devices[5].pk).update(virtual_chassis=virtual_chassis[2])

    def test_q(self):
        params = {'q': 'foobar1'}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_domain(self):
        params = {'domain': ['Domain 1', 'Domain 2']}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_master(self):
        masters = Device.objects.all()
        params = {'master_id': [masters[0].pk, masters[2].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {'master': [masters[0].name, masters[2].name]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_name(self):
        params = {'name': ['VC 1', 'VC 2']}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_description(self):
        params = {'description': ['foobar1', 'foobar2']}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_region(self):
        regions = Region.objects.all()[:2]
        params = {'region_id': [regions[0].pk, regions[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {'region': [regions[0].slug, regions[1].slug]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_site_group(self):
        site_groups = SiteGroup.objects.all()[:2]
        params = {'site_group_id': [site_groups[0].pk, site_groups[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {'site_group': [site_groups[0].slug, site_groups[1].slug]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_site(self):
        sites = Site.objects.all()[:2]
        params = {'site_id': [sites[0].pk, sites[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {'site': [sites[0].slug, sites[1].slug]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)


class CableTestCase(TestCase, ChangeLoggedFilterSetTests):
    queryset = Cable.objects.all()
    filterset = CableFilterSet

    @classmethod
    def setUpTestData(cls):

        sites = (
            Site(name='Site 1', slug='site-1'),
            Site(name='Site 2', slug='site-2'),
            Site(name='Site 3', slug='site-3'),
        )
        Site.objects.bulk_create(sites)

        locations = (
            Location(name='Location 1', site=sites[0], slug='location-1'),
            Location(name='Location 2', site=sites[1], slug='location-1'),
            Location(name='Location 3', site=sites[2], slug='location-1'),
        )
        for location in locations:
            location.save()

        racks = (
            Rack(name='Rack 1', site=sites[0], location=locations[0]),
            Rack(name='Rack 2', site=sites[1], location=locations[1]),
            Rack(name='Rack 3', site=sites[2], location=locations[2]),
        )
        Rack.objects.bulk_create(racks)

        tenants = (
            Tenant(name='Tenant 1', slug='tenant-1'),
            Tenant(name='Tenant 2', slug='tenant-2'),
            Tenant(name='Tenant 3', slug='tenant-3'),
        )
        Tenant.objects.bulk_create(tenants)

        manufacturer = Manufacturer.objects.create(name='Manufacturer 1', slug='manufacturer-1')
        device_type = DeviceType.objects.create(manufacturer=manufacturer, model='Model 1', slug='model-1')
        role = DeviceRole.objects.create(name='Device Role 1', slug='device-role-1')

        devices = (
            Device(name='Device 1', device_type=device_type, role=role, site=sites[0], rack=racks[0], location=locations[0], position=1),
            Device(name='Device 2', device_type=device_type, role=role, site=sites[0], rack=racks[0], location=locations[0], position=2),
            Device(name='Device 3', device_type=device_type, role=role, site=sites[1], rack=racks[1], location=locations[1], position=1),
            Device(name='Device 4', device_type=device_type, role=role, site=sites[1], rack=racks[1], location=locations[1], position=2),
            Device(name='Device 5', device_type=device_type, role=role, site=sites[2], rack=racks[2], location=locations[2], position=1),
            Device(name='Device 6', device_type=device_type, role=role, site=sites[2], rack=racks[2], location=locations[2], position=2),
        )
        Device.objects.bulk_create(devices)

        interfaces = (
            Interface(device=devices[0], name='Interface 1', type=InterfaceTypeChoices.TYPE_1GE_FIXED),
            Interface(device=devices[0], name='Interface 2', type=InterfaceTypeChoices.TYPE_1GE_FIXED),
            Interface(device=devices[1], name='Interface 3', type=InterfaceTypeChoices.TYPE_1GE_FIXED),
            Interface(device=devices[1], name='Interface 4', type=InterfaceTypeChoices.TYPE_1GE_FIXED),
            Interface(device=devices[2], name='Interface 5', type=InterfaceTypeChoices.TYPE_1GE_FIXED),
            Interface(device=devices[2], name='Interface 6', type=InterfaceTypeChoices.TYPE_1GE_FIXED),
            Interface(device=devices[3], name='Interface 7', type=InterfaceTypeChoices.TYPE_1GE_FIXED),
            Interface(device=devices[3], name='Interface 8', type=InterfaceTypeChoices.TYPE_1GE_FIXED),
            Interface(device=devices[4], name='Interface 9', type=InterfaceTypeChoices.TYPE_1GE_FIXED),
            Interface(device=devices[4], name='Interface 10', type=InterfaceTypeChoices.TYPE_1GE_FIXED),
            Interface(device=devices[5], name='Interface 11', type=InterfaceTypeChoices.TYPE_1GE_FIXED),
            Interface(device=devices[5], name='Interface 12', type=InterfaceTypeChoices.TYPE_1GE_FIXED),
            Interface(device=devices[5], name='Interface 13', type=InterfaceTypeChoices.TYPE_1GE_FIXED),
        )
        Interface.objects.bulk_create(interfaces)

        console_port = ConsolePort.objects.create(device=devices[0], name='Console Port 1')
        console_server_port = ConsoleServerPort.objects.create(device=devices[0], name='Console Server Port 1')
        power_port = PowerPort.objects.create(device=devices[0], name='Power Port 1')
        power_outlet = PowerOutlet.objects.create(device=devices[0], name='Power Outlet 1')
        rear_port = RearPort.objects.create(device=devices[0], name='Rear Port 1', positions=1)
        front_port = FrontPort.objects.create(
            device=devices[0],
            name='Front Port 1',
            rear_port=rear_port,
            rear_port_position=1
        )

        power_panel = PowerPanel.objects.create(name='Power Panel 1', site=sites[0])
        power_feed = PowerFeed.objects.create(name='Power Feed 1', power_panel=power_panel)

        provider = Provider.objects.create(name='Provider 1', slug='provider-1')
        circuit_type = CircuitType.objects.create(name='Circuit Type 1', slug='circuit-type-1')
        circuit = Circuit.objects.create(cid='Circuit 1', provider=provider, type=circuit_type)
        circuit_termination = CircuitTermination.objects.create(circuit=circuit, term_side='A', termination=sites[0])

        # Cables
        cables = (
            Cable(
                a_terminations=[interfaces[1]],
                b_terminations=[interfaces[2]],
                label='Cable 1',
                type=CableTypeChoices.TYPE_CAT3,
                tenant=tenants[0],
                status=LinkStatusChoices.STATUS_CONNECTED,
                color='aa1409',
                length=10,
                length_unit=CableLengthUnitChoices.UNIT_FOOT,
                description='foobar1'
            ),
            Cable(
                a_terminations=[interfaces[3]],
                b_terminations=[interfaces[4]],
                label='Cable 2',
                type=CableTypeChoices.TYPE_CAT3,
                tenant=tenants[0],
                status=LinkStatusChoices.STATUS_CONNECTED,
                color='aa1409',
                length=20,
                length_unit=CableLengthUnitChoices.UNIT_FOOT,
                description='foobar2'
            ),
            Cable(
                a_terminations=[interfaces[5]],
                b_terminations=[interfaces[6]],
                label='Cable 3',
                type=CableTypeChoices.TYPE_CAT5E,
                tenant=tenants[1],
                status=LinkStatusChoices.STATUS_CONNECTED,
                color='f44336',
                length=30,
                length_unit=CableLengthUnitChoices.UNIT_FOOT,
                description='foobar3'
            ),
            Cable(
                a_terminations=[interfaces[7]],
                b_terminations=[interfaces[8]],
                label='Cable 4',
                type=CableTypeChoices.TYPE_CAT5E,
                tenant=tenants[1],
                status=LinkStatusChoices.STATUS_PLANNED,
                color='f44336',
                length=40,
                length_unit=CableLengthUnitChoices.UNIT_FOOT
            ),
            Cable(
                a_terminations=[interfaces[9]],
                b_terminations=[interfaces[10]],
                label='Cable 5',
                type=CableTypeChoices.TYPE_CAT6,
                tenant=tenants[2],
                status=LinkStatusChoices.STATUS_PLANNED,
                color='e91e63',
                length=10,
                length_unit=CableLengthUnitChoices.UNIT_METER
            ),
            Cable(
                a_terminations=[interfaces[11]],
                b_terminations=[interfaces[0]],
                label='Cable 6',
                type=CableTypeChoices.TYPE_CAT6,
                tenant=tenants[2],
                status=LinkStatusChoices.STATUS_PLANNED,
                color='e91e63',
                length=20,
                length_unit=CableLengthUnitChoices.UNIT_METER
            ),

            # Cables for filtering by termination object
            Cable(
                a_terminations=[console_port],
                label='Cable 7'
            ),
            Cable(
                a_terminations=[console_server_port],
                label='Cable 8'
            ),
            Cable(
                a_terminations=[power_port],
                label='Cable 9'
            ),
            Cable(
                a_terminations=[power_outlet],
                label='Cable 10'
            ),
            Cable(
                a_terminations=[front_port],
                label='Cable 11'
            ),
            Cable(
                a_terminations=[rear_port],
                label='Cable 12'
            ),
            Cable(
                a_terminations=[power_feed],
                label='Cable 13'
            ),
            Cable(
                a_terminations=[circuit_termination],
                label='Cable 14'
            ),
        )
        for cable in cables:
            cable.save()

    def test_q(self):
        params = {'q': 'foobar1'}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_label(self):
        params = {'label': ['Cable 1', 'Cable 2']}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_length(self):
        params = {'length': [10, 20]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 4)

    def test_length_unit(self):
        params = {'length_unit': CableLengthUnitChoices.UNIT_FOOT}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 4)

    def test_type(self):
        params = {'type': [CableTypeChoices.TYPE_CAT3, CableTypeChoices.TYPE_CAT5E]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 4)
        params = {'type__empty': 'true'}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 8)
        params = {'type__empty': 'false'}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 6)

    def test_status(self):
        params = {'status': [LinkStatusChoices.STATUS_CONNECTED]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 11)
        params = {'status': [LinkStatusChoices.STATUS_PLANNED]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 3)

    def test_color(self):
        params = {'color': ['aa1409', 'f44336']}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 4)

    def test_description(self):
        params = {'description': ['foobar1', 'foobar2']}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_device(self):
        devices = Device.objects.all()[:2]
        params = {'device_id': [devices[0].pk, devices[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 9)
        params = {'device': [devices[0].name, devices[1].name]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 9)

    def test_rack(self):
        racks = Rack.objects.all()[:2]
        params = {'rack_id': [racks[0].pk, racks[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 11)
        params = {'rack': [racks[0].name, racks[1].name]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 11)

    def test_location(self):
        locations = Location.objects.all()[:2]
        params = {'location_id': [locations[0].pk, locations[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 11)
        params = {'location': [locations[0].name, locations[1].name]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 11)

    def test_site(self):
        site = Site.objects.all()[:2]
        params = {'site_id': [site[0].pk, site[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 11)
        params = {'site': [site[0].slug, site[1].slug]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 11)

    def test_tenant(self):
        tenant = Tenant.objects.all()[:2]
        params = {'tenant_id': [tenant[0].pk, tenant[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 4)
        params = {'tenant': [tenant[0].slug, tenant[1].slug]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 4)

    def test_termination_types(self):
        params = {'termination_a_type': 'dcim.consoleport'}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)
        # params = {'termination_b_type': 'dcim.consoleserverport'}
        # self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_termination_ids(self):
        interface_ids = CableTermination.objects.filter(
            cable__in=Cable.objects.all()[:3],
            cable_end='A'
        ).values_list('termination_id', flat=True)
        params = {
            'termination_a_type': 'dcim.interface',
            'termination_a_id': list(interface_ids),
        }
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 3)

    def test_unterminated(self):
        params = {'unterminated': True}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 8)
        params = {'unterminated': False}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 6)

    def test_consoleport(self):
        params = {'consoleport_id': [ConsolePort.objects.first().pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_consoleserverport(self):
        params = {'consoleserverport_id': [ConsoleServerPort.objects.first().pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_powerport(self):
        params = {'powerport_id': [PowerPort.objects.first().pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_poweroutlet(self):
        params = {'poweroutlet_id': [PowerOutlet.objects.first().pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_frontport(self):
        params = {'frontport_id': [FrontPort.objects.first().pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_rearport(self):
        params = {'rearport_id': [RearPort.objects.first().pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_powerfeed(self):
        params = {'powerfeed_id': [PowerFeed.objects.first().pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_circuittermination(self):
        params = {'circuittermination_id': [CircuitTermination.objects.first().pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)


class PowerPanelTestCase(TestCase, ChangeLoggedFilterSetTests):
    queryset = PowerPanel.objects.all()
    filterset = PowerPanelFilterSet

    @classmethod
    def setUpTestData(cls):

        regions = (
            Region(name='Region 1', slug='region-1'),
            Region(name='Region 2', slug='region-2'),
            Region(name='Region 3', slug='region-3'),
        )
        for region in regions:
            region.save()

        groups = (
            SiteGroup(name='Site Group 1', slug='site-group-1'),
            SiteGroup(name='Site Group 2', slug='site-group-2'),
            SiteGroup(name='Site Group 3', slug='site-group-3'),
        )
        for group in groups:
            group.save()

        sites = (
            Site(name='Site 1', slug='site-1', region=regions[0], group=groups[0]),
            Site(name='Site 2', slug='site-2', region=regions[1], group=groups[1]),
            Site(name='Site 3', slug='site-3', region=regions[2], group=groups[2]),
        )
        Site.objects.bulk_create(sites)

        locations = (
            Location(name='Location 1', slug='location-1', site=sites[0]),
            Location(name='Location 2', slug='location-2', site=sites[1]),
            Location(name='Location 3', slug='location-3', site=sites[2]),
        )
        for location in locations:
            location.save()

        power_panels = (
            PowerPanel(name='Power Panel 1', site=sites[0], location=locations[0], description='foobar1'),
            PowerPanel(name='Power Panel 2', site=sites[1], location=locations[1], description='foobar2'),
            PowerPanel(name='Power Panel 3', site=sites[2], location=locations[2], description='foobar3'),
        )
        PowerPanel.objects.bulk_create(power_panels)

    def test_q(self):
        params = {'q': 'foobar1'}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_name(self):
        params = {'name': ['Power Panel 1', 'Power Panel 2']}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_description(self):
        params = {'description': ['foobar1', 'foobar2']}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_region(self):
        regions = Region.objects.all()[:2]
        params = {'region_id': [regions[0].pk, regions[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {'region': [regions[0].slug, regions[1].slug]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_site_group(self):
        site_groups = SiteGroup.objects.all()[:2]
        params = {'site_group_id': [site_groups[0].pk, site_groups[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {'site_group': [site_groups[0].slug, site_groups[1].slug]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_site(self):
        sites = Site.objects.all()[:2]
        params = {'site_id': [sites[0].pk, sites[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {'site': [sites[0].slug, sites[1].slug]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_location(self):
        locations = Location.objects.all()[:2]
        params = {'location_id': [locations[0].pk, locations[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)


class PowerFeedTestCase(TestCase, ChangeLoggedFilterSetTests):
    queryset = PowerFeed.objects.all()
    filterset = PowerFeedFilterSet

    @classmethod
    def setUpTestData(cls):

        regions = (
            Region(name='Region 1', slug='region-1'),
            Region(name='Region 2', slug='region-2'),
            Region(name='Region 3', slug='region-3'),
        )
        for region in regions:
            region.save()

        groups = (
            SiteGroup(name='Site Group 1', slug='site-group-1'),
            SiteGroup(name='Site Group 2', slug='site-group-2'),
            SiteGroup(name='Site Group 3', slug='site-group-3'),
        )
        for group in groups:
            group.save()

        sites = (
            Site(name='Site 1', slug='site-1', region=regions[0], group=groups[0]),
            Site(name='Site 2', slug='site-2', region=regions[1], group=groups[1]),
            Site(name='Site 3', slug='site-3', region=regions[2], group=groups[2]),
        )
        Site.objects.bulk_create(sites)

        racks = (
            Rack(name='Rack 1', site=sites[0]),
            Rack(name='Rack 2', site=sites[1]),
            Rack(name='Rack 3', site=sites[2]),
        )
        Rack.objects.bulk_create(racks)

        tenant_groups = (
            TenantGroup(name='Tenant group 1', slug='tenant-group-1'),
            TenantGroup(name='Tenant group 2', slug='tenant-group-2'),
            TenantGroup(name='Tenant group 3', slug='tenant-group-3'),
        )
        for tenantgroup in tenant_groups:
            tenantgroup.save()

        tenants = (
            Tenant(name='Tenant 1', slug='tenant-1', group=tenant_groups[0]),
            Tenant(name='Tenant 2', slug='tenant-2', group=tenant_groups[1]),
            Tenant(name='Tenant 3', slug='tenant-3', group=tenant_groups[2]),
        )
        Tenant.objects.bulk_create(tenants)

        power_panels = (
            PowerPanel(name='Power Panel 1', site=sites[0]),
            PowerPanel(name='Power Panel 2', site=sites[1]),
            PowerPanel(name='Power Panel 3', site=sites[2]),
        )
        PowerPanel.objects.bulk_create(power_panels)

        power_feeds = (
            PowerFeed(
                power_panel=power_panels[0],
                rack=racks[0],
                name='Power Feed 1',
                tenant=tenants[0],
                status=PowerFeedStatusChoices.STATUS_ACTIVE,
                type=PowerFeedTypeChoices.TYPE_PRIMARY,
                supply=PowerFeedSupplyChoices.SUPPLY_AC,
                phase=PowerFeedPhaseChoices.PHASE_3PHASE,
                voltage=100,
                amperage=100,
                max_utilization=10,
                description='foobar1'
            ),
            PowerFeed(
                power_panel=power_panels[1],
                rack=racks[1],
                name='Power Feed 2',
                tenant=tenants[1],
                status=PowerFeedStatusChoices.STATUS_FAILED,
                type=PowerFeedTypeChoices.TYPE_PRIMARY,
                supply=PowerFeedSupplyChoices.SUPPLY_AC,
                phase=PowerFeedPhaseChoices.PHASE_3PHASE,
                voltage=200,
                amperage=200,
                max_utilization=20,
                description='foobar2'
            ),
            PowerFeed(
                power_panel=power_panels[2],
                rack=racks[2],
                name='Power Feed 3',
                tenant=tenants[2],
                status=PowerFeedStatusChoices.STATUS_OFFLINE,
                type=PowerFeedTypeChoices.TYPE_REDUNDANT,
                supply=PowerFeedSupplyChoices.SUPPLY_DC,
                phase=PowerFeedPhaseChoices.PHASE_SINGLE,
                voltage=300,
                amperage=300,
                max_utilization=30,
                description='foobar3'
            ),
        )
        PowerFeed.objects.bulk_create(power_feeds)

        manufacturer = Manufacturer.objects.create(name='Manufacturer', slug='manufacturer')
        device_type = DeviceType.objects.create(manufacturer=manufacturer, model='Model', slug='model')
        role = DeviceRole.objects.create(name='Device Role', slug='device-role')
        device = Device.objects.create(name='Device', device_type=device_type, role=role, site=sites[0])
        power_ports = [
            PowerPort(device=device, name='Power Port 1'),
            PowerPort(device=device, name='Power Port 2'),
        ]
        PowerPort.objects.bulk_create(power_ports)
        Cable(a_terminations=[power_feeds[0]], b_terminations=[power_ports[0]]).save()
        Cable(a_terminations=[power_feeds[1]], b_terminations=[power_ports[1]]).save()

    def test_q(self):
        params = {'q': 'foobar1'}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_name(self):
        params = {'name': ['Power Feed 1', 'Power Feed 2']}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_status(self):
        params = {'status': [PowerFeedStatusChoices.STATUS_ACTIVE, PowerFeedStatusChoices.STATUS_FAILED]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_type(self):
        params = {'type': PowerFeedTypeChoices.TYPE_PRIMARY}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_supply(self):
        params = {'supply': PowerFeedSupplyChoices.SUPPLY_AC}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_phase(self):
        params = {'phase': PowerFeedPhaseChoices.PHASE_3PHASE}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_voltage(self):
        params = {'voltage': [100, 200]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_amperage(self):
        params = {'amperage': [100, 200]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_max_utilization(self):
        params = {'max_utilization': [10, 20]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_description(self):
        params = {'description': ['foobar1', 'foobar2']}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_region(self):
        regions = Region.objects.all()[:2]
        params = {'region_id': [regions[0].pk, regions[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {'region': [regions[0].slug, regions[1].slug]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_site_group(self):
        site_groups = SiteGroup.objects.all()[:2]
        params = {'site_group_id': [site_groups[0].pk, site_groups[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {'site_group': [site_groups[0].slug, site_groups[1].slug]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_site(self):
        sites = Site.objects.all()[:2]
        params = {'site_id': [sites[0].pk, sites[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {'site': [sites[0].slug, sites[1].slug]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_power_panel_id(self):
        power_panels = PowerPanel.objects.all()[:2]
        params = {'power_panel_id': [power_panels[0].pk, power_panels[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_rack_id(self):
        racks = Rack.objects.all()[:2]
        params = {'rack_id': [racks[0].pk, racks[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_cabled(self):
        params = {'cabled': True}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {'cabled': False}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_connected(self):
        params = {'connected': True}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {'connected': False}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_tenant(self):
        tenants = Tenant.objects.all()[:2]
        params = {'tenant_id': [tenants[0].pk, tenants[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {'tenant': [tenants[0].slug, tenants[1].slug]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_tenant_group(self):
        tenant_groups = TenantGroup.objects.all()[:2]
        params = {'tenant_group_id': [tenant_groups[0].pk, tenant_groups[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {'tenant_group': [tenant_groups[0].slug, tenant_groups[1].slug]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)


class VirtualDeviceContextTestCase(TestCase, ChangeLoggedFilterSetTests):
    queryset = VirtualDeviceContext.objects.all()
    filterset = VirtualDeviceContextFilterSet
    ignore_fields = ('primary_ip4', 'primary_ip6')

    @classmethod
    def setUpTestData(cls):

        sites = (
            Site(name='Site 1', slug='site-1'),
            Site(name='Site 2', slug='site-2'),
            Site(name='Site 3', slug='site-3'),
        )
        Site.objects.bulk_create(sites)

        tenants = (
            Tenant(name='Tenant 1', slug='tenant-1'),
            Tenant(name='Tenant 2', slug='tenant-2'),
            Tenant(name='Tenant 3', slug='tenant-3'),
        )
        Tenant.objects.bulk_create(tenants)

        manufacturer = Manufacturer.objects.create(name='Manufacturer 1', slug='manufacturer-1')
        device_type = DeviceType.objects.create(manufacturer=manufacturer, model='Model 1', slug='model-1')
        role = DeviceRole.objects.create(name='Device Role 1', slug='device-role-1')

        devices = (
            Device(name='Device 1', device_type=device_type, role=role, site=sites[0]),
            Device(name='Device 2', device_type=device_type, role=role, site=sites[1]),
            Device(name='Device 3', device_type=device_type, role=role, site=sites[2]),
        )
        Device.objects.bulk_create(devices)

        vdcs = (
            VirtualDeviceContext(
                device=devices[0],
                name='VDC 1',
                identifier=1,
                status=VirtualDeviceContextStatusChoices.STATUS_ACTIVE,
                description='foobar1'
            ),
            VirtualDeviceContext(
                device=devices[0],
                name='VDC 2',
                identifier=2,
                status=VirtualDeviceContextStatusChoices.STATUS_PLANNED,
                description='foobar2'
            ),
            VirtualDeviceContext(
                device=devices[1],
                name='VDC 1',
                status=VirtualDeviceContextStatusChoices.STATUS_OFFLINE,
                description='foobar3'
            ),
            VirtualDeviceContext(
                device=devices[1],
                name='VDC 2',
                status=VirtualDeviceContextStatusChoices.STATUS_PLANNED
            ),
            VirtualDeviceContext(
                device=devices[2],
                name='VDC 1',
                status=VirtualDeviceContextStatusChoices.STATUS_ACTIVE
            ),
            VirtualDeviceContext(
                device=devices[2],
                name='VDC 2',
                status=VirtualDeviceContextStatusChoices.STATUS_ACTIVE
            ),
        )
        VirtualDeviceContext.objects.bulk_create(vdcs)

        interfaces = (
            Interface(device=devices[0], name='Interface 1', type=InterfaceTypeChoices.TYPE_VIRTUAL),
            Interface(device=devices[0], name='Interface 2', type=InterfaceTypeChoices.TYPE_VIRTUAL),
            Interface(device=devices[1], name='Interface 3', type=InterfaceTypeChoices.TYPE_VIRTUAL),
            Interface(device=devices[1], name='Interface 4', type=InterfaceTypeChoices.TYPE_VIRTUAL),
            Interface(device=devices[2], name='Interface 5', type=InterfaceTypeChoices.TYPE_VIRTUAL),
            Interface(device=devices[2], name='Interface 6', type=InterfaceTypeChoices.TYPE_VIRTUAL),
        )
        Interface.objects.bulk_create(interfaces)
        interfaces[0].vdcs.set([vdcs[0]])
        interfaces[1].vdcs.set([vdcs[1]])
        interfaces[2].vdcs.set([vdcs[2]])
        interfaces[3].vdcs.set([vdcs[3]])
        interfaces[4].vdcs.set([vdcs[4]])
        interfaces[5].vdcs.set([vdcs[5]])

        ip_addresses = (
            IPAddress(assigned_object=interfaces[0], address='10.1.1.1/24'),
            IPAddress(assigned_object=interfaces[1], address='10.1.1.2/24'),
            IPAddress(assigned_object=None, address='10.1.1.3/24'),
            IPAddress(assigned_object=interfaces[0], address='2001:db8::1/64'),
            IPAddress(assigned_object=interfaces[1], address='2001:db8::2/64'),
            IPAddress(assigned_object=None, address='2001:db8::3/64'),
        )
        IPAddress.objects.bulk_create(ip_addresses)
        vdcs[0].primary_ip4 = ip_addresses[0]
        vdcs[0].primary_ip6 = ip_addresses[3]
        vdcs[0].save()
        vdcs[1].primary_ip4 = ip_addresses[1]
        vdcs[1].primary_ip6 = ip_addresses[4]
        vdcs[1].save()

    def test_q(self):
        params = {'q': 'foobar1'}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_device(self):
        devices = Device.objects.filter(name__in=['Device 1', 'Device 2'])
        params = {'device': [devices[0].name, devices[1].name]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 6)
        params = {'device_id': [devices[0].pk, devices[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 4)

    def test_status(self):
        params = {'status': ['active']}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 3)

    def test_description(self):
        params = {'description': ['foobar1', 'foobar2']}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_interface(self):
        interfaces = Interface.objects.filter(name__in=['Interface 1', 'Interface 3'])
        params = {'interface_id': [interfaces[0].pk, interfaces[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_has_primary_ip(self):
        params = {'has_primary_ip': True}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {'has_primary_ip': False}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 4)

    def test_primary_ip4(self):
        addresses = IPAddress.objects.filter(address__family=4)
        params = {'primary_ip4_id': [addresses[0].pk, addresses[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {'primary_ip4_id': [addresses[2].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 0)

    def test_primary_ip6(self):
        addresses = IPAddress.objects.filter(address__family=6)
        params = {'primary_ip6_id': [addresses[0].pk, addresses[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {'primary_ip6_id': [addresses[2].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 0)


class MACAddressTestCase(TestCase, ChangeLoggedFilterSetTests):
    queryset = MACAddress.objects.all()
    filterset = MACAddressFilterSet

    @classmethod
    def setUpTestData(cls):
        devices = (
            create_test_device('Device 1'),
            create_test_device('Device 2'),
            create_test_device('Device 3'),
        )
        interfaces = (
            Interface(device=devices[0], name='Interface 1', type=InterfaceTypeChoices.TYPE_1GE_FIXED),
            Interface(device=devices[1], name='Interface 2', type=InterfaceTypeChoices.TYPE_1GE_FIXED),
            Interface(device=devices[2], name='Interface 3', type=InterfaceTypeChoices.TYPE_1GE_FIXED),
        )
        Interface.objects.bulk_create(interfaces)

        virtual_machines = (
            create_test_virtualmachine('Virtual Machine 1'),
            create_test_virtualmachine('Virtual Machine 2'),
            create_test_virtualmachine('Virtual Machine 3'),
        )
        vm_interfaces = (
            VMInterface(virtual_machine=virtual_machines[0], name='Interface 1'),
            VMInterface(virtual_machine=virtual_machines[1], name='Interface 2'),
            VMInterface(virtual_machine=virtual_machines[2], name='Interface 3'),
        )
        VMInterface.objects.bulk_create(vm_interfaces)

        mac_addresses = (
            # Device MACs
            MACAddress(mac_address='00-00-00-01-01-01', assigned_object=interfaces[0]),
            MACAddress(mac_address='00-00-00-02-01-01', assigned_object=interfaces[1]),
            MACAddress(mac_address='00-00-00-03-01-01', assigned_object=interfaces[2]),
            MACAddress(mac_address='00-00-00-03-01-02', assigned_object=interfaces[2]),
            # VM MACs
            MACAddress(mac_address='00-00-00-04-01-01', assigned_object=vm_interfaces[0]),
            MACAddress(mac_address='00-00-00-05-01-01', assigned_object=vm_interfaces[1]),
            MACAddress(mac_address='00-00-00-06-01-01', assigned_object=vm_interfaces[2]),
            MACAddress(mac_address='00-00-00-06-01-02', assigned_object=vm_interfaces[2]),
        )
        MACAddress.objects.bulk_create(mac_addresses)

    def test_mac_address(self):
        params = {'mac_address': ['00-00-00-01-01-01', '00-00-00-02-01-01']}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_device(self):
        devices = Device.objects.all()[:2]
        params = {'device_id': [devices[0].pk, devices[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {'device': [devices[0].name, devices[1].name]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_virtual_machine(self):
        virtual_machines = VirtualMachine.objects.all()[:2]
        params = {'virtual_machine_id': [virtual_machines[0].pk, virtual_machines[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {'virtual_machine': [virtual_machines[0].name, virtual_machines[1].name]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_interface(self):
        interfaces = Interface.objects.all()[:2]
        params = {'interface_id': [interfaces[0].pk, interfaces[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {'interface': [interfaces[0].name, interfaces[1].name]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_vminterface(self):
        vm_interfaces = VMInterface.objects.all()[:2]
        params = {'vminterface_id': [vm_interfaces[0].pk, vm_interfaces[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {'vminterface': [vm_interfaces[0].name, vm_interfaces[1].name]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
