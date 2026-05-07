import logging

from django.test import tag
from django.urls import reverse
from netaddr import IPNetwork
from rest_framework import status

from core.models import ObjectType
from dcim.choices import InterfaceModeChoices
from dcim.models import Platform, Site
from extras.choices import CustomFieldTypeChoices
from extras.models import ConfigTemplate, CustomField
from ipam.choices import VLANQinQRoleChoices
from ipam.models import VLAN, VRF, Prefix
from users.constants import TOKEN_PREFIX
from users.models import Token
from utilities.testing import (
    APITestCase,
    APIViewTestCases,
    create_test_device,
    create_test_nat_ip_pair,
    create_test_virtualmachine,
    disable_logging,
)
from virtualization.choices import *
from virtualization.models import *


class AppTest(APITestCase):

    def test_root(self):

        url = reverse('virtualization-api:api-root')
        response = self.client.get('{}?format=api'.format(url), **self.header)

        self.assertEqual(response.status_code, 200)


class ClusterTypeTest(APIViewTestCases.APIViewTestCase):
    model = ClusterType
    brief_fields = ['cluster_count', 'description', 'display', 'id', 'name', 'slug', 'url']
    create_data = [
        {
            'name': 'Cluster Type 4',
            'slug': 'cluster-type-4',
        },
        {
            'name': 'Cluster Type 5',
            'slug': 'cluster-type-5',
        },
        {
            'name': 'Cluster Type 6',
            'slug': 'cluster-type-6',
        },
    ]
    bulk_update_data = {
        'description': 'New description',
    }

    @classmethod
    def setUpTestData(cls):

        cluster_types = (
            ClusterType(name='Cluster Type 1', slug='cluster-type-1'),
            ClusterType(name='Cluster Type 2', slug='cluster-type-2'),
            ClusterType(name='Cluster Type 3', slug='cluster-type-3'),
        )
        ClusterType.objects.bulk_create(cluster_types)


class ClusterGroupTest(APIViewTestCases.APIViewTestCase):
    model = ClusterGroup
    brief_fields = ['cluster_count', 'description', 'display', 'id', 'name', 'slug', 'url']
    create_data = [
        {
            'name': 'Cluster Group 4',
            'slug': 'cluster-type-4',
        },
        {
            'name': 'Cluster Group 5',
            'slug': 'cluster-type-5',
        },
        {
            'name': 'Cluster Group 6',
            'slug': 'cluster-type-6',
        },
    ]
    bulk_update_data = {
        'description': 'New description',
    }

    @classmethod
    def setUpTestData(cls):

        cluster_Groups = (
            ClusterGroup(name='Cluster Group 1', slug='cluster-type-1'),
            ClusterGroup(name='Cluster Group 2', slug='cluster-type-2'),
            ClusterGroup(name='Cluster Group 3', slug='cluster-type-3'),
        )
        ClusterGroup.objects.bulk_create(cluster_Groups)


class ClusterTest(APIViewTestCases.APIViewTestCase):
    model = Cluster
    brief_fields = ['description', 'display', 'id', 'name', 'url', 'virtualmachine_count']
    bulk_update_data = {
        'status': 'offline',
        'comments': 'New comment',
    }

    @classmethod
    def setUpTestData(cls):

        cluster_types = (
            ClusterType(name='Cluster Type 1', slug='cluster-type-1'),
            ClusterType(name='Cluster Type 2', slug='cluster-type-2'),
        )
        ClusterType.objects.bulk_create(cluster_types)

        cluster_groups = (
            ClusterGroup(name='Cluster Group 1', slug='cluster-group-1'),
            ClusterGroup(name='Cluster Group 2', slug='cluster-group-2'),
        )
        ClusterGroup.objects.bulk_create(cluster_groups)

        clusters = (
            Cluster(
                name='Cluster 1',
                type=cluster_types[0],
                group=cluster_groups[0],
                status=ClusterStatusChoices.STATUS_PLANNED,
            ),
            Cluster(
                name='Cluster 2',
                type=cluster_types[0],
                group=cluster_groups[0],
                status=ClusterStatusChoices.STATUS_PLANNED,
            ),
            Cluster(
                name='Cluster 3',
                type=cluster_types[0],
                group=cluster_groups[0],
                status=ClusterStatusChoices.STATUS_PLANNED,
            ),
        )
        for cluster in clusters:
            cluster.save()

        cls.create_data = [
            {
                'name': 'Cluster 4',
                'type': cluster_types[1].pk,
                'group': cluster_groups[1].pk,
                'status': ClusterStatusChoices.STATUS_STAGING,
            },
            {
                'name': 'Cluster 5',
                'type': cluster_types[1].pk,
                'group': cluster_groups[1].pk,
                'status': ClusterStatusChoices.STATUS_STAGING,
            },
            {
                'name': 'Cluster 6',
                'type': cluster_types[1].pk,
                'group': cluster_groups[1].pk,
                'status': ClusterStatusChoices.STATUS_STAGING,
            },
        ]


class VirtualMachineTypeTest(APIViewTestCases.APIViewTestCase):
    model = VirtualMachineType
    brief_fields = ['description', 'display', 'id', 'name', 'slug', 'url']
    user_permissions = ('dcim.view_platform', 'virtualization.view_virtualmachine')

    @classmethod
    def setUpTestData(cls):
        cls.platforms = (
            Platform.objects.create(name='Platform 1', slug='platform-1'),
            Platform.objects.create(name='Platform 2', slug='platform-2'),
            Platform.objects.create(name='Platform 3', slug='platform-3'),
        )

        cls.virtual_machine_types = (
            VirtualMachineType.objects.create(
                name='Virtual Machine Type 1',
                slug='virtual-machine-type-1',
                default_platform=cls.platforms[0],
                default_vcpus=1,
                default_memory=1024,
            ),
            VirtualMachineType.objects.create(
                name='Virtual Machine Type 2',
                slug='virtual-machine-type-2',
                default_platform=cls.platforms[1],
                default_vcpus=2,
                default_memory=2048,
            ),
            VirtualMachineType.objects.create(
                name='Virtual Machine Type 3',
                slug='virtual-machine-type-3',
                default_platform=cls.platforms[2],
                default_vcpus=4,
                default_memory=4096,
            ),
        )

        cls.create_data = [
            {
                'name': 'Virtual Machine Type 4',
                'slug': 'virtual-machine-type-4',
                'default_platform': cls.platforms[0].pk,
                'default_vcpus': 1,
                'default_memory': 1024,
            },
            {
                'name': 'Virtual Machine Type 5',
                'slug': 'virtual-machine-type-5',
                'default_platform': cls.platforms[1].pk,
                'default_vcpus': 2,
                'default_memory': 2048,
            },
            {
                'name': 'Virtual Machine Type 6',
                'slug': 'virtual-machine-type-6',
                'default_platform': cls.platforms[2].pk,
                'default_vcpus': 4,
                'default_memory': 4096,
            },
        ]

        cls.bulk_update_data = {
            'default_platform': cls.platforms[2].pk,
            'default_vcpus': 8,
            'default_memory': 8192,
            'description': 'New description',
        }


class VirtualMachineTest(APIViewTestCases.APIViewTestCase):
    model = VirtualMachine
    brief_fields = ['description', 'display', 'id', 'name', 'url']
    bulk_update_data = {
        'status': 'staged',
    }
    user_permissions = ('dcim.view_platform', 'virtualization.view_virtualmachinetype')

    @classmethod
    def setUpTestData(cls):
        clustertype = ClusterType.objects.create(name='Cluster Type 1', slug='cluster-type-1')
        clustergroup = ClusterGroup.objects.create(name='Cluster Group 1', slug='cluster-group-1')

        cls.sites = (
            Site(name='Site 1', slug='site-1'),
            Site(name='Site 2', slug='site-2'),
            Site(name='Site 3', slug='site-3'),
        )
        Site.objects.bulk_create(cls.sites)

        cls.clusters = (
            Cluster(name='Cluster 1', type=clustertype, scope=cls.sites[0], group=clustergroup),
            Cluster(name='Cluster 2', type=clustertype, scope=cls.sites[1], group=clustergroup),
            Cluster(name='Cluster 3', type=clustertype),
        )
        for cluster in cls.clusters:
            cluster.save()

        cls.devices = (
            create_test_device('device1', site=cls.sites[0], cluster=cls.clusters[0]),
            create_test_device('device2', site=cls.sites[1], cluster=cls.clusters[1]),
        )

        cls.platforms = (
            Platform.objects.create(name='Platform 1', slug='platform-1'),
            Platform.objects.create(name='Platform 2', slug='platform-2'),
            Platform.objects.create(name='Platform 3', slug='platform-3'),
        )

        cls.vm_types = (
            VirtualMachineType.objects.create(
                name='Virtual Machine Type 1',
                slug='virtual-machine-type-1',
                default_platform=cls.platforms[0],
                default_vcpus=2,
                default_memory=4096,
            ),
            VirtualMachineType.objects.create(
                name='Virtual Machine Type 2',
                slug='virtual-machine-type-2',
                default_platform=cls.platforms[1],
                default_vcpus=4,
                default_memory=8192,
            ),
        )

        virtual_machines = (
            VirtualMachine(
                name='Virtual Machine 1',
                virtual_machine_type=cls.vm_types[0],
                site=cls.sites[0],
                cluster=cls.clusters[0],
                device=cls.devices[0],
                platform=cls.platforms[0],
                vcpus=2,
                memory=4096,
                local_context_data={'A': 1},
            ),
            VirtualMachine(
                name='Virtual Machine 2',
                site=cls.sites[0],
                cluster=cls.clusters[0],
                local_context_data={'B': 2},
            ),
            VirtualMachine(
                name='Virtual Machine 3',
                site=cls.sites[0],
                cluster=cls.clusters[0],
                local_context_data={'C': 3},
                start_on_boot=VirtualMachineStartOnBootChoices.STATUS_ON,
            ),
        )
        VirtualMachine.objects.bulk_create(virtual_machines)

        cls.create_data = [
            {
                'name': 'Virtual Machine 4',
                'site': cls.sites[1].pk,
                'cluster': cls.clusters[1].pk,
                'device': cls.devices[1].pk,
                'virtual_machine_type': cls.vm_types[0].pk,
            },
            {
                'name': 'Virtual Machine 5',
                'site': cls.sites[1].pk,
                'cluster': cls.clusters[1].pk,
                'virtual_machine_type': cls.vm_types[1].pk,
            },
            {
                'name': 'Virtual Machine 6',
                'site': cls.sites[1].pk,
            },
            {
                'name': 'Virtual Machine 7',
                'cluster': cls.clusters[2].pk,
                'virtual_machine_type': cls.vm_types[0].pk,
                'start_on_boot': VirtualMachineStartOnBootChoices.STATUS_ON,
            },
        ]

    def test_virtual_machine_type_defaults_applied_on_create(self):
        data = {
            'name': 'Virtual Machine With Defaults',
            'site': self.sites[1].pk,
            'cluster': self.clusters[1].pk,
            'virtual_machine_type': self.vm_types[0].pk,
            'platform': None,
            'vcpus': None,
            'memory': None,
        }
        self.add_permissions('virtualization.add_virtualmachine')

        response = self.client.post(self._get_list_url(), data, format='json', **self.header)
        self.assertHttpStatus(response, status.HTTP_201_CREATED)

        vm = VirtualMachine.objects.get(pk=response.data['id'])
        self.assertEqual(vm.virtual_machine_type, self.vm_types[0])
        self.assertEqual(vm.platform, self.vm_types[0].default_platform)
        self.assertEqual(vm.vcpus, self.vm_types[0].default_vcpus)
        self.assertEqual(vm.memory, self.vm_types[0].default_memory)

    def test_virtual_machine_type_defaults_do_not_override_explicit_values(self):
        data = {
            'name': 'Virtual Machine With Explicit Values',
            'site': self.sites[1].pk,
            'cluster': self.clusters[1].pk,
            'virtual_machine_type': self.vm_types[0].pk,
            'platform': self.platforms[2].pk,
            'vcpus': 6,
            'memory': 12288,
        }
        self.add_permissions('virtualization.add_virtualmachine')

        response = self.client.post(self._get_list_url(), data, format='json', **self.header)
        self.assertHttpStatus(response, status.HTTP_201_CREATED)

        vm = VirtualMachine.objects.get(pk=response.data['id'])
        self.assertEqual(vm.virtual_machine_type, self.vm_types[0])
        self.assertEqual(vm.platform, self.platforms[2])
        self.assertEqual(vm.vcpus, 6)
        self.assertEqual(vm.memory, 12288)

    def test_setting_virtual_machine_type_on_existing_vm_does_not_backfill_defaults(self):
        vm = VirtualMachine.objects.get(name='Virtual Machine 2')
        self.add_permissions('virtualization.change_virtualmachine')

        response = self.client.patch(
            self._get_detail_url(vm),
            {'virtual_machine_type': self.vm_types[1].pk},
            format='json',
            **self.header,
        )
        self.assertHttpStatus(response, status.HTTP_200_OK)

        vm.refresh_from_db()
        self.assertEqual(vm.virtual_machine_type, self.vm_types[1])
        self.assertIsNone(vm.platform)
        self.assertIsNone(vm.vcpus)
        self.assertIsNone(vm.memory)

    def test_config_context_included_by_default_in_list_view(self):
        """
        Check that config context data is included by default in the virtual machines list.
        """
        virtualmachine = VirtualMachine.objects.first()
        url = '{}?id={}'.format(reverse('virtualization-api:virtualmachine-list'), virtualmachine.pk)
        self.add_permissions('virtualization.view_virtualmachine')

        response = self.client.get(url, **self.header)
        self.assertEqual(response.data['results'][0].get('config_context', {}).get('A'), 1)

    def test_config_context_excluded(self):
        """
        Check that config context data can be excluded by passing ?exclude=config_context.
        """
        url = reverse('virtualization-api:virtualmachine-list') + '?exclude=config_context'
        self.add_permissions('virtualization.view_virtualmachine')

        response = self.client.get(url, **self.header)
        self.assertFalse('config_context' in response.data['results'][0])

    def test_unique_name_per_cluster_constraint(self):
        """
        Check that creating a virtual machine with a duplicate name fails.
        """
        data = {
            'name': 'Virtual Machine 1',
            'cluster': Cluster.objects.first().pk,
        }
        url = reverse('virtualization-api:virtualmachine-list')
        self.add_permissions('virtualization.add_virtualmachine')

        response = self.client.post(url, data, format='json', **self.header)
        self.assertHttpStatus(response, status.HTTP_400_BAD_REQUEST)

    def test_render_config(self):
        configtemplate = ConfigTemplate.objects.create(
            name='Config Template 1',
            template_code='Config for virtual machine {{ virtualmachine.name }}'
        )

        vm = VirtualMachine.objects.first()
        vm.config_template = configtemplate
        vm.save()

        self.add_permissions(
            'virtualization.render_config_virtualmachine', 'virtualization.view_virtualmachine'
        )
        url = reverse('virtualization-api:virtualmachine-render-config', kwargs={'pk': vm.pk})
        response = self.client.post(url, {}, format='json', **self.header)
        self.assertHttpStatus(response, status.HTTP_200_OK)
        self.assertEqual(response.data['content'], f'Config for virtual machine {vm.name}')

    def test_render_config_without_permission(self):
        configtemplate = ConfigTemplate.objects.create(
            name='Config Template 1',
            template_code='Config for virtual machine {{ virtualmachine.name }}'
        )

        vm = VirtualMachine.objects.first()
        vm.config_template = configtemplate
        vm.save()

        # No permissions added - user has no render_config permission
        url = reverse('virtualization-api:virtualmachine-render-config', kwargs={'pk': vm.pk})
        response = self.client.post(url, {}, format='json', **self.header)
        self.assertHttpStatus(response, status.HTTP_404_NOT_FOUND)

    def test_render_config_token_write_enabled(self):
        configtemplate = ConfigTemplate.objects.create(
            name='Config Template 1',
            template_code='Config for virtual machine {{ virtualmachine.name }}'
        )

        vm = VirtualMachine.objects.first()
        vm.config_template = configtemplate
        vm.save()

        self.add_permissions('virtualization.render_config_virtualmachine', 'virtualization.view_virtualmachine')
        url = reverse('virtualization-api:virtualmachine-render-config', kwargs={'pk': vm.pk})

        # Request without token auth should fail with PermissionDenied
        response = self.client.post(url, {}, format='json')
        self.assertHttpStatus(response, status.HTTP_403_FORBIDDEN)

        # Create token with write_enabled=False
        token = Token.objects.create(version=2, user=self.user, write_enabled=False)
        token_header = f'Bearer {TOKEN_PREFIX}{token.key}.{token.token}'

        # Request with write-disabled token should fail
        response = self.client.post(url, {}, format='json', HTTP_AUTHORIZATION=token_header)
        self.assertHttpStatus(response, status.HTTP_403_FORBIDDEN)

        # Enable write and retry
        token.write_enabled = True
        token.save()
        response = self.client.post(url, {}, format='json', HTTP_AUTHORIZATION=token_header)
        self.assertHttpStatus(response, status.HTTP_200_OK)

    def test_list_object_includes_nat_inside_on_primary_ip(self):
        virtualmachine = create_test_virtualmachine('natted-vm')
        interface = VMInterface.objects.create(virtual_machine=virtualmachine, name='eth0')

        real_ip, nat_ip = create_test_nat_ip_pair(
            real_address='10.0.1.10/32',
            nat_address='198.51.100.20/32',
            inside_interface=interface,
        )

        virtualmachine.primary_ip4 = nat_ip
        virtualmachine.save()

        self.add_permissions('virtualization.view_virtualmachine', 'ipam.view_ipaddress')
        response = self.client.get(f'{self._get_list_url()}?id={virtualmachine.pk}', **self.header)
        self.assertHttpStatus(response, status.HTTP_200_OK)

        result = response.data['results'][0]
        for field in ('primary_ip', 'primary_ip4'):
            self.assertEqual(result[field]['address'], str(nat_ip.address))
            self.assertEqual(result[field]['nat_inside']['address'], str(real_ip.address))
            self.assertEqual(result[field]['nat_outside'], [])

    def test_get_object_includes_nat_outside_on_primary_ip(self):
        virtualmachine = create_test_virtualmachine('real-ip-vm')
        interface = VMInterface.objects.create(virtual_machine=virtualmachine, name='eth0')

        real_ip, nat_ip = create_test_nat_ip_pair(
            real_address='10.0.1.11/32',
            nat_address='198.51.100.21/32',
            inside_interface=interface,
        )

        virtualmachine.primary_ip4 = real_ip
        virtualmachine.save()

        self.add_permissions('virtualization.view_virtualmachine', 'ipam.view_ipaddress')
        response = self.client.get(
            f'{self._get_detail_url(virtualmachine)}?exclude=config_context',
            **self.header,
        )
        self.assertHttpStatus(response, status.HTTP_200_OK)

        for field in ('primary_ip', 'primary_ip4'):
            self.assertEqual(response.data[field]['address'], str(real_ip.address))
            self.assertIsNone(response.data[field]['nat_inside'])
            self.assertCountEqual(
                [ip['address'] for ip in response.data[field]['nat_outside']],
                [str(nat_ip.address)],
            )

    def test_render_config_with_config_template_id(self):
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
            'virtualization.render_config_virtualmachine', 'virtualization.view_virtualmachine',
            'extras.view_configtemplate'
        )
        url = reverse('virtualization-api:virtualmachine-render-config', kwargs={'pk': vm.pk})

        # Render with override template
        response = self.client.post(url, {'config_template_id': override_template.pk}, format='json', **self.header)
        self.assertHttpStatus(response, status.HTTP_200_OK)
        self.assertEqual(response.data['content'], f'Override config for {vm.name}')

        # Render with nonexistent config_template_id
        response = self.client.post(url, {'config_template_id': 999999}, format='json', **self.header)
        self.assertHttpStatus(response, status.HTTP_400_BAD_REQUEST)

        # Render with non-integer config_template_id
        response = self.client.post(url, {'config_template_id': 'abc'}, format='json', **self.header)
        self.assertHttpStatus(response, status.HTTP_400_BAD_REQUEST)

        # Without view_configtemplate permission, override template should not be accessible
        self.remove_permissions('extras.view_configtemplate')
        response = self.client.post(url, {'config_template_id': override_template.pk}, format='json', **self.header)
        self.assertHttpStatus(response, status.HTTP_400_BAD_REQUEST)


class VMInterfaceTest(APIViewTestCases.APIViewTestCase):
    model = VMInterface
    brief_fields = ['description', 'display', 'id', 'name', 'url', 'virtual_machine']
    bulk_update_data = {
        'description': 'New description',
    }
    graphql_base_name = 'vm_interface'
    user_permissions = ('virtualization.view_virtualmachine', )

    @classmethod
    def setUpTestData(cls):
        virtualmachine = create_test_virtualmachine('Virtual Machine 1')

        interfaces = (
            VMInterface(virtual_machine=virtualmachine, name='Interface 1'),
            VMInterface(virtual_machine=virtualmachine, name='Interface 2'),
            VMInterface(virtual_machine=virtualmachine, name='Interface 3'),
        )
        VMInterface.objects.bulk_create(interfaces)

        vlans = (
            VLAN(name='VLAN 1', vid=1),
            VLAN(name='VLAN 2', vid=2),
            VLAN(name='VLAN 3', vid=3),
            VLAN(name='SVLAN 1', vid=1001, qinq_role=VLANQinQRoleChoices.ROLE_SERVICE),
        )
        VLAN.objects.bulk_create(vlans)

        vrfs = (
            VRF(name='VRF 1'),
            VRF(name='VRF 2'),
            VRF(name='VRF 3'),
        )
        VRF.objects.bulk_create(vrfs)

        cls.create_data = [
            {
                'virtual_machine': virtualmachine.pk,
                'name': 'Interface 4',
                'mode': InterfaceModeChoices.MODE_TAGGED,
                'tagged_vlans': [vlans[0].pk, vlans[1].pk],
                'untagged_vlan': vlans[2].pk,
                'vrf': vrfs[0].pk,
            },
            {
                'virtual_machine': virtualmachine.pk,
                'name': 'Interface 5',
                'mode': InterfaceModeChoices.MODE_TAGGED,
                'bridge': interfaces[0].pk,
                'tagged_vlans': [vlans[0].pk, vlans[1].pk],
                'untagged_vlan': vlans[2].pk,
                'vrf': vrfs[1].pk,
            },
            {
                'virtual_machine': virtualmachine.pk,
                'name': 'Interface 6',
                'mode': InterfaceModeChoices.MODE_TAGGED,
                'parent': interfaces[1].pk,
                'tagged_vlans': [vlans[0].pk, vlans[1].pk],
                'untagged_vlan': vlans[2].pk,
                'vrf': vrfs[2].pk,
            },
            {
                'virtual_machine': virtualmachine.pk,
                'name': 'Interface 7',
                'mode': InterfaceModeChoices.MODE_Q_IN_Q,
                'qinq_svlan': vlans[3].pk,
            },
        ]

    @tag('regression')
    def test_set_vminterface_as_object_in_custom_field(self):
        cf = CustomField.objects.create(
            name='associated_interface',
            type=CustomFieldTypeChoices.TYPE_OBJECT,
            related_object_type=ObjectType.objects.get_for_model(VMInterface),
            required=False
        )
        cf.object_types.set([ObjectType.objects.get_for_model(Prefix)])
        cf.save()

        prefix = Prefix.objects.create(prefix=IPNetwork('10.0.0.0/12'))
        vmi = VMInterface.objects.first()

        url = reverse('ipam-api:prefix-detail', kwargs={'pk': prefix.pk})
        data = {
            'custom_fields': {
                'associated_interface': vmi.id,
            },
        }

        self.add_permissions('ipam.change_prefix')

        response = self.client.patch(url, data, format='json', **self.header)
        self.assertEqual(response.status_code, 200)

        prefix_data = response.json()
        self.assertEqual(prefix_data['custom_fields']['associated_interface']['id'], vmi.id)

        reloaded_prefix = Prefix.objects.get(pk=prefix.pk)
        self.assertEqual(prefix.pk, reloaded_prefix.pk)
        self.assertNotEqual(reloaded_prefix.cf['associated_interface'], None)

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
        url = self._get_detail_url(interface1)
        with disable_logging(level=logging.WARNING):
            self.client.delete(url, **self.header)
        self.assertEqual(virtual_machine.interfaces.count(), 4)  # Parent was not deleted

        # Attempt to bulk delete parent & child together
        data = [
            {"id": interface1.pk},
            {"id": child.pk},
        ]
        self.client.delete(self._get_list_url(), data, format='json', **self.header)
        self.assertEqual(virtual_machine.interfaces.count(), 2)  # Child & parent were both deleted


class VirtualDiskTest(APIViewTestCases.APIViewTestCase):
    model = VirtualDisk
    brief_fields = ['description', 'display', 'id', 'name', 'size', 'url', 'virtual_machine']
    bulk_update_data = {
        'size': 888,
    }
    graphql_base_name = 'virtual_disk'
    user_permissions = ('virtualization.view_virtualmachine', )

    @classmethod
    def setUpTestData(cls):
        virtualmachine = create_test_virtualmachine('Virtual Machine 1')

        disks = (
            VirtualDisk(virtual_machine=virtualmachine, name='Disk 1', size=10),
            VirtualDisk(virtual_machine=virtualmachine, name='Disk 2', size=20),
            VirtualDisk(virtual_machine=virtualmachine, name='Disk 3', size=30),
        )
        VirtualDisk.objects.bulk_create(disks)

        cls.create_data = [
            {
                'virtual_machine': virtualmachine.pk,
                'name': 'Disk 4',
                'size': 10,
            },
            {
                'virtual_machine': virtualmachine.pk,
                'name': 'Disk 5',
                'size': 20,
            },
            {
                'virtual_machine': virtualmachine.pk,
                'name': 'Disk 6',
                'size': 30,
            },
        ]
