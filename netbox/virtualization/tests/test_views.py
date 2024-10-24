from django.contrib.contenttypes.models import ContentType
from django.test import override_settings
from django.urls import reverse
from netaddr import EUI

from dcim.choices import InterfaceModeChoices
from dcim.models import DeviceRole, Platform, Site
from ipam.models import VLAN, VRF
from utilities.testing import ViewTestCases, create_tags, create_test_device, create_test_virtualmachine
from virtualization.choices import *
from virtualization.models import *


class ClusterGroupTestCase(ViewTestCases.OrganizationalObjectViewTestCase):
    model = ClusterGroup

    @classmethod
    def setUpTestData(cls):

        cluster_groups = (
            ClusterGroup(name='Cluster Group 1', slug='cluster-group-1'),
            ClusterGroup(name='Cluster Group 2', slug='cluster-group-2'),
            ClusterGroup(name='Cluster Group 3', slug='cluster-group-3'),
        )
        ClusterGroup.objects.bulk_create(cluster_groups)

        tags = create_tags('Alpha', 'Bravo', 'Charlie')

        cls.form_data = {
            'name': 'Cluster Group X',
            'slug': 'cluster-group-x',
            'description': 'A new cluster group',
            'tags': [t.pk for t in tags],
        }

        cls.csv_data = (
            "name,slug,description",
            "Cluster Group 4,cluster-group-4,Fourth cluster group",
            "Cluster Group 5,cluster-group-5,Fifth cluster group",
            "Cluster Group 6,cluster-group-6,Sixth cluster group",
        )

        cls.csv_update_data = (
            "id,name,description",
            f"{cluster_groups[0].pk},Cluster Group 7,Fourth cluster group7",
            f"{cluster_groups[1].pk},Cluster Group 8,Fifth cluster group8",
            f"{cluster_groups[2].pk},Cluster Group 9,Sixth cluster group9",
        )

        cls.bulk_edit_data = {
            'description': 'New description',
        }


class ClusterTypeTestCase(ViewTestCases.OrganizationalObjectViewTestCase):
    model = ClusterType

    @classmethod
    def setUpTestData(cls):

        cluster_types = (
            ClusterType(name='Cluster Type 1', slug='cluster-type-1'),
            ClusterType(name='Cluster Type 2', slug='cluster-type-2'),
            ClusterType(name='Cluster Type 3', slug='cluster-type-3'),
        )
        ClusterType.objects.bulk_create(cluster_types)

        tags = create_tags('Alpha', 'Bravo', 'Charlie')

        cls.form_data = {
            'name': 'Cluster Type X',
            'slug': 'cluster-type-x',
            'description': 'A new cluster type',
            'tags': [t.pk for t in tags],
        }

        cls.csv_data = (
            "name,slug,description",
            "Cluster Type 4,cluster-type-4,Fourth cluster type",
            "Cluster Type 5,cluster-type-5,Fifth cluster type",
            "Cluster Type 6,cluster-type-6,Sixth cluster type",
        )

        cls.csv_update_data = (
            "id,name,description",
            f"{cluster_types[0].pk},Cluster Type 7,Fourth cluster type7",
            f"{cluster_types[1].pk},Cluster Type 8,Fifth cluster type8",
            f"{cluster_types[2].pk},Cluster Type 9,Sixth cluster type9",
        )

        cls.bulk_edit_data = {
            'description': 'New description',
        }


class ClusterTestCase(ViewTestCases.PrimaryObjectViewTestCase):
    model = Cluster

    @classmethod
    def setUpTestData(cls):

        sites = (
            Site(name='Site 1', slug='site-1'),
            Site(name='Site 2', slug='site-2'),
        )
        Site.objects.bulk_create(sites)

        clustergroups = (
            ClusterGroup(name='Cluster Group 1', slug='cluster-group-1'),
            ClusterGroup(name='Cluster Group 2', slug='cluster-group-2'),
        )
        ClusterGroup.objects.bulk_create(clustergroups)

        clustertypes = (
            ClusterType(name='Cluster Type 1', slug='cluster-type-1'),
            ClusterType(name='Cluster Type 2', slug='cluster-type-2'),
        )
        ClusterType.objects.bulk_create(clustertypes)

        clusters = (
            Cluster(name='Cluster 1', group=clustergroups[0], type=clustertypes[0], status=ClusterStatusChoices.STATUS_ACTIVE, scope=sites[0]),
            Cluster(name='Cluster 2', group=clustergroups[0], type=clustertypes[0], status=ClusterStatusChoices.STATUS_ACTIVE, scope=sites[0]),
            Cluster(name='Cluster 3', group=clustergroups[0], type=clustertypes[0], status=ClusterStatusChoices.STATUS_ACTIVE, scope=sites[0]),
        )
        for cluster in clusters:
            cluster.save()

        tags = create_tags('Alpha', 'Bravo', 'Charlie')

        cls.form_data = {
            'name': 'Cluster X',
            'group': clustergroups[1].pk,
            'type': clustertypes[1].pk,
            'status': ClusterStatusChoices.STATUS_OFFLINE,
            'tenant': None,
            'scope_type': ContentType.objects.get_for_model(Site).pk,
            'scope': sites[1].pk,
            'comments': 'Some comments',
            'tags': [t.pk for t in tags],
        }

        cls.csv_data = (
            "name,type,status",
            "Cluster 4,Cluster Type 1,active",
            "Cluster 5,Cluster Type 1,active",
            "Cluster 6,Cluster Type 1,active",
        )

        cls.csv_update_data = (
            "id,name,comments",
            f"{clusters[0].pk},Cluster 7,New comments 7",
            f"{clusters[1].pk},Cluster 8,New comments 8",
            f"{clusters[2].pk},Cluster 9,New comments 9",
        )

        cls.bulk_edit_data = {
            'group': clustergroups[1].pk,
            'type': clustertypes[1].pk,
            'status': ClusterStatusChoices.STATUS_OFFLINE,
            'tenant': None,
            'comments': 'New comments',
        }

    @override_settings(EXEMPT_VIEW_PERMISSIONS=['*'])
    def test_cluster_virtualmachines(self):
        cluster = Cluster.objects.first()

        url = reverse('virtualization:cluster_virtualmachines', kwargs={'pk': cluster.pk})
        self.assertHttpStatus(self.client.get(url), 200)

    @override_settings(EXEMPT_VIEW_PERMISSIONS=['*'])
    def test_cluster_devices(self):
        cluster = Cluster.objects.first()

        url = reverse('virtualization:cluster_devices', kwargs={'pk': cluster.pk})
        self.assertHttpStatus(self.client.get(url), 200)


class VirtualMachineTestCase(ViewTestCases.PrimaryObjectViewTestCase):
    model = VirtualMachine

    @classmethod
    def setUpTestData(cls):

        roles = (
            DeviceRole(name='Device Role 1', slug='device-role-1'),
            DeviceRole(name='Device Role 2', slug='device-role-2'),
        )
        DeviceRole.objects.bulk_create(roles)

        platforms = (
            Platform(name='Platform 1', slug='platform-1'),
            Platform(name='Platform 2', slug='platform-2'),
        )
        Platform.objects.bulk_create(platforms)

        sites = (
            Site(name='Site 1', slug='site-1'),
            Site(name='Site 2', slug='site-2'),
        )
        Site.objects.bulk_create(sites)

        clustertype = ClusterType.objects.create(name='Cluster Type 1', slug='cluster-type-1')

        clusters = (
            Cluster(name='Cluster 1', type=clustertype, scope=sites[0]),
            Cluster(name='Cluster 2', type=clustertype, scope=sites[1]),
        )
        for cluster in clusters:
            cluster.save()

        devices = (
            create_test_device('device1', site=sites[0], cluster=clusters[0]),
            create_test_device('device2', site=sites[1], cluster=clusters[1]),
        )

        virtual_machines = (
            VirtualMachine(name='Virtual Machine 1', site=sites[0], cluster=clusters[0], device=devices[0], role=roles[0], platform=platforms[0]),
            VirtualMachine(name='Virtual Machine 2', site=sites[0], cluster=clusters[0], device=devices[0], role=roles[0], platform=platforms[0]),
            VirtualMachine(name='Virtual Machine 3', site=sites[0], cluster=clusters[0], device=devices[0], role=roles[0], platform=platforms[0]),
        )
        VirtualMachine.objects.bulk_create(virtual_machines)

        tags = create_tags('Alpha', 'Bravo', 'Charlie')

        cls.form_data = {
            'cluster': clusters[1].pk,
            'device': devices[1].pk,
            'site': sites[1].pk,
            'tenant': None,
            'platform': platforms[1].pk,
            'name': 'Virtual Machine X',
            'status': VirtualMachineStatusChoices.STATUS_STAGED,
            'role': roles[1].pk,
            'primary_ip4': None,
            'primary_ip6': None,
            'vcpus': 4,
            'memory': 32768,
            'disk': 4000,
            'serial': 'aaa-111',
            'comments': 'Some comments',
            'tags': [t.pk for t in tags],
            'local_context_data': None,
        }

        cls.csv_data = (
            "name,status,site,cluster,device",
            "Virtual Machine 4,active,Site 1,Cluster 1,device1",
            "Virtual Machine 5,active,Site 1,Cluster 1,device1",
            "Virtual Machine 6,active,Site 1,Cluster 1,",
        )

        cls.csv_update_data = (
            "id,name,comments",
            f"{virtual_machines[0].pk},Virtual Machine 7,New comments 7",
            f"{virtual_machines[1].pk},Virtual Machine 8,New comments 8",
            f"{virtual_machines[2].pk},Virtual Machine 9,New comments 9",
        )

        cls.bulk_edit_data = {
            'site': sites[1].pk,
            'cluster': clusters[1].pk,
            'device': devices[1].pk,
            'tenant': None,
            'platform': platforms[1].pk,
            'status': VirtualMachineStatusChoices.STATUS_STAGED,
            'role': roles[1].pk,
            'vcpus': 8,
            'memory': 65535,
            'disk': 8000,
            'comments': 'New comments',
        }

    @override_settings(EXEMPT_VIEW_PERMISSIONS=['*'])
    def test_virtualmachine_interfaces(self):
        virtualmachine = VirtualMachine.objects.first()
        vminterfaces = (
            VMInterface(virtual_machine=virtualmachine, name='Interface 1'),
            VMInterface(virtual_machine=virtualmachine, name='Interface 2'),
            VMInterface(virtual_machine=virtualmachine, name='Interface 3'),
        )
        VMInterface.objects.bulk_create(vminterfaces)

        url = reverse('virtualization:virtualmachine_interfaces', kwargs={'pk': virtualmachine.pk})
        self.assertHttpStatus(self.client.get(url), 200)


class VMInterfaceTestCase(ViewTestCases.DeviceComponentViewTestCase):
    model = VMInterface
    validation_excluded_fields = ('name',)

    @classmethod
    def setUpTestData(cls):

        site = Site.objects.create(name='Site 1', slug='site-1')
        role = DeviceRole.objects.create(name='Device Role 1', slug='device-role-1')
        clustertype = ClusterType.objects.create(name='Cluster Type 1', slug='cluster-type-1')
        cluster = Cluster.objects.create(name='Cluster 1', type=clustertype, scope=site)
        virtualmachines = (
            VirtualMachine(name='Virtual Machine 1', site=site, cluster=cluster, role=role),
            VirtualMachine(name='Virtual Machine 2', site=site, cluster=cluster, role=role),
        )
        VirtualMachine.objects.bulk_create(virtualmachines)

        interfaces = VMInterface.objects.bulk_create([
            VMInterface(virtual_machine=virtualmachines[0], name='Interface 1'),
            VMInterface(virtual_machine=virtualmachines[0], name='Interface 2'),
            VMInterface(virtual_machine=virtualmachines[0], name='Interface 3'),
            VMInterface(virtual_machine=virtualmachines[1], name='BRIDGE'),
        ])

        vlans = (
            VLAN(vid=1, name='VLAN1', site=site),
            VLAN(vid=101, name='VLAN101', site=site),
            VLAN(vid=102, name='VLAN102', site=site),
            VLAN(vid=103, name='VLAN103', site=site),
        )
        VLAN.objects.bulk_create(vlans)

        vrfs = (
            VRF(name='VRF 1'),
            VRF(name='VRF 2'),
            VRF(name='VRF 3'),
        )
        VRF.objects.bulk_create(vrfs)

        tags = create_tags('Alpha', 'Bravo', 'Charlie')

        cls.form_data = {
            'virtual_machine': virtualmachines[0].pk,
            'name': 'Interface X',
            'enabled': False,
            'bridge': interfaces[1].pk,
            'mac_address': EUI('01-02-03-04-05-06'),
            'mtu': 65000,
            'description': 'New description',
            'mode': InterfaceModeChoices.MODE_TAGGED,
            'untagged_vlan': vlans[0].pk,
            'tagged_vlans': [v.pk for v in vlans[1:4]],
            'vrf': vrfs[0].pk,
            'tags': [t.pk for t in tags],
        }

        cls.bulk_create_data = {
            'virtual_machine': virtualmachines[1].pk,
            'name': 'Interface [4-6]',
            'enabled': False,
            'bridge': interfaces[3].pk,
            'mac_address': EUI('01-02-03-04-05-06'),
            'mtu': 2000,
            'description': 'New description',
            'mode': InterfaceModeChoices.MODE_TAGGED,
            'untagged_vlan': vlans[0].pk,
            'tagged_vlans': [v.pk for v in vlans[1:4]],
            'vrf': vrfs[0].pk,
            'tags': [t.pk for t in tags],
        }

        cls.csv_data = (
            "virtual_machine,name,vrf.pk",
            f"Virtual Machine 2,Interface 4,{vrfs[0].pk}",
            f"Virtual Machine 2,Interface 5,{vrfs[0].pk}",
            f"Virtual Machine 2,Interface 6,{vrfs[0].pk}",
        )

        cls.csv_update_data = (
            "id,name,description",
            f"{interfaces[0].pk},Interface 7,New description 7",
            f"{interfaces[1].pk},Interface 8,New description 8",
            f"{interfaces[2].pk},Interface 9,New description 9",
        )

        cls.bulk_edit_data = {
            'enabled': False,
            'mtu': 2000,
            'description': 'New description',
            'mode': InterfaceModeChoices.MODE_TAGGED,
            'untagged_vlan': vlans[0].pk,
            'tagged_vlans': [v.pk for v in vlans[1:4]],
        }

    def test_bulk_delete_child_interfaces(self):
        interface1 = VMInterface.objects.get(name='Interface 1')
        virtual_machine = interface1.virtual_machine
        self.add_permissions('virtualization.delete_vminterface')

        # Create a child interface
        child = VMInterface.objects.create(
            virtual_machine=virtual_machine,
            name='Interface 1A',
            parent=interface1
        )
        self.assertEqual(virtual_machine.interfaces.count(), 4)

        # Attempt to delete only the parent interface
        data = {
            'confirm': True,
        }
        self.client.post(self._get_url('delete', interface1), data)
        self.assertEqual(virtual_machine.interfaces.count(), 4)  # Parent was not deleted

        # Attempt to bulk delete parent & child together
        data = {
            'pk': [interface1.pk, child.pk],
            'confirm': True,
            '_confirm': True,  # Form button
        }
        self.client.post(self._get_url('bulk_delete'), data)
        self.assertEqual(virtual_machine.interfaces.count(), 2)  # Child & parent were both deleted


class VirtualDiskTestCase(ViewTestCases.DeviceComponentViewTestCase):
    model = VirtualDisk
    validation_excluded_fields = ('name',)

    @classmethod
    def setUpTestData(cls):
        virtualmachine = create_test_virtualmachine('Virtual Machine 1')

        disks = VirtualDisk.objects.bulk_create([
            VirtualDisk(virtual_machine=virtualmachine, name='Virtual Disk 1', size=10),
            VirtualDisk(virtual_machine=virtualmachine, name='Virtual Disk 2', size=10),
            VirtualDisk(virtual_machine=virtualmachine, name='Virtual Disk 3', size=10),
        ])

        tags = create_tags('Alpha', 'Bravo', 'Charlie')

        cls.form_data = {
            'virtual_machine': virtualmachine.pk,
            'name': 'Virtual Disk X',
            'size': 20,
            'description': 'New description',
            'tags': [t.pk for t in tags],
        }

        cls.bulk_create_data = {
            'virtual_machine': virtualmachine.pk,
            'name': 'Virtual Disk [4-6]',
            'size': 10,
            'tags': [t.pk for t in tags],
        }

        cls.csv_data = (
            "virtual_machine,name,size,description",
            "Virtual Machine 1,Disk 4,20,Fourth",
            "Virtual Machine 1,Disk 5,20,Fifth",
            "Virtual Machine 1,Disk 6,20,Sixth",
        )

        cls.csv_update_data = (
            "id,name,size",
            f"{disks[0].pk},disk1,20",
            f"{disks[1].pk},disk2,20",
            f"{disks[2].pk},disk3,20",
        )

        cls.bulk_edit_data = {
            'size': 30,
            'description': 'New description',
        }
