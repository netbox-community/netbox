from django.test import TestCase

from dcim.models import DeviceRole, Platform, Region, Site, SiteGroup
from ipam.models import IPAddress
from tenancy.models import Tenant, TenantGroup
from virtualization.choices import *
from virtualization.filters import *
from virtualization.models import Cluster, ClusterGroup, ClusterType, VirtualMachine, VMInterface


class ClusterTypeTestCase(TestCase):
    queryset = ClusterType.objects.all()
    filterset = ClusterTypeFilterSet

    @classmethod
    def setUpTestData(cls):

        cluster_types = (
            ClusterType(name='Cluster Type 1', slug='cluster-type-1', description='A'),
            ClusterType(name='Cluster Type 2', slug='cluster-type-2', description='B'),
            ClusterType(name='Cluster Type 3', slug='cluster-type-3', description='C'),
        )
        ClusterType.objects.bulk_create(cluster_types)

    def test_id(self):
        params = {'id': self.queryset.values_list('pk', flat=True)[:2]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_name(self):
        params = {'name': ['Cluster Type 1', 'Cluster Type 2']}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_slug(self):
        params = {'slug': ['cluster-type-1', 'cluster-type-2']}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_description(self):
        params = {'description': ['A', 'B']}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)


class ClusterGroupTestCase(TestCase):
    queryset = ClusterGroup.objects.all()
    filterset = ClusterGroupFilterSet

    @classmethod
    def setUpTestData(cls):

        cluster_groups = (
            ClusterGroup(name='Cluster Group 1', slug='cluster-group-1', description='A'),
            ClusterGroup(name='Cluster Group 2', slug='cluster-group-2', description='B'),
            ClusterGroup(name='Cluster Group 3', slug='cluster-group-3', description='C'),
        )
        ClusterGroup.objects.bulk_create(cluster_groups)

    def test_id(self):
        params = {'id': self.queryset.values_list('pk', flat=True)[:2]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_name(self):
        params = {'name': ['Cluster Group 1', 'Cluster Group 2']}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_slug(self):
        params = {'slug': ['cluster-group-1', 'cluster-group-2']}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_description(self):
        params = {'description': ['A', 'B']}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)


class ClusterTestCase(TestCase):
    queryset = Cluster.objects.all()
    filterset = ClusterFilterSet

    @classmethod
    def setUpTestData(cls):

        cluster_types = (
            ClusterType(name='Cluster Type 1', slug='cluster-type-1'),
            ClusterType(name='Cluster Type 2', slug='cluster-type-2'),
            ClusterType(name='Cluster Type 3', slug='cluster-type-3'),
        )
        ClusterType.objects.bulk_create(cluster_types)

        cluster_groups = (
            ClusterGroup(name='Cluster Group 1', slug='cluster-group-1'),
            ClusterGroup(name='Cluster Group 2', slug='cluster-group-2'),
            ClusterGroup(name='Cluster Group 3', slug='cluster-group-3'),
        )
        ClusterGroup.objects.bulk_create(cluster_groups)

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

        clusters = (
            Cluster(name='Cluster 1', type=cluster_types[0], group=cluster_groups[0], site=sites[0], tenant=tenants[0]),
            Cluster(name='Cluster 2', type=cluster_types[1], group=cluster_groups[1], site=sites[1], tenant=tenants[1]),
            Cluster(name='Cluster 3', type=cluster_types[2], group=cluster_groups[2], site=sites[2], tenant=tenants[2]),
        )
        Cluster.objects.bulk_create(clusters)

    def test_id(self):
        params = {'id': self.queryset.values_list('pk', flat=True)[:2]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_name(self):
        params = {'name': ['Cluster 1', 'Cluster 2']}
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

    def test_group(self):
        groups = ClusterGroup.objects.all()[:2]
        params = {'group_id': [groups[0].pk, groups[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {'group': [groups[0].slug, groups[1].slug]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_type(self):
        types = ClusterType.objects.all()[:2]
        params = {'type_id': [types[0].pk, types[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {'type': [types[0].slug, types[1].slug]}
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


class VirtualMachineTestCase(TestCase):
    queryset = VirtualMachine.objects.all()
    filterset = VirtualMachineFilterSet

    @classmethod
    def setUpTestData(cls):

        cluster_types = (
            ClusterType(name='Cluster Type 1', slug='cluster-type-1'),
            ClusterType(name='Cluster Type 2', slug='cluster-type-2'),
            ClusterType(name='Cluster Type 3', slug='cluster-type-3'),
        )
        ClusterType.objects.bulk_create(cluster_types)

        cluster_groups = (
            ClusterGroup(name='Cluster Group 1', slug='cluster-group-1'),
            ClusterGroup(name='Cluster Group 2', slug='cluster-group-2'),
            ClusterGroup(name='Cluster Group 3', slug='cluster-group-3'),
        )
        ClusterGroup.objects.bulk_create(cluster_groups)

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

        clusters = (
            Cluster(name='Cluster 1', type=cluster_types[0], group=cluster_groups[0], site=sites[0]),
            Cluster(name='Cluster 2', type=cluster_types[1], group=cluster_groups[1], site=sites[1]),
            Cluster(name='Cluster 3', type=cluster_types[2], group=cluster_groups[2], site=sites[2]),
        )
        Cluster.objects.bulk_create(clusters)

        platforms = (
            Platform(name='Platform 1', slug='platform-1'),
            Platform(name='Platform 2', slug='platform-2'),
            Platform(name='Platform 3', slug='platform-3'),
        )
        Platform.objects.bulk_create(platforms)

        roles = (
            DeviceRole(name='Device Role 1', slug='device-role-1'),
            DeviceRole(name='Device Role 2', slug='device-role-2'),
            DeviceRole(name='Device Role 3', slug='device-role-3'),
        )
        DeviceRole.objects.bulk_create(roles)

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

        vms = (
            VirtualMachine(name='Virtual Machine 1', cluster=clusters[0], platform=platforms[0], role=roles[0], tenant=tenants[0], status=VirtualMachineStatusChoices.STATUS_ACTIVE, vcpus=1, memory=1, disk=1, local_context_data={"foo": 123}),
            VirtualMachine(name='Virtual Machine 2', cluster=clusters[1], platform=platforms[1], role=roles[1], tenant=tenants[1], status=VirtualMachineStatusChoices.STATUS_STAGED, vcpus=2, memory=2, disk=2),
            VirtualMachine(name='Virtual Machine 3', cluster=clusters[2], platform=platforms[2], role=roles[2], tenant=tenants[2], status=VirtualMachineStatusChoices.STATUS_OFFLINE, vcpus=3, memory=3, disk=3),
        )
        VirtualMachine.objects.bulk_create(vms)

        interfaces = (
            VMInterface(virtual_machine=vms[0], name='Interface 1', mac_address='00-00-00-00-00-01'),
            VMInterface(virtual_machine=vms[1], name='Interface 2', mac_address='00-00-00-00-00-02'),
            VMInterface(virtual_machine=vms[2], name='Interface 3', mac_address='00-00-00-00-00-03'),
        )
        VMInterface.objects.bulk_create(interfaces)

        # Assign primary IPs for filtering
        ipaddresses = (
            IPAddress(address='192.0.2.1/24', assigned_object=interfaces[0]),
            IPAddress(address='192.0.2.2/24', assigned_object=interfaces[1]),
        )
        IPAddress.objects.bulk_create(ipaddresses)
        VirtualMachine.objects.filter(pk=vms[0].pk).update(primary_ip4=ipaddresses[0])
        VirtualMachine.objects.filter(pk=vms[1].pk).update(primary_ip4=ipaddresses[1])

    def test_id(self):
        params = {'id': self.queryset.values_list('pk', flat=True)[:2]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_name(self):
        params = {'name': ['Virtual Machine 1', 'Virtual Machine 2']}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_vcpus(self):
        params = {'vcpus': [1, 2]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_memory(self):
        params = {'memory': [1, 2]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_disk(self):
        params = {'disk': [1, 2]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_status(self):
        params = {'status': [VirtualMachineStatusChoices.STATUS_ACTIVE, VirtualMachineStatusChoices.STATUS_STAGED]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_cluster_group(self):
        groups = ClusterGroup.objects.all()[:2]
        params = {'cluster_group_id': [groups[0].pk, groups[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {'cluster_group': [groups[0].slug, groups[1].slug]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_cluster_type(self):
        types = ClusterType.objects.all()[:2]
        params = {'cluster_type_id': [types[0].pk, types[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {'cluster_type': [types[0].slug, types[1].slug]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_cluster(self):
        clusters = Cluster.objects.all()[:2]
        params = {'cluster_id': [clusters[0].pk, clusters[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        # TODO: 'cluster' should match on name
        # params = {'cluster': [clusters[0].name, clusters[1].name]}
        # self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

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

    def test_role(self):
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

    def test_mac_address(self):
        params = {'mac_address': ['00-00-00-00-00-01', '00-00-00-00-00-02']}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_has_primary_ip(self):
        params = {'has_primary_ip': 'true'}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {'has_primary_ip': 'false'}
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


class VMInterfaceTestCase(TestCase):
    queryset = VMInterface.objects.all()
    filterset = VMInterfaceFilterSet

    @classmethod
    def setUpTestData(cls):

        cluster_types = (
            ClusterType(name='Cluster Type 1', slug='cluster-type-1'),
            ClusterType(name='Cluster Type 2', slug='cluster-type-2'),
            ClusterType(name='Cluster Type 3', slug='cluster-type-3'),
        )
        ClusterType.objects.bulk_create(cluster_types)

        clusters = (
            Cluster(name='Cluster 1', type=cluster_types[0]),
            Cluster(name='Cluster 2', type=cluster_types[1]),
            Cluster(name='Cluster 3', type=cluster_types[2]),
        )
        Cluster.objects.bulk_create(clusters)

        vms = (
            VirtualMachine(name='Virtual Machine 1', cluster=clusters[0]),
            VirtualMachine(name='Virtual Machine 2', cluster=clusters[1]),
            VirtualMachine(name='Virtual Machine 3', cluster=clusters[2]),
        )
        VirtualMachine.objects.bulk_create(vms)

        interfaces = (
            VMInterface(virtual_machine=vms[0], name='Interface 1', enabled=True, mtu=100, mac_address='00-00-00-00-00-01'),
            VMInterface(virtual_machine=vms[1], name='Interface 2', enabled=True, mtu=200, mac_address='00-00-00-00-00-02'),
            VMInterface(virtual_machine=vms[2], name='Interface 3', enabled=False, mtu=300, mac_address='00-00-00-00-00-03'),
        )
        VMInterface.objects.bulk_create(interfaces)

    def test_id(self):
        id_list = self.queryset.values_list('id', flat=True)[:2]
        params = {'id': [str(id) for id in id_list]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_name(self):
        params = {'name': ['Interface 1', 'Interface 2']}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_enabled(self):
        params = {'enabled': 'true'}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {'enabled': 'false'}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_parent(self):
        # Create child interfaces
        parent_interface = VMInterface.objects.first()
        child_interfaces = (
            VMInterface(virtual_machine=parent_interface.virtual_machine, name='Child 1', parent=parent_interface),
            VMInterface(virtual_machine=parent_interface.virtual_machine, name='Child 2', parent=parent_interface),
            VMInterface(virtual_machine=parent_interface.virtual_machine, name='Child 3', parent=parent_interface),
        )
        VMInterface.objects.bulk_create(child_interfaces)

        params = {'parent_id': [parent_interface.pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 3)

    def test_mtu(self):
        params = {'mtu': [100, 200]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_virtual_machine(self):
        vms = VirtualMachine.objects.all()[:2]
        params = {'virtual_machine_id': [vms[0].pk, vms[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {'virtual_machine': [vms[0].name, vms[1].name]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_mac_address(self):
        params = {'mac_address': ['00-00-00-00-00-01', '00-00-00-00-00-02']}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
