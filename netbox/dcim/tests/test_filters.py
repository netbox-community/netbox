from django.contrib.auth.models import User
from django.test import TestCase

from dcim.constants import *
from dcim.filters import (
    RackFilter, RackGroupFilter, RackReservationFilter, RackRoleFilter, RegionFilter, SiteFilter,
)
from dcim.models import (
    Rack, RackGroup, RackReservation, RackRole, Region, Site,
)


class RegionTestCase(TestCase):
    queryset = Region.objects.all()

    @classmethod
    def setUpTestData(cls):

        regions = (
            Region(name='Region 1', slug='region-1'),
            Region(name='Region 2', slug='region-2'),
            Region(name='Region 3', slug='region-3'),
        )
        for region in regions:
            region.save()

        child_regions = (
            Region(name='Region 1A', slug='region-1a', parent=regions[0]),
            Region(name='Region 1B', slug='region-1b', parent=regions[0]),
            Region(name='Region 2A', slug='region-2a', parent=regions[1]),
            Region(name='Region 2B', slug='region-2b', parent=regions[1]),
            Region(name='Region 3A', slug='region-3a', parent=regions[2]),
            Region(name='Region 3B', slug='region-3b', parent=regions[2]),
        )
        for region in child_regions:
            region.save()

    def test_id(self):
        id_list = self.queryset.values_list('id', flat=True)[:2]
        params = {'id': [str(id) for id in id_list]}
        self.assertEqual(RegionFilter(params, self.queryset).qs.count(), 2)

    def test_name(self):
        params = {'name': ['Region 1', 'Region 2']}
        self.assertEqual(RegionFilter(params, self.queryset).qs.count(), 2)

    def test_slug(self):
        params = {'slug': ['region-1', 'region-2']}
        self.assertEqual(RegionFilter(params, self.queryset).qs.count(), 2)

    def test_parent(self):
        parent_regions = Region.objects.filter(parent__isnull=True)[:2]
        params = {'parent_id': [parent_regions[0].pk, parent_regions[1].pk]}
        self.assertEqual(RegionFilter(params, self.queryset).qs.count(), 4)
        params = {'parent': [parent_regions[0].slug, parent_regions[1].slug]}
        self.assertEqual(RegionFilter(params, self.queryset).qs.count(), 4)


class SiteTestCase(TestCase):
    queryset = Site.objects.all()

    @classmethod
    def setUpTestData(cls):

        regions = (
            Region(name='Region 1', slug='region-1'),
            Region(name='Region 2', slug='region-2'),
            Region(name='Region 3', slug='region-3'),
        )
        for region in regions:
            region.save()

        sites = (
            Site(name='Site 1', slug='site-1', region=regions[0], status=SITE_STATUS_ACTIVE, facility='Facility 1', asn=65001, latitude=10, longitude=10, contact_name='Contact 1', contact_phone='123-555-0001', contact_email='contact1@example.com'),
            Site(name='Site 2', slug='site-2', region=regions[1], status=SITE_STATUS_PLANNED, facility='Facility 2', asn=65002, latitude=20, longitude=20, contact_name='Contact 2', contact_phone='123-555-0002', contact_email='contact2@example.com'),
            Site(name='Site 3', slug='site-3', region=regions[2], status=SITE_STATUS_RETIRED, facility='Facility 3', asn=65003, latitude=30, longitude=30, contact_name='Contact 3', contact_phone='123-555-0003', contact_email='contact3@example.com'),
        )
        Site.objects.bulk_create(sites)

    def test_id(self):
        id_list = self.queryset.values_list('id', flat=True)[:2]
        params = {'id': [str(id) for id in id_list]}
        self.assertEqual(SiteFilter(params, self.queryset).qs.count(), 2)

    def test_name(self):
        params = {'name': ['Site 1', 'Site 2']}
        self.assertEqual(SiteFilter(params, self.queryset).qs.count(), 2)

    def test_slug(self):
        params = {'slug': ['site-1', 'site-2']}
        self.assertEqual(SiteFilter(params, self.queryset).qs.count(), 2)

    def test_facility(self):
        params = {'facility': ['Facility 1', 'Facility 2']}
        self.assertEqual(SiteFilter(params, self.queryset).qs.count(), 2)

    def test_asn(self):
        params = {'asn': [65001, 65002]}
        self.assertEqual(SiteFilter(params, self.queryset).qs.count(), 2)

    def test_latitude(self):
        params = {'latitude': [10, 20]}
        self.assertEqual(SiteFilter(params, self.queryset).qs.count(), 2)

    def test_longitude(self):
        params = {'longitude': [10, 20]}
        self.assertEqual(SiteFilter(params, self.queryset).qs.count(), 2)

    def test_contact_name(self):
        params = {'contact_name': ['Contact 1', 'Contact 2']}
        self.assertEqual(SiteFilter(params, self.queryset).qs.count(), 2)

    def test_contact_phone(self):
        params = {'contact_phone': ['123-555-0001', '123-555-0002']}
        self.assertEqual(SiteFilter(params, self.queryset).qs.count(), 2)

    def test_contact_email(self):
        params = {'contact_email': ['contact1@example.com', 'contact2@example.com']}
        self.assertEqual(SiteFilter(params, self.queryset).qs.count(), 2)

    def test_id__in(self):
        id_list = self.queryset.values_list('id', flat=True)[:2]
        params = {'id__in': ','.join([str(id) for id in id_list])}
        self.assertEqual(SiteFilter(params, self.queryset).qs.count(), 2)

    def test_status(self):
        params = {'status': [SITE_STATUS_ACTIVE, SITE_STATUS_PLANNED]}
        self.assertEqual(SiteFilter(params, self.queryset).qs.count(), 2)

    def test_region(self):
        regions = Region.objects.all()[:2]
        params = {'region_id': [regions[0].pk, regions[1].pk]}
        self.assertEqual(SiteFilter(params, self.queryset).qs.count(), 2)
        params = {'region': [regions[0].slug, regions[1].slug]}
        self.assertEqual(SiteFilter(params, self.queryset).qs.count(), 2)


class RackGroupTestCase(TestCase):
    queryset = RackGroup.objects.all()

    @classmethod
    def setUpTestData(cls):

        regions = (
            Region(name='Region 1', slug='region-1'),
            Region(name='Region 2', slug='region-2'),
            Region(name='Region 3', slug='region-3'),
        )
        for region in regions:
            region.save()

        sites = (
            Site(name='Site 1', slug='site-1', region=regions[0]),
            Site(name='Site 2', slug='site-2', region=regions[1]),
            Site(name='Site 3', slug='site-3', region=regions[2]),
        )
        Site.objects.bulk_create(sites)

        rack_groups = (
            RackGroup(name='Rack Group 1', slug='rack-group-1', site=sites[0]),
            RackGroup(name='Rack Group 2', slug='rack-group-2', site=sites[1]),
            RackGroup(name='Rack Group 3', slug='rack-group-3', site=sites[2]),
        )
        RackGroup.objects.bulk_create(rack_groups)

    def test_id(self):
        id_list = self.queryset.values_list('id', flat=True)[:2]
        params = {'id': [str(id) for id in id_list]}
        self.assertEqual(RackGroupFilter(params, self.queryset).qs.count(), 2)

    def test_name(self):
        params = {'name': ['Rack Group 1', 'Rack Group 2']}
        self.assertEqual(RackGroupFilter(params, self.queryset).qs.count(), 2)

    def test_slug(self):
        params = {'slug': ['rack-group-1', 'rack-group-2']}
        self.assertEqual(RackGroupFilter(params, self.queryset).qs.count(), 2)

    def test_region(self):
        regions = Region.objects.all()[:2]
        params = {'region_id': [regions[0].pk, regions[1].pk]}
        self.assertEqual(RackGroupFilter(params, self.queryset).qs.count(), 2)
        params = {'region': [regions[0].slug, regions[1].slug]}
        self.assertEqual(RackGroupFilter(params, self.queryset).qs.count(), 2)

    def test_site(self):
        sites = Site.objects.all()[:2]
        params = {'site_id': [sites[0].pk, sites[1].pk]}
        self.assertEqual(RackGroupFilter(params, self.queryset).qs.count(), 2)
        params = {'site': [sites[0].slug, sites[1].slug]}
        self.assertEqual(RackGroupFilter(params, self.queryset).qs.count(), 2)


class RackRoleTestCase(TestCase):
    queryset = RackRole.objects.all()

    @classmethod
    def setUpTestData(cls):

        rack_roles = (
            RackRole(name='Rack Role 1', slug='rack-role-1', color='ff0000'),
            RackRole(name='Rack Role 2', slug='rack-role-2', color='00ff00'),
            RackRole(name='Rack Role 3', slug='rack-role-3', color='0000ff'),
        )
        RackRole.objects.bulk_create(rack_roles)

    def test_id(self):
        id_list = self.queryset.values_list('id', flat=True)[:2]
        params = {'id': [str(id) for id in id_list]}
        self.assertEqual(RackRoleFilter(params, self.queryset).qs.count(), 2)

    def test_name(self):
        params = {'name': ['Rack Role 1', 'Rack Role 2']}
        self.assertEqual(RackRoleFilter(params, self.queryset).qs.count(), 2)

    def test_slug(self):
        params = {'slug': ['rack-role-1', 'rack-role-2']}
        self.assertEqual(RackRoleFilter(params, self.queryset).qs.count(), 2)

    def test_color(self):
        params = {'color': ['ff0000', '00ff00']}
        self.assertEqual(RackRoleFilter(params, self.queryset).qs.count(), 2)


class RackTestCase(TestCase):
    queryset = Rack.objects.all()

    @classmethod
    def setUpTestData(cls):

        regions = (
            Region(name='Region 1', slug='region-1'),
            Region(name='Region 2', slug='region-2'),
            Region(name='Region 3', slug='region-3'),
        )
        for region in regions:
            region.save()

        sites = (
            Site(name='Site 1', slug='site-1', region=regions[0]),
            Site(name='Site 2', slug='site-2', region=regions[1]),
            Site(name='Site 3', slug='site-3', region=regions[2]),
        )
        Site.objects.bulk_create(sites)

        rack_groups = (
            RackGroup(name='Rack Group 1', slug='rack-group-1', site=sites[0]),
            RackGroup(name='Rack Group 2', slug='rack-group-2', site=sites[1]),
            RackGroup(name='Rack Group 3', slug='rack-group-3', site=sites[2]),
        )
        RackGroup.objects.bulk_create(rack_groups)

        rack_roles = (
            RackRole(name='Rack Role 1', slug='rack-role-1'),
            RackRole(name='Rack Role 2', slug='rack-role-2'),
            RackRole(name='Rack Role 3', slug='rack-role-3'),
        )
        RackRole.objects.bulk_create(rack_roles)

        racks = (
            Rack(name='Rack 1', facility_id='rack-1', site=sites[0], group=rack_groups[0], status=RACK_STATUS_ACTIVE, role=rack_roles[0], serial='ABC', asset_tag='1001', type=RACK_TYPE_2POST, width=RACK_WIDTH_19IN, u_height=42, desc_units=False, outer_width=100, outer_depth=100, outer_unit=LENGTH_UNIT_MILLIMETER),
            Rack(name='Rack 2', facility_id='rack-2', site=sites[1], group=rack_groups[1], status=RACK_STATUS_PLANNED, role=rack_roles[1], serial='DEF', asset_tag='1002', type=RACK_TYPE_4POST, width=RACK_WIDTH_19IN, u_height=43, desc_units=False, outer_width=200, outer_depth=200, outer_unit=LENGTH_UNIT_MILLIMETER),
            Rack(name='Rack 3', facility_id='rack-3', site=sites[2], group=rack_groups[2], status=RACK_STATUS_RESERVED, role=rack_roles[2], serial='GHI', asset_tag='1003', type=RACK_TYPE_CABINET, width=RACK_WIDTH_23IN, u_height=44, desc_units=True, outer_width=300, outer_depth=300, outer_unit=LENGTH_UNIT_INCH),
        )
        Rack.objects.bulk_create(racks)

    def test_id(self):
        id_list = self.queryset.values_list('id', flat=True)[:2]
        params = {'id': [str(id) for id in id_list]}
        self.assertEqual(RackFilter(params, self.queryset).qs.count(), 2)

    def test_name(self):
        params = {'name': ['Rack 1', 'Rack 2']}
        self.assertEqual(RackFilter(params, self.queryset).qs.count(), 2)

    def test_facility_id(self):
        params = {'facility_id': ['rack-1', 'rack-2']}
        self.assertEqual(RackFilter(params, self.queryset).qs.count(), 2)

    def test_asset_tag(self):
        params = {'asset_tag': ['1001', '1002']}
        self.assertEqual(RackFilter(params, self.queryset).qs.count(), 2)

    def test_type(self):
        # TODO: Test for multiple values
        params = {'type': RACK_TYPE_2POST}
        self.assertEqual(RackFilter(params, self.queryset).qs.count(), 1)

    def test_width(self):
        # TODO: Test for multiple values
        params = {'width': RACK_WIDTH_19IN}
        self.assertEqual(RackFilter(params, self.queryset).qs.count(), 2)

    def test_u_height(self):
        params = {'u_height': [42, 43]}
        self.assertEqual(RackFilter(params, self.queryset).qs.count(), 2)

    def test_desc_units(self):
        params = {'desc_units': 'true'}
        self.assertEqual(RackFilter(params, self.queryset).qs.count(), 1)
        params = {'desc_units': 'false'}
        self.assertEqual(RackFilter(params, self.queryset).qs.count(), 2)

    def test_outer_width(self):
        params = {'outer_width': [100, 200]}
        self.assertEqual(RackFilter(params, self.queryset).qs.count(), 2)

    def test_outer_depth(self):
        params = {'outer_depth': [100, 200]}
        self.assertEqual(RackFilter(params, self.queryset).qs.count(), 2)

    def test_outer_unit(self):
        self.assertEqual(Rack.objects.filter(outer_unit__isnull=False).count(), 3)
        params = {'outer_unit': LENGTH_UNIT_MILLIMETER}
        self.assertEqual(RackFilter(params, self.queryset).qs.count(), 2)

    def test_id__in(self):
        id_list = self.queryset.values_list('id', flat=True)[:2]
        params = {'id__in': ','.join([str(id) for id in id_list])}
        self.assertEqual(RackFilter(params, self.queryset).qs.count(), 2)

    def test_region(self):
        regions = Region.objects.all()[:2]
        params = {'region_id': [regions[0].pk, regions[1].pk]}
        self.assertEqual(RackFilter(params, self.queryset).qs.count(), 2)
        params = {'region': [regions[0].slug, regions[1].slug]}
        self.assertEqual(RackFilter(params, self.queryset).qs.count(), 2)

    def test_site(self):
        sites = Site.objects.all()[:2]
        params = {'site_id': [sites[0].pk, sites[1].pk]}
        self.assertEqual(RackFilter(params, self.queryset).qs.count(), 2)
        params = {'site': [sites[0].slug, sites[1].slug]}
        self.assertEqual(RackFilter(params, self.queryset).qs.count(), 2)

    def test_group(self):
        groups = RackGroup.objects.all()[:2]
        params = {'group_id': [groups[0].pk, groups[1].pk]}
        self.assertEqual(RackFilter(params, self.queryset).qs.count(), 2)
        params = {'group': [groups[0].slug, groups[1].slug]}
        self.assertEqual(RackFilter(params, self.queryset).qs.count(), 2)

    def test_status(self):
        params = {'status': [RACK_STATUS_ACTIVE, RACK_STATUS_PLANNED]}
        self.assertEqual(RackFilter(params, self.queryset).qs.count(), 2)

    def test_role(self):
        roles = RackRole.objects.all()[:2]
        params = {'role_id': [roles[0].pk, roles[1].pk]}
        self.assertEqual(RackFilter(params, self.queryset).qs.count(), 2)
        params = {'role': [roles[0].slug, roles[1].slug]}
        self.assertEqual(RackFilter(params, self.queryset).qs.count(), 2)

    def test_serial(self):
        params = {'serial': 'ABC'}
        self.assertEqual(RackFilter(params, self.queryset).qs.count(), 1)
        params = {'serial': 'abc'}
        self.assertEqual(RackFilter(params, self.queryset).qs.count(), 1)


class RackReservationTestCase(TestCase):
    queryset = RackReservation.objects.all()

    @classmethod
    def setUpTestData(cls):

        sites = (
            Site(name='Site 1', slug='site-1'),
            Site(name='Site 2', slug='site-2'),
            Site(name='Site 3', slug='site-3'),
        )
        Site.objects.bulk_create(sites)

        rack_groups = (
            RackGroup(name='Rack Group 1', slug='rack-group-1', site=sites[0]),
            RackGroup(name='Rack Group 2', slug='rack-group-2', site=sites[1]),
            RackGroup(name='Rack Group 3', slug='rack-group-3', site=sites[2]),
        )
        RackGroup.objects.bulk_create(rack_groups)

        racks = (
            Rack(name='Rack 1', site=sites[0], group=rack_groups[0]),
            Rack(name='Rack 2', site=sites[1], group=rack_groups[1]),
            Rack(name='Rack 3', site=sites[2], group=rack_groups[2]),
        )
        Rack.objects.bulk_create(racks)

        users = (
            User(username='User 1'),
            User(username='User 2'),
            User(username='User 3'),
        )
        User.objects.bulk_create(users)

        reservations = (
            RackReservation(rack=racks[0], units=[1, 2, 3], user=users[0]),
            RackReservation(rack=racks[1], units=[4, 5, 6], user=users[1]),
            RackReservation(rack=racks[2], units=[7, 8, 9], user=users[2]),
        )
        RackReservation.objects.bulk_create(reservations)

    def test_id__in(self):
        id_list = self.queryset.values_list('id', flat=True)[:2]
        params = {'id__in': ','.join([str(id) for id in id_list])}
        self.assertEqual(RackReservationFilter(params, self.queryset).qs.count(), 2)

    def test_site(self):
        sites = Site.objects.all()[:2]
        params = {'site_id': [sites[0].pk, sites[1].pk]}
        self.assertEqual(RackReservationFilter(params, self.queryset).qs.count(), 2)
        params = {'site': [sites[0].slug, sites[1].slug]}
        self.assertEqual(RackReservationFilter(params, self.queryset).qs.count(), 2)

    def test_group(self):
        groups = RackGroup.objects.all()[:2]
        params = {'group_id': [groups[0].pk, groups[1].pk]}
        self.assertEqual(RackReservationFilter(params, self.queryset).qs.count(), 2)
        params = {'group': [groups[0].slug, groups[1].slug]}
        self.assertEqual(RackReservationFilter(params, self.queryset).qs.count(), 2)

    def test_user(self):
        users = User.objects.all()[:2]
        params = {'user_id': [users[0].pk, users[1].pk]}
        self.assertEqual(RackReservationFilter(params, self.queryset).qs.count(), 2)
        # TODO: Filtering by username is broken
        # params = {'user': [users[0].username, users[1].username]}
        # self.assertEqual(RackReservationFilter(params, self.queryset).qs.count(), 2)
