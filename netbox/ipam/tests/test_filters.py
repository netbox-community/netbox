from django.test import TestCase

from dcim.models import Device, DeviceRole, DeviceType, Interface, Location, Manufacturer, Rack, Region, Site, SiteGroup
from ipam.choices import *
from ipam.filters import *
from ipam.models import Aggregate, IPAddress, Prefix, RIR, Role, RouteTarget, Service, VLAN, VLANGroup, VRF
from virtualization.models import Cluster, ClusterGroup, ClusterType, VirtualMachine, VMInterface
from tenancy.models import Tenant, TenantGroup


class VRFTestCase(TestCase):
    queryset = VRF.objects.all()
    filterset = VRFFilterSet

    @classmethod
    def setUpTestData(cls):

        route_targets = (
            RouteTarget(name='65000:1001'),
            RouteTarget(name='65000:1002'),
            RouteTarget(name='65000:1003'),
        )
        RouteTarget.objects.bulk_create(route_targets)

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

        vrfs = (
            VRF(name='VRF 1', rd='65000:100', tenant=tenants[0], enforce_unique=False),
            VRF(name='VRF 2', rd='65000:200', tenant=tenants[0], enforce_unique=False),
            VRF(name='VRF 3', rd='65000:300', tenant=tenants[1], enforce_unique=False),
            VRF(name='VRF 4', rd='65000:400', tenant=tenants[1], enforce_unique=True),
            VRF(name='VRF 5', rd='65000:500', tenant=tenants[2], enforce_unique=True),
            VRF(name='VRF 6', rd='65000:600', tenant=tenants[2], enforce_unique=True),
        )
        VRF.objects.bulk_create(vrfs)
        vrfs[0].import_targets.add(route_targets[0])
        vrfs[0].export_targets.add(route_targets[0])
        vrfs[1].import_targets.add(route_targets[1])
        vrfs[1].export_targets.add(route_targets[1])
        vrfs[2].import_targets.add(route_targets[2])
        vrfs[2].export_targets.add(route_targets[2])

    def test_id(self):
        params = {'id': self.queryset.values_list('pk', flat=True)[:2]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_name(self):
        params = {'name': ['VRF 1', 'VRF 2']}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_rd(self):
        params = {'rd': ['65000:100', '65000:200']}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_enforce_unique(self):
        params = {'enforce_unique': 'true'}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 3)
        params = {'enforce_unique': 'false'}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 3)

    def test_import_target(self):
        route_targets = RouteTarget.objects.all()[:2]
        params = {'import_target_id': [route_targets[0].pk, route_targets[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {'import_target': [route_targets[0].name, route_targets[1].name]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_export_target(self):
        route_targets = RouteTarget.objects.all()[:2]
        params = {'export_target_id': [route_targets[0].pk, route_targets[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {'export_target': [route_targets[0].name, route_targets[1].name]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_tenant(self):
        tenants = Tenant.objects.all()[:2]
        params = {'tenant_id': [tenants[0].pk, tenants[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 4)
        params = {'tenant': [tenants[0].slug, tenants[1].slug]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 4)

    def test_tenant_group(self):
        tenant_groups = TenantGroup.objects.all()[:2]
        params = {'tenant_group_id': [tenant_groups[0].pk, tenant_groups[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 4)
        params = {'tenant_group': [tenant_groups[0].slug, tenant_groups[1].slug]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 4)


class RouteTargetTestCase(TestCase):
    queryset = RouteTarget.objects.all()
    filterset = RouteTargetFilterSet

    @classmethod
    def setUpTestData(cls):

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

        route_targets = (
            RouteTarget(name='65000:1001', tenant=tenants[0]),
            RouteTarget(name='65000:1002', tenant=tenants[0]),
            RouteTarget(name='65000:1003', tenant=tenants[0]),
            RouteTarget(name='65000:1004', tenant=tenants[0]),
            RouteTarget(name='65000:2001', tenant=tenants[1]),
            RouteTarget(name='65000:2002', tenant=tenants[1]),
            RouteTarget(name='65000:2003', tenant=tenants[1]),
            RouteTarget(name='65000:2004', tenant=tenants[1]),
            RouteTarget(name='65000:3001', tenant=tenants[2]),
            RouteTarget(name='65000:3002', tenant=tenants[2]),
            RouteTarget(name='65000:3003', tenant=tenants[2]),
            RouteTarget(name='65000:3004', tenant=tenants[2]),
        )
        RouteTarget.objects.bulk_create(route_targets)

        vrfs = (
            VRF(name='VRF 1', rd='65000:100'),
            VRF(name='VRF 2', rd='65000:200'),
            VRF(name='VRF 3', rd='65000:300'),
        )
        VRF.objects.bulk_create(vrfs)
        vrfs[0].import_targets.add(route_targets[0], route_targets[1])
        vrfs[0].export_targets.add(route_targets[2], route_targets[3])
        vrfs[1].import_targets.add(route_targets[4], route_targets[5])
        vrfs[1].export_targets.add(route_targets[6], route_targets[7])

    def test_id(self):
        params = {'id': self.queryset.values_list('pk', flat=True)[:2]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_name(self):
        params = {'name': ['65000:1001', '65000:1002', '65000:1003']}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 3)

    def test_importing_vrf(self):
        vrfs = VRF.objects.all()[:2]
        params = {'importing_vrf_id': [vrfs[0].pk, vrfs[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 4)
        params = {'importing_vrf': [vrfs[0].rd, vrfs[1].rd]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 4)

    def test_exporting_vrf(self):
        vrfs = VRF.objects.all()[:2]
        params = {'exporting_vrf_id': [vrfs[0].pk, vrfs[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 4)
        params = {'exporting_vrf': [vrfs[0].rd, vrfs[1].rd]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 4)

    def test_tenant(self):
        tenants = Tenant.objects.all()[:2]
        params = {'tenant_id': [tenants[0].pk, tenants[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 8)
        params = {'tenant': [tenants[0].slug, tenants[1].slug]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 8)

    def test_tenant_group(self):
        tenant_groups = TenantGroup.objects.all()[:2]
        params = {'tenant_group_id': [tenant_groups[0].pk, tenant_groups[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 8)
        params = {'tenant_group': [tenant_groups[0].slug, tenant_groups[1].slug]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 8)


class RIRTestCase(TestCase):
    queryset = RIR.objects.all()
    filterset = RIRFilterSet

    @classmethod
    def setUpTestData(cls):

        rirs = (
            RIR(name='RIR 1', slug='rir-1', is_private=False, description='A'),
            RIR(name='RIR 2', slug='rir-2', is_private=False, description='B'),
            RIR(name='RIR 3', slug='rir-3', is_private=False, description='C'),
            RIR(name='RIR 4', slug='rir-4', is_private=True, description='D'),
            RIR(name='RIR 5', slug='rir-5', is_private=True, description='E'),
            RIR(name='RIR 6', slug='rir-6', is_private=True, description='F'),
        )
        RIR.objects.bulk_create(rirs)

    def test_id(self):
        params = {'id': self.queryset.values_list('pk', flat=True)[:2]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_name(self):
        params = {'name': ['RIR 1', 'RIR 2']}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_slug(self):
        params = {'slug': ['rir-1', 'rir-2']}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_description(self):
        params = {'description': ['A', 'B']}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_is_private(self):
        params = {'is_private': 'true'}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 3)
        params = {'is_private': 'false'}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 3)


class AggregateTestCase(TestCase):
    queryset = Aggregate.objects.all()
    filterset = AggregateFilterSet

    @classmethod
    def setUpTestData(cls):

        rirs = (
            RIR(name='RIR 1', slug='rir-1'),
            RIR(name='RIR 2', slug='rir-2'),
            RIR(name='RIR 3', slug='rir-3'),
        )
        RIR.objects.bulk_create(rirs)

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

        aggregates = (
            Aggregate(prefix='10.1.0.0/16', rir=rirs[0], tenant=tenants[0], date_added='2020-01-01'),
            Aggregate(prefix='10.2.0.0/16', rir=rirs[0], tenant=tenants[1], date_added='2020-01-02'),
            Aggregate(prefix='10.3.0.0/16', rir=rirs[1], tenant=tenants[2], date_added='2020-01-03'),
            Aggregate(prefix='2001:db8:1::/48', rir=rirs[1], tenant=tenants[0], date_added='2020-01-04'),
            Aggregate(prefix='2001:db8:2::/48', rir=rirs[2], tenant=tenants[1], date_added='2020-01-05'),
            Aggregate(prefix='2001:db8:3::/48', rir=rirs[2], tenant=tenants[2], date_added='2020-01-06'),
        )
        Aggregate.objects.bulk_create(aggregates)

    def test_id(self):
        params = {'id': self.queryset.values_list('pk', flat=True)[:2]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_family(self):
        params = {'family': '4'}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 3)

    def test_date_added(self):
        params = {'date_added': ['2020-01-01', '2020-01-02']}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    # TODO: Test for multiple values
    def test_prefix(self):
        params = {'prefix': '10.1.0.0/16'}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_rir(self):
        rirs = RIR.objects.all()[:2]
        params = {'rir_id': [rirs[0].pk, rirs[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 4)
        params = {'rir': [rirs[0].slug, rirs[1].slug]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 4)

    def test_tenant(self):
        tenants = Tenant.objects.all()[:2]
        params = {'tenant_id': [tenants[0].pk, tenants[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 4)
        params = {'tenant': [tenants[0].slug, tenants[1].slug]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 4)

    def test_tenant_group(self):
        tenant_groups = TenantGroup.objects.all()[:2]
        params = {'tenant_group_id': [tenant_groups[0].pk, tenant_groups[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 4)
        params = {'tenant_group': [tenant_groups[0].slug, tenant_groups[1].slug]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 4)


class RoleTestCase(TestCase):
    queryset = Role.objects.all()
    filterset = RoleFilterSet

    @classmethod
    def setUpTestData(cls):

        roles = (
            Role(name='Role 1', slug='role-1'),
            Role(name='Role 2', slug='role-2'),
            Role(name='Role 3', slug='role-3'),
        )
        Role.objects.bulk_create(roles)

    def test_id(self):
        params = {'id': self.queryset.values_list('pk', flat=True)[:2]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_name(self):
        params = {'name': ['Role 1', 'Role 2']}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_slug(self):
        params = {'slug': ['role-1', 'role-2']}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)


class PrefixTestCase(TestCase):
    queryset = Prefix.objects.all()
    filterset = PrefixFilterSet

    @classmethod
    def setUpTestData(cls):

        regions = (
            Region(name='Test Region 1', slug='test-region-1'),
            Region(name='Test Region 2', slug='test-region-2'),
            Region(name='Test Region 3', slug='test-region-3'),
        )
        for r in regions:
            r.save()

        site_groups = (
            SiteGroup(name='Site Group 1', slug='site-group-1'),
            SiteGroup(name='Site Group 2', slug='site-group-2'),
            SiteGroup(name='Site Group 3', slug='site-group-3'),
        )
        for site_group in site_groups:
            site_group.save()

        sites = (
            Site(name='Test Site 1', slug='test-site-1', region=regions[0], group=site_groups[0]),
            Site(name='Test Site 2', slug='test-site-2', region=regions[1], group=site_groups[1]),
            Site(name='Test Site 3', slug='test-site-3', region=regions[2], group=site_groups[2]),
        )
        Site.objects.bulk_create(sites)

        route_targets = (
            RouteTarget(name='65000:100'),
            RouteTarget(name='65000:200'),
            RouteTarget(name='65000:300'),
        )
        RouteTarget.objects.bulk_create(route_targets)

        vrfs = (
            VRF(name='VRF 1', rd='65000:100'),
            VRF(name='VRF 2', rd='65000:200'),
            VRF(name='VRF 3', rd='65000:300'),
        )
        VRF.objects.bulk_create(vrfs)
        vrfs[0].import_targets.add(route_targets[0], route_targets[1], route_targets[2])
        vrfs[1].export_targets.add(route_targets[1])
        vrfs[2].export_targets.add(route_targets[2])

        vlans = (
            VLAN(vid=1, name='VLAN 1'),
            VLAN(vid=2, name='VLAN 2'),
            VLAN(vid=3, name='VLAN 3'),
        )
        VLAN.objects.bulk_create(vlans)

        roles = (
            Role(name='Role 1', slug='role-1'),
            Role(name='Role 2', slug='role-2'),
            Role(name='Role 3', slug='role-3'),
        )
        Role.objects.bulk_create(roles)

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

        prefixes = (
            Prefix(prefix='10.0.0.0/24', tenant=None, site=None, vrf=None, vlan=None, role=None, is_pool=True),
            Prefix(prefix='10.0.1.0/24', tenant=tenants[0], site=sites[0], vrf=vrfs[0], vlan=vlans[0], role=roles[0]),
            Prefix(prefix='10.0.2.0/24', tenant=tenants[1], site=sites[1], vrf=vrfs[1], vlan=vlans[1], role=roles[1], status=PrefixStatusChoices.STATUS_DEPRECATED),
            Prefix(prefix='10.0.3.0/24', tenant=tenants[2], site=sites[2], vrf=vrfs[2], vlan=vlans[2], role=roles[2], status=PrefixStatusChoices.STATUS_RESERVED),
            Prefix(prefix='2001:db8::/64', tenant=None, site=None, vrf=None, vlan=None, role=None, is_pool=True),
            Prefix(prefix='2001:db8:0:1::/64', tenant=tenants[0], site=sites[0], vrf=vrfs[0], vlan=vlans[0], role=roles[0]),
            Prefix(prefix='2001:db8:0:2::/64', tenant=tenants[1], site=sites[1], vrf=vrfs[1], vlan=vlans[1], role=roles[1], status=PrefixStatusChoices.STATUS_DEPRECATED),
            Prefix(prefix='2001:db8:0:3::/64', tenant=tenants[2], site=sites[2], vrf=vrfs[2], vlan=vlans[2], role=roles[2], status=PrefixStatusChoices.STATUS_RESERVED),
            Prefix(prefix='10.0.0.0/16'),
            Prefix(prefix='2001:db8::/32'),
        )
        Prefix.objects.bulk_create(prefixes)

    def test_id(self):
        params = {'id': self.queryset.values_list('pk', flat=True)[:2]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_family(self):
        params = {'family': '6'}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 5)

    def test_prefix(self):
        prefixes = Prefix.objects.all()[:2]
        params = {'prefix': [prefixes[0].prefix, prefixes[1].prefix]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_is_pool(self):
        params = {'is_pool': 'true'}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {'is_pool': 'false'}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 8)

    def test_within(self):
        params = {'within': '10.0.0.0/16'}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 4)

    def test_within_include(self):
        params = {'within_include': '10.0.0.0/16'}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 5)

    def test_contains(self):
        params = {'contains': '10.0.1.0/24'}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {'contains': '2001:db8:0:1::/64'}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_mask_length(self):
        params = {'mask_length': '24'}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 4)

    def test_vrf(self):
        vrfs = VRF.objects.all()[:2]
        params = {'vrf_id': [vrfs[0].pk, vrfs[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 4)
        params = {'vrf': [vrfs[0].rd, vrfs[1].rd]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 4)

    def test_present_in_vrf(self):
        vrf1 = VRF.objects.get(name='VRF 1')
        vrf2 = VRF.objects.get(name='VRF 2')
        self.assertEqual(self.filterset({'present_in_vrf_id': vrf1.pk}, self.queryset).qs.count(), 6)
        self.assertEqual(self.filterset({'present_in_vrf_id': vrf2.pk}, self.queryset).qs.count(), 2)
        self.assertEqual(self.filterset({'present_in_vrf': vrf1.rd}, self.queryset).qs.count(), 6)
        self.assertEqual(self.filterset({'present_in_vrf': vrf2.rd}, self.queryset).qs.count(), 2)

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

    def test_vlan(self):
        vlans = VLAN.objects.all()[:2]
        params = {'vlan_id': [vlans[0].pk, vlans[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 4)
        # TODO: Test for multiple values
        params = {'vlan_vid': vlans[0].vid}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_role(self):
        roles = Role.objects.all()[:2]
        params = {'role_id': [roles[0].pk, roles[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 4)
        params = {'role': [roles[0].slug, roles[1].slug]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 4)

    def test_status(self):
        params = {'status': [PrefixStatusChoices.STATUS_DEPRECATED, PrefixStatusChoices.STATUS_RESERVED]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 4)

    def test_tenant(self):
        tenants = Tenant.objects.all()[:2]
        params = {'tenant_id': [tenants[0].pk, tenants[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 4)
        params = {'tenant': [tenants[0].slug, tenants[1].slug]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 4)

    def test_tenant_group(self):
        tenant_groups = TenantGroup.objects.all()[:2]
        params = {'tenant_group_id': [tenant_groups[0].pk, tenant_groups[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 4)
        params = {'tenant_group': [tenant_groups[0].slug, tenant_groups[1].slug]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 4)


class IPAddressTestCase(TestCase):
    queryset = IPAddress.objects.all()
    filterset = IPAddressFilterSet

    @classmethod
    def setUpTestData(cls):

        vrfs = (
            VRF(name='VRF 1', rd='65000:100'),
            VRF(name='VRF 2', rd='65000:200'),
            VRF(name='VRF 3', rd='65000:300'),
        )
        VRF.objects.bulk_create(vrfs)

        site = Site.objects.create(name='Site 1', slug='site-1')
        manufacturer = Manufacturer.objects.create(name='Manufacturer 1', slug='manufacturer-1')
        device_type = DeviceType.objects.create(manufacturer=manufacturer, model='Device Type 1')
        device_role = DeviceRole.objects.create(name='Device Role 1', slug='device-role-1')

        devices = (
            Device(device_type=device_type, name='Device 1', site=site, device_role=device_role),
            Device(device_type=device_type, name='Device 2', site=site, device_role=device_role),
            Device(device_type=device_type, name='Device 3', site=site, device_role=device_role),
        )
        Device.objects.bulk_create(devices)

        interfaces = (
            Interface(device=devices[0], name='Interface 1'),
            Interface(device=devices[1], name='Interface 2'),
            Interface(device=devices[2], name='Interface 3'),
        )
        Interface.objects.bulk_create(interfaces)

        clustertype = ClusterType.objects.create(name='Cluster Type 1', slug='cluster-type-1')
        cluster = Cluster.objects.create(type=clustertype, name='Cluster 1')

        virtual_machines = (
            VirtualMachine(name='Virtual Machine 1', cluster=cluster),
            VirtualMachine(name='Virtual Machine 2', cluster=cluster),
            VirtualMachine(name='Virtual Machine 3', cluster=cluster),
        )
        VirtualMachine.objects.bulk_create(virtual_machines)

        vminterfaces = (
            VMInterface(virtual_machine=virtual_machines[0], name='Interface 1'),
            VMInterface(virtual_machine=virtual_machines[1], name='Interface 2'),
            VMInterface(virtual_machine=virtual_machines[2], name='Interface 3'),
        )
        VMInterface.objects.bulk_create(vminterfaces)

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

        ipaddresses = (
            IPAddress(address='10.0.0.1/24', tenant=None, vrf=None, assigned_object=None, status=IPAddressStatusChoices.STATUS_ACTIVE, dns_name='ipaddress-a'),
            IPAddress(address='10.0.0.2/24', tenant=tenants[0], vrf=vrfs[0], assigned_object=interfaces[0], status=IPAddressStatusChoices.STATUS_ACTIVE, dns_name='ipaddress-b'),
            IPAddress(address='10.0.0.3/24', tenant=tenants[1], vrf=vrfs[1], assigned_object=interfaces[1], status=IPAddressStatusChoices.STATUS_RESERVED, role=IPAddressRoleChoices.ROLE_VIP, dns_name='ipaddress-c'),
            IPAddress(address='10.0.0.4/24', tenant=tenants[2], vrf=vrfs[2], assigned_object=interfaces[2], status=IPAddressStatusChoices.STATUS_DEPRECATED, role=IPAddressRoleChoices.ROLE_SECONDARY, dns_name='ipaddress-d'),
            IPAddress(address='10.0.0.1/25', tenant=None, vrf=None, assigned_object=None, status=IPAddressStatusChoices.STATUS_ACTIVE),
            IPAddress(address='2001:db8::1/64', tenant=None, vrf=None, assigned_object=None, status=IPAddressStatusChoices.STATUS_ACTIVE, dns_name='ipaddress-a'),
            IPAddress(address='2001:db8::2/64', tenant=tenants[0], vrf=vrfs[0], assigned_object=vminterfaces[0], status=IPAddressStatusChoices.STATUS_ACTIVE, dns_name='ipaddress-b'),
            IPAddress(address='2001:db8::3/64', tenant=tenants[1], vrf=vrfs[1], assigned_object=vminterfaces[1], status=IPAddressStatusChoices.STATUS_RESERVED, role=IPAddressRoleChoices.ROLE_VIP, dns_name='ipaddress-c'),
            IPAddress(address='2001:db8::4/64', tenant=tenants[2], vrf=vrfs[2], assigned_object=vminterfaces[2], status=IPAddressStatusChoices.STATUS_DEPRECATED, role=IPAddressRoleChoices.ROLE_SECONDARY, dns_name='ipaddress-d'),
            IPAddress(address='2001:db8::1/65', tenant=None, vrf=None, assigned_object=None, status=IPAddressStatusChoices.STATUS_ACTIVE),
        )
        IPAddress.objects.bulk_create(ipaddresses)

    def test_id(self):
        params = {'id': self.queryset.values_list('pk', flat=True)[:2]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_family(self):
        params = {'family': '6'}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 5)

    def test_dns_name(self):
        params = {'dns_name': ['ipaddress-a', 'ipaddress-b']}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 4)

    def test_parent(self):
        params = {'parent': '10.0.0.0/24'}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 5)
        params = {'parent': '2001:db8::/64'}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 5)

    def test_filter_address(self):
        # Check IPv4 and IPv6, with and without a mask
        params = {'address': ['10.0.0.1/24']}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)
        params = {'address': ['10.0.0.1']}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {'address': ['10.0.0.1/24', '10.0.0.1/25']}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {'address': ['2001:db8::1/64']}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)
        params = {'address': ['2001:db8::1']}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {'address': ['2001:db8::1/64', '2001:db8::1/65']}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_mask_length(self):
        params = {'mask_length': '24'}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 4)

    def test_vrf(self):
        vrfs = VRF.objects.all()[:2]
        params = {'vrf_id': [vrfs[0].pk, vrfs[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 4)
        params = {'vrf': [vrfs[0].rd, vrfs[1].rd]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 4)

    def test_device(self):
        devices = Device.objects.all()[:2]
        params = {'device_id': [devices[0].pk, devices[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {'device': [devices[0].name, devices[1].name]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_virtual_machine(self):
        vms = VirtualMachine.objects.all()[:2]
        params = {'virtual_machine_id': [vms[0].pk, vms[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {'virtual_machine': [vms[0].name, vms[1].name]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_interface(self):
        interfaces = Interface.objects.all()[:2]
        params = {'interface_id': [interfaces[0].pk, interfaces[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {'interface': ['Interface 1', 'Interface 2']}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_vminterface(self):
        vminterfaces = VMInterface.objects.all()[:2]
        params = {'vminterface_id': [vminterfaces[0].pk, vminterfaces[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {'vminterface': ['Interface 1', 'Interface 2']}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_assigned_to_interface(self):
        params = {'assigned_to_interface': 'true'}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 6)
        params = {'assigned_to_interface': 'false'}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 4)

    def test_status(self):
        params = {'status': [PrefixStatusChoices.STATUS_DEPRECATED, PrefixStatusChoices.STATUS_RESERVED]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 4)

    def test_role(self):
        params = {'role': [IPAddressRoleChoices.ROLE_SECONDARY, IPAddressRoleChoices.ROLE_VIP]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 4)

    def test_tenant(self):
        tenants = Tenant.objects.all()[:2]
        params = {'tenant_id': [tenants[0].pk, tenants[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 4)
        params = {'tenant': [tenants[0].slug, tenants[1].slug]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 4)

    def test_tenant_group(self):
        tenant_groups = TenantGroup.objects.all()[:2]
        params = {'tenant_group_id': [tenant_groups[0].pk, tenant_groups[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 4)
        params = {'tenant_group': [tenant_groups[0].slug, tenant_groups[1].slug]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 4)


class VLANGroupTestCase(TestCase):
    queryset = VLANGroup.objects.all()
    filterset = VLANGroupFilterSet

    @classmethod
    def setUpTestData(cls):

        region = Region(name='Region 1', slug='region-1')
        region.save()

        sitegroup = SiteGroup(name='Site Group 1', slug='site-group-1')
        sitegroup.save()

        site = Site(name='Site 1', slug='site-1')
        site.save()

        location = Location(name='Location 1', slug='location-1', site=site)
        location.save()

        rack = Rack(name='Rack 1', site=site)
        rack.save()

        clustertype = ClusterType(name='Cluster Type 1', slug='cluster-type-1')
        clustertype.save()

        clustergroup = ClusterGroup(name='Cluster Group 1', slug='cluster-group-1')
        clustergroup.save()

        cluster = Cluster(name='Cluster 1', type=clustertype)
        cluster.save()

        vlan_groups = (
            VLANGroup(name='VLAN Group 1', slug='vlan-group-1', scope=region, description='A'),
            VLANGroup(name='VLAN Group 2', slug='vlan-group-2', scope=sitegroup, description='B'),
            VLANGroup(name='VLAN Group 3', slug='vlan-group-3', scope=site, description='C'),
            VLANGroup(name='VLAN Group 4', slug='vlan-group-4', scope=location, description='D'),
            VLANGroup(name='VLAN Group 5', slug='vlan-group-5', scope=rack, description='E'),
            VLANGroup(name='VLAN Group 6', slug='vlan-group-6', scope=clustergroup, description='F'),
            VLANGroup(name='VLAN Group 7', slug='vlan-group-7', scope=cluster, description='G'),
            VLANGroup(name='VLAN Group 8', slug='vlan-group-8'),
        )
        VLANGroup.objects.bulk_create(vlan_groups)

    def test_id(self):
        params = {'id': self.queryset.values_list('pk', flat=True)[:2]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_name(self):
        params = {'name': ['VLAN Group 1', 'VLAN Group 2']}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_slug(self):
        params = {'slug': ['vlan-group-1', 'vlan-group-2']}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_description(self):
        params = {'description': ['A', 'B']}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_region(self):
        params = {'region': Region.objects.first().pk}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_sitegroup(self):
        params = {'sitegroup': SiteGroup.objects.first().pk}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_site(self):
        params = {'site': Site.objects.first().pk}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_location(self):
        params = {'location': Location.objects.first().pk}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_rack(self):
        params = {'rack': Rack.objects.first().pk}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_clustergroup(self):
        params = {'clustergroup': ClusterGroup.objects.first().pk}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_cluster(self):
        params = {'cluster': Cluster.objects.first().pk}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)


class VLANTestCase(TestCase):
    queryset = VLAN.objects.all()
    filterset = VLANFilterSet

    @classmethod
    def setUpTestData(cls):

        regions = (
            Region(name='Test Region 1', slug='test-region-1'),
            Region(name='Test Region 2', slug='test-region-2'),
            Region(name='Test Region 3', slug='test-region-3'),
        )
        for r in regions:
            r.save()

        site_groups = (
            SiteGroup(name='Site Group 1', slug='site-group-1'),
            SiteGroup(name='Site Group 2', slug='site-group-2'),
            SiteGroup(name='Site Group 3', slug='site-group-3'),
        )
        for site_group in site_groups:
            site_group.save()

        sites = (
            Site(name='Test Site 1', slug='test-site-1', region=regions[0], group=site_groups[0]),
            Site(name='Test Site 2', slug='test-site-2', region=regions[1], group=site_groups[1]),
            Site(name='Test Site 3', slug='test-site-3', region=regions[2], group=site_groups[2]),
        )
        Site.objects.bulk_create(sites)

        roles = (
            Role(name='Role 1', slug='role-1'),
            Role(name='Role 2', slug='role-2'),
            Role(name='Role 3', slug='role-3'),
        )
        Role.objects.bulk_create(roles)

        groups = (
            VLANGroup(name='VLAN Group 1', slug='vlan-group-1', scope=sites[0]),
            VLANGroup(name='VLAN Group 2', slug='vlan-group-2', scope=sites[1]),
            VLANGroup(name='VLAN Group 3', slug='vlan-group-3', scope=None),
        )
        VLANGroup.objects.bulk_create(groups)

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

        vlans = (
            VLAN(vid=101, name='VLAN 101', site=sites[0], group=groups[0], role=roles[0], tenant=tenants[0], status=VLANStatusChoices.STATUS_ACTIVE),
            VLAN(vid=102, name='VLAN 102', site=sites[0], group=groups[0], role=roles[0], tenant=tenants[0], status=VLANStatusChoices.STATUS_ACTIVE),
            VLAN(vid=201, name='VLAN 201', site=sites[1], group=groups[1], role=roles[1], tenant=tenants[1], status=VLANStatusChoices.STATUS_DEPRECATED),
            VLAN(vid=202, name='VLAN 202', site=sites[1], group=groups[1], role=roles[1], tenant=tenants[1], status=VLANStatusChoices.STATUS_DEPRECATED),
            VLAN(vid=301, name='VLAN 301', site=sites[2], group=groups[2], role=roles[2], tenant=tenants[2], status=VLANStatusChoices.STATUS_RESERVED),
            VLAN(vid=302, name='VLAN 302', site=sites[2], group=groups[2], role=roles[2], tenant=tenants[2], status=VLANStatusChoices.STATUS_RESERVED),
        )
        VLAN.objects.bulk_create(vlans)

    def test_id(self):
        params = {'id': self.queryset.values_list('pk', flat=True)[:2]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_name(self):
        params = {'name': ['VLAN 101', 'VLAN 102']}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_rd(self):
        params = {'vid': ['101', '201', '301']}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 3)

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

    def test_group(self):
        groups = VLANGroup.objects.all()[:2]
        params = {'group_id': [groups[0].pk, groups[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 4)
        params = {'group': [groups[0].slug, groups[1].slug]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 4)

    def test_role(self):
        roles = Role.objects.all()[:2]
        params = {'role_id': [roles[0].pk, roles[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 4)
        params = {'role': [roles[0].slug, roles[1].slug]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 4)

    def test_status(self):
        params = {'status': [VLANStatusChoices.STATUS_ACTIVE, VLANStatusChoices.STATUS_DEPRECATED]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 4)

    def test_tenant(self):
        tenants = Tenant.objects.all()[:2]
        params = {'tenant_id': [tenants[0].pk, tenants[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 4)
        params = {'tenant': [tenants[0].slug, tenants[1].slug]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 4)

    def test_tenant_group(self):
        tenant_groups = TenantGroup.objects.all()[:2]
        params = {'tenant_group_id': [tenant_groups[0].pk, tenant_groups[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 4)
        params = {'tenant_group': [tenant_groups[0].slug, tenant_groups[1].slug]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 4)


class ServiceTestCase(TestCase):
    queryset = Service.objects.all()
    filterset = ServiceFilterSet

    @classmethod
    def setUpTestData(cls):

        site = Site.objects.create(name='Site 1', slug='site-1')
        manufacturer = Manufacturer.objects.create(name='Manufacturer 1', slug='manufacturer-1')
        device_type = DeviceType.objects.create(manufacturer=manufacturer, model='Device Type 1')
        device_role = DeviceRole.objects.create(name='Device Role 1', slug='device-role-1')

        devices = (
            Device(device_type=device_type, name='Device 1', site=site, device_role=device_role),
            Device(device_type=device_type, name='Device 2', site=site, device_role=device_role),
            Device(device_type=device_type, name='Device 3', site=site, device_role=device_role),
        )
        Device.objects.bulk_create(devices)

        clustertype = ClusterType.objects.create(name='Cluster Type 1', slug='cluster-type-1')
        cluster = Cluster.objects.create(type=clustertype, name='Cluster 1')

        virtual_machines = (
            VirtualMachine(name='Virtual Machine 1', cluster=cluster),
            VirtualMachine(name='Virtual Machine 2', cluster=cluster),
            VirtualMachine(name='Virtual Machine 3', cluster=cluster),
        )
        VirtualMachine.objects.bulk_create(virtual_machines)

        services = (
            Service(device=devices[0], name='Service 1', protocol=ServiceProtocolChoices.PROTOCOL_TCP, ports=[1001]),
            Service(device=devices[1], name='Service 2', protocol=ServiceProtocolChoices.PROTOCOL_TCP, ports=[1002]),
            Service(device=devices[2], name='Service 3', protocol=ServiceProtocolChoices.PROTOCOL_UDP, ports=[1003]),
            Service(virtual_machine=virtual_machines[0], name='Service 4', protocol=ServiceProtocolChoices.PROTOCOL_TCP, ports=[2001]),
            Service(virtual_machine=virtual_machines[1], name='Service 5', protocol=ServiceProtocolChoices.PROTOCOL_TCP, ports=[2002]),
            Service(virtual_machine=virtual_machines[2], name='Service 6', protocol=ServiceProtocolChoices.PROTOCOL_UDP, ports=[2003]),
        )
        Service.objects.bulk_create(services)

    def test_id(self):
        params = {'id': self.queryset.values_list('pk', flat=True)[:3]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 3)

    def test_name(self):
        params = {'name': ['Service 1', 'Service 2']}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_protocol(self):
        params = {'protocol': ServiceProtocolChoices.PROTOCOL_TCP}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 4)

    def test_port(self):
        params = {'port': '1001'}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_device(self):
        devices = Device.objects.all()[:2]
        params = {'device_id': [devices[0].pk, devices[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {'device': [devices[0].name, devices[1].name]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_virtual_machine(self):
        vms = VirtualMachine.objects.all()[:2]
        params = {'virtual_machine_id': [vms[0].pk, vms[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {'virtual_machine': [vms[0].name, vms[1].name]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
