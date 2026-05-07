from decimal import Decimal

from django.contrib.contenttypes.models import ContentType
from django.test import override_settings
from django.urls import reverse

from dcim.choices import InterfaceModeChoices
from dcim.models import DeviceRole, Platform, Site
from extras.models import ConfigTemplate
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
            Cluster(
                name='Cluster 1',
                group=clustergroups[0],
                type=clustertypes[0],
                status=ClusterStatusChoices.STATUS_ACTIVE,
                scope=sites[0],
            ),
            Cluster(
                name='Cluster 2',
                group=clustergroups[0],
                type=clustertypes[0],
                status=ClusterStatusChoices.STATUS_ACTIVE,
                scope=sites[0],
            ),
            Cluster(
                name='Cluster 3',
                group=clustergroups[0],
                type=clustertypes[0],
                status=ClusterStatusChoices.STATUS_ACTIVE,
                scope=sites[0],
            ),
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

        cls.csv_data = {
            'default': (
                "name,type,status,scope_type,scope_id",
                f"Cluster 4,Cluster Type 1,active,dcim.site,{sites[0].pk}",
                f"Cluster 5,Cluster Type 1,active,dcim.site,{sites[0].pk}",
                f"Cluster 6,Cluster Type 1,active,dcim.site,{sites[0].pk}",
            ),
            'scope_name': (
                "name,type,status,scope_type,scope_name",
                f"Cluster 4,Cluster Type 1,active,dcim.site,{sites[0].name}",
                f"Cluster 5,Cluster Type 1,active,dcim.site,{sites[0].name}",
                f"Cluster 6,Cluster Type 1,active,dcim.site,{sites[0].name}",
            ),
        }

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


class VirtualMachineTypeTestCase(ViewTestCases.PrimaryObjectViewTestCase):
    model = VirtualMachineType

    @classmethod
    def setUpTestData(cls):

        cls.platforms = (
            Platform(name='Platform 1', slug='platform-1'),
            Platform(name='Platform 2', slug='platform-2'),
            Platform(name='Platform 3', slug='platform-3'),
        )
        for platform in cls.platforms:
            platform.save()

        cls.virtual_machine_types = (
            VirtualMachineType(
                name='Virtual Machine Type 1',
                slug='virtual-machine-type-1',
                default_platform=cls.platforms[0],
                default_vcpus=Decimal('1.00'),
                default_memory=1024,
            ),
            VirtualMachineType(
                name='Virtual Machine Type 2',
                slug='virtual-machine-type-2',
                default_platform=cls.platforms[1],
                default_vcpus=Decimal('2.00'),
                default_memory=2048,
            ),
            VirtualMachineType(
                name='Virtual Machine Type 3',
                slug='virtual-machine-type-3',
                default_platform=cls.platforms[2],
                default_vcpus=Decimal('4.00'),
                default_memory=4096,
            ),
        )
        for virtual_machine_type in cls.virtual_machine_types:
            virtual_machine_type.save()

        tags = create_tags('Alpha', 'Bravo', 'Charlie')

        cls.form_data = {
            'name': 'Virtual Machine Type X',
            'slug': 'virtual-machine-type-x',
            'default_platform': cls.platforms[1].pk,
            'default_vcpus': 8,
            'default_memory': 8192,
            'description': 'A new virtual machine type',
            'comments': 'Some comments',
            'tags': [t.pk for t in tags],
        }

        cls.csv_data = (
            'name,slug,default_platform,default_vcpus,default_memory,description',
            'Virtual Machine Type 4,virtual-machine-type-4,Platform 1,1.00,1024,Fourth virtual machine type',
            'Virtual Machine Type 5,virtual-machine-type-5,Platform 2,2.00,2048,Fifth virtual machine type',
            'Virtual Machine Type 6,virtual-machine-type-6,Platform 3,4.00,4096,Sixth virtual machine type',
        )

        cls.csv_update_data = (
            'id,name,description',
            f'{cls.virtual_machine_types[0].pk},Virtual Machine Type 7,New description 7',
            f'{cls.virtual_machine_types[1].pk},Virtual Machine Type 8,New description 8',
            f'{cls.virtual_machine_types[2].pk},Virtual Machine Type 9,New description 9',
        )

        cls.bulk_edit_data = {
            'default_platform': cls.platforms[2].pk,
            'default_vcpus': 16,
            'default_memory': 16384,
            'description': 'New description',
        }


class VirtualMachineTestCase(ViewTestCases.PrimaryObjectViewTestCase):
    model = VirtualMachine

    @classmethod
    def setUpTestData(cls):

        roles = (
            DeviceRole(name='Device Role 1', slug='device-role-1'),
            DeviceRole(name='Device Role 2', slug='device-role-2'),
        )
        for role in roles:
            role.save()

        cls.platforms = (
            Platform(name='Platform 1', slug='platform-1'),
            Platform(name='Platform 2', slug='platform-2'),
        )
        for platform in cls.platforms:
            platform.save()

        cls.sites = (
            Site(name='Site 1', slug='site-1'),
            Site(name='Site 2', slug='site-2'),
        )
        Site.objects.bulk_create(cls.sites)

        clustertype = ClusterType.objects.create(name='Cluster Type 1', slug='cluster-type-1')

        cls.clusters = (
            Cluster(name='Cluster 1', type=clustertype, scope=cls.sites[0]),
            Cluster(name='Cluster 2', type=clustertype, scope=cls.sites[1]),
        )
        for cluster in cls.clusters:
            cluster.save()

        cls.devices = (
            create_test_device('device1', site=cls.sites[0], cluster=cls.clusters[0]),
            create_test_device('device2', site=cls.sites[1], cluster=cls.clusters[1]),
        )

        cls.vm_types = (
            VirtualMachineType(
                name='Virtual Machine Type 1',
                slug='virtual-machine-type-1',
                default_platform=cls.platforms[0],
                default_vcpus=Decimal('2.00'),
                default_memory=4096,
            ),
            VirtualMachineType(
                name='Virtual Machine Type 2',
                slug='virtual-machine-type-2',
                default_platform=cls.platforms[1],
                default_vcpus=Decimal('4.00'),
                default_memory=8192,
            ),
        )
        for vm_type in cls.vm_types:
            vm_type.save()

        virtual_machines = (
            VirtualMachine(
                name='Virtual Machine 1',
                virtual_machine_type=cls.vm_types[0],
                site=cls.sites[0],
                cluster=cls.clusters[0],
                device=cls.devices[0],
                role=roles[0],
                platform=cls.platforms[0],
            ),
            VirtualMachine(
                name='Virtual Machine 2',
                virtual_machine_type=cls.vm_types[0],
                site=cls.sites[0],
                cluster=cls.clusters[0],
                device=cls.devices[0],
                role=roles[0],
                platform=cls.platforms[0],
            ),
            VirtualMachine(
                name='Virtual Machine 3',
                virtual_machine_type=cls.vm_types[1],
                site=cls.sites[0],
                cluster=cls.clusters[0],
                device=cls.devices[0],
                role=roles[0],
                platform=cls.platforms[0],
            ),
        )
        VirtualMachine.objects.bulk_create(virtual_machines)

        tags = create_tags('Alpha', 'Bravo', 'Charlie')

        cls.form_data = {
            'virtual_machine_type': cls.vm_types[1].pk,
            'cluster': cls.clusters[1].pk,
            'device': cls.devices[1].pk,
            'site': cls.sites[1].pk,
            'tenant': None,
            'platform': cls.platforms[1].pk,
            'name': 'Virtual Machine X',
            'status': VirtualMachineStatusChoices.STATUS_STAGED,
            'start_on_boot': VirtualMachineStartOnBootChoices.STATUS_ON,
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
            'name,status,site,cluster,device,virtual_machine_type',
            'Virtual Machine 4,active,Site 1,Cluster 1,device1,Virtual Machine Type 1',
            'Virtual Machine 5,active,Site 1,Cluster 1,device1,Virtual Machine Type 2',
            'Virtual Machine 6,active,Site 1,Cluster 1,,Virtual Machine Type 1',
        )

        cls.csv_update_data = (
            'id,name,comments',
            f'{virtual_machines[0].pk},Virtual Machine 7,New comments 7',
            f'{virtual_machines[1].pk},Virtual Machine 8,New comments 8',
            f'{virtual_machines[2].pk},Virtual Machine 9,New comments 9',
        )

        cls.bulk_edit_data = {
            'virtual_machine_type': cls.vm_types[1].pk,
            'site': cls.sites[1].pk,
            'cluster': cls.clusters[1].pk,
            'device': cls.devices[1].pk,
            'tenant': None,
            'platform': cls.platforms[1].pk,
            'status': VirtualMachineStatusChoices.STATUS_STAGED,
            'role': roles[1].pk,
            'vcpus': Decimal('8.00'),
            'memory': 65535,
            'disk': 8000,
            'comments': 'New comments',
            'start_on_boot': VirtualMachineStartOnBootChoices.STATUS_OFF,
        }

    @override_settings(EXEMPT_VIEW_PERMISSIONS=['*'], EXEMPT_EXCLUDE_MODELS=[])
    def test_create_virtualmachine_with_type_defaults(self):
        self.add_permissions('virtualization.add_virtualmachine')

        response = self.client.post(
            self._get_url('add'),
            data={
                'name': 'Virtual Machine Defaults',
                'virtual_machine_type': self.vm_types[0].pk,
                'status': VirtualMachineStatusChoices.STATUS_ACTIVE,
                'start_on_boot': VirtualMachineStartOnBootChoices.STATUS_OFF,
                'site': self.sites[0].pk,
                'cluster': self.clusters[0].pk,
                'platform': '',
                'vcpus': '',
                'memory': '',
            },
        )
        self.assertHttpStatus(response, 302)

        vm = VirtualMachine.objects.get(name='Virtual Machine Defaults')
        self.assertEqual(vm.virtual_machine_type, self.vm_types[0])
        self.assertEqual(vm.platform, self.platforms[0])
        self.assertEqual(vm.vcpus, self.vm_types[0].default_vcpus)
        self.assertEqual(vm.memory, self.vm_types[0].default_memory)

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

    def test_bulk_edit_device_context_preserves_device(self):
        """
        Regression test for #21990: Bulk editing VMs from the Device's VMs tab (URL contains
        ?device=<id>) must not clear the device field on those VMs.
        """
        self.add_permissions('virtualization.view_virtualmachine', 'virtualization.change_virtualmachine')

        device = VirtualMachine.objects.filter(device__isnull=False).first().device
        vms = list(VirtualMachine.objects.filter(device=device)[:3])
        pk_list = [vm.pk for vm in vms]

        data = {
            'pk': pk_list,
            '_apply': True,
            # Only change status — device is intentionally omitted
            'status': VirtualMachineStatusChoices.STATUS_STAGED,
        }

        # Simulate navigation from Device -> Virtual Machines tab by passing ?device=<id> as GET param
        url = reverse('virtualization:virtualmachine_bulk_edit') + f'?device={device.pk}'
        response = self.client.post(url, data)
        self.assertHttpStatus(response, 302)

        for vm in VirtualMachine.objects.filter(pk__in=pk_list):
            self.assertEqual(vm.device, device, msg=f"Device was unexpectedly cleared on VM '{vm.name}'")
            self.assertEqual(vm.status, VirtualMachineStatusChoices.STATUS_STAGED)

    def test_virtualmachine_renderconfig(self):
        configtemplate = ConfigTemplate.objects.create(
            name='Test Config Template',
            template_code='Config for VM {{ virtualmachine.name }}'
        )
        vm = VirtualMachine.objects.first()
        vm.config_template = configtemplate
        vm.save()
        url = reverse('virtualization:virtualmachine_render-config', kwargs={'pk': vm.pk})

        # User with only view permission should NOT be able to render config
        self.add_permissions('virtualization.view_virtualmachine')
        self.assertHttpStatus(self.client.get(url), 403)

        # With render_config permission added should be able to render config
        self.add_permissions('virtualization.render_config_virtualmachine')
        self.assertHttpStatus(self.client.get(url), 200)

        # With view permission removed should NOT be able to render config
        self.remove_permissions('virtualization.view_virtualmachine')
        self.assertHttpStatus(self.client.get(url), 403)

    def test_virtualmachine_renderconfig_with_config_template_id(self):
        default_template = ConfigTemplate.objects.create(
            name='Default Template',
            template_code='Default config for {{ virtualmachine.name }}'
        )
        override_template = ConfigTemplate.objects.create(
            name='Override Template',
            template_code='Override config for {{ virtualmachine.name }}'
        )
        vm = VirtualMachine.objects.first()
        vm.config_template = default_template
        vm.save()

        self.add_permissions(
            'virtualization.view_virtualmachine', 'virtualization.render_config_virtualmachine',
            'extras.view_configtemplate'
        )
        url = reverse('virtualization:virtualmachine_render-config', kwargs={'pk': vm.pk})

        # Render with override config_template_id
        response = self.client.get(url, {'config_template_id': override_template.pk})
        self.assertHttpStatus(response, 200)
        self.assertIn(b'Override config for', response.content)

        # Render with nonexistent config_template_id still returns 200 with error message
        response = self.client.get(url, {'config_template_id': 999999})
        self.assertHttpStatus(response, 200)
        self.assertIn(b'Error rendering template', response.content)

        # Render with non-integer config_template_id still returns 200 with error message
        response = self.client.get(url, {'config_template_id': 'abc'})
        self.assertHttpStatus(response, 200)
        self.assertIn(b'Error rendering template', response.content)

        # Without view_configtemplate permission, override template should not be accessible
        self.remove_permissions('extras.view_configtemplate')
        response = self.client.get(url, {'config_template_id': override_template.pk})
        self.assertHttpStatus(response, 200)
        self.assertIn(b'Error rendering template', response.content)


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
            'mtu': 2000,
            'description': 'New description',
            'mode': InterfaceModeChoices.MODE_TAGGED,
            'untagged_vlan': vlans[0].pk,
            'tagged_vlans': [v.pk for v in vlans[1:4]],
            'vrf': vrfs[0].pk,
            'tags': [t.pk for t in tags],
        }

        cls.csv_data = (
            "virtual_machine,name,vrf.pk,mode,untagged_vlan,tagged_vlans",
            (
                f"Virtual Machine 2,Interface 4,{vrfs[0].pk},"
                f"tagged,{vlans[0].vid},'{','.join([str(v.vid) for v in vlans[1:4]])}'"
            ),
            (
                f"Virtual Machine 2,Interface 5,{vrfs[0].pk},"
                f"tagged,{vlans[0].vid},'{','.join([str(v.vid) for v in vlans[1:4]])}'"
            ),
            (
                f"Virtual Machine 2,Interface 6,{vrfs[0].pk},"
                f"tagged,{vlans[0].vid},'{','.join([str(v.vid) for v in vlans[1:4]])}'"
            ),
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
