from decimal import Decimal

from django.core.exceptions import ValidationError
from django.test import TestCase

from dcim.models import Platform, Site
from tenancy.models import Tenant
from utilities.testing import create_test_device
from virtualization.models import *


class VirtualMachineTypeTestCase(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.platform = Platform.objects.create(
            name='Type Test Ubuntu 24.04',
            slug='type-test-ubuntu-24-04',
        )
        cls.virtual_machine_type = VirtualMachineType.objects.create(
            name='Small Linux',
            slug='small-linux',
            default_platform=cls.platform,
            default_vcpus=Decimal('2.00'),
            default_memory=4096,
        )

        cls.cluster_type = ClusterType.objects.create(
            name='VM Type Count Cluster Type',
            slug='vm-type-count-cluster-type',
        )
        cls.site = Site.objects.create(
            name='VM Type Count Site',
            slug='vm-type-count-site',
        )
        cls.cluster = Cluster.objects.create(
            name='VM Type Count Cluster',
            type=cls.cluster_type,
            scope=cls.site,
        )

    def test_virtual_machine_type_str_and_defaults(self):
        """
        Verify that the string representation of a VirtualMachineType returns
        its name, and that all default fields (platform, vcpus, memory) are
        stored correctly after creation.
        """
        self.assertEqual(str(self.virtual_machine_type), 'Small Linux')
        self.assertEqual(self.virtual_machine_type.default_platform, self.platform)
        self.assertEqual(self.virtual_machine_type.default_vcpus, Decimal('2.00'))
        self.assertEqual(self.virtual_machine_type.default_memory, 4096)

    def test_virtual_machine_type_virtual_machine_count(self):
        """
        The virtual_machine_count counter cache field should accurately track
        the number of VirtualMachines referencing this type through creation,
        additional insertions, reassignment, and deletion.
        """
        # Starts at zero
        self.assertEqual(self.virtual_machine_type.virtual_machine_count, 0)

        # Create the first VM
        vm1 = VirtualMachine.objects.create(
            name='vm-count-test-1',
            cluster=self.cluster,
            virtual_machine_type=self.virtual_machine_type,
        )
        self.virtual_machine_type.refresh_from_db()
        self.assertEqual(self.virtual_machine_type.virtual_machine_count, 1)

        # Create the second VM
        vm2 = VirtualMachine.objects.create(
            name='vm-count-test-2',
            cluster=self.cluster,
            virtual_machine_type=self.virtual_machine_type,
        )
        self.virtual_machine_type.refresh_from_db()
        self.assertEqual(self.virtual_machine_type.virtual_machine_count, 2)

        # Delete one VM — count should decrement
        vm1.delete()
        self.virtual_machine_type.refresh_from_db()
        self.assertEqual(self.virtual_machine_type.virtual_machine_count, 1)

        # Reassign the remaining VM to no type — count should drop to zero
        vm2.virtual_machine_type = None
        vm2.save()
        self.virtual_machine_type.refresh_from_db()
        self.assertEqual(self.virtual_machine_type.virtual_machine_count, 0)

    def test_virtual_machine_type_invalid_default_vcpus(self):
        """
        default_vcpus below the minimum should fail validation.
        """
        vmt = VirtualMachineType(
            name='Zero vCPU Type',
            slug='zero-vcpu-type',
            default_vcpus=Decimal('0.00'),
        )
        with self.assertRaises(ValidationError):
            vmt.full_clean()


class VirtualMachineTestCase(TestCase):

    @classmethod
    def setUpTestData(cls):
        # Create the cluster type
        cls.cluster_type = ClusterType.objects.create(name='Cluster Type 1', slug='cluster-type-1')

        # Create platforms
        cls.platforms = (
            Platform.objects.create(name='VM Default Ubuntu 24.04', slug='vm-default-ubuntu-24-04'),
            Platform.objects.create(name='VM Default Debian 12', slug='vm-default-debian-12'),
        )

        # Create sites
        cls.sites = (
            Site.objects.create(name='Site 1', slug='site-1'),
            Site.objects.create(name='Site 2', slug='site-2'),
        )

        # Create clusters with various site scopes
        cls.cluster_with_site = Cluster.objects.create(
            name='Cluster with Site',
            type=cls.cluster_type,
            scope=cls.sites[0],
        )
        cls.cluster_with_site2 = Cluster.objects.create(
            name='Cluster with Site 2',
            type=cls.cluster_type,
            scope=cls.sites[1],
        )
        cls.cluster_no_site = Cluster.objects.create(
            name='Cluster No Site',
            type=cls.cluster_type,
            scope=None,
        )

        # Create devices
        cls.device_in_cluster = create_test_device(
            'Device in Cluster',
            site=cls.sites[0],
            cluster=cls.cluster_with_site,
        )
        cls.device_in_cluster2 = create_test_device(
            'Device in Cluster 2',
            site=cls.sites[0],
            cluster=cls.cluster_with_site,
        )
        cls.standalone_device = create_test_device(
            'Standalone Device',
            site=cls.sites[1],
        )

        # Create tenants
        cls.tenants = (
            Tenant.objects.create(name='Tenant 1', slug='tenant-1'),
            Tenant.objects.create(name='Tenant 2', slug='tenant-2'),
        )

        # Create virtual machine types
        cls.vm_types = (
            VirtualMachineType.objects.create(
                name='General Purpose Small',
                slug='general-purpose-small',
                default_platform=cls.platforms[0],
                default_vcpus=Decimal('2.00'),
                default_memory=4096,
            ),
            VirtualMachineType.objects.create(
                name='General Purpose Large',
                slug='general-purpose-large',
                default_platform=cls.platforms[1],
                default_vcpus=Decimal('8.00'),
                default_memory=16384,
            ),
        )

    def test_vm_duplicate_name_per_cluster(self):
        """
        Test that creating two Virtual Machines with the same name in
        the same cluster fails validation.
        """
        vm1 = VirtualMachine(
            cluster=self.cluster_with_site,
            name='Test VM 1',
        )
        vm1.save()

        vm2 = VirtualMachine(
            cluster=vm1.cluster,
            name=vm1.name,
        )

        # Two VMs assigned to the same Cluster and no Tenant should fail validation
        with self.assertRaises(ValidationError):
            vm2.full_clean()

        vm1.tenant = self.tenants[0]
        vm1.save()
        vm2.tenant = self.tenants[0]

        # Two VMs assigned to the same Cluster and the same Tenant should fail validation
        with self.assertRaises(ValidationError):
            vm2.full_clean()

        vm2.tenant = None

        # Two VMs assigned to the same Cluster and different Tenants should pass validation
        vm2.full_clean()
        vm2.save()

    def test_vm_mismatched_site_cluster(self):
        """
        Test that creating a Virtual Machine with a mismatched site and
        cluster fails validation.
        """
        # VM with site only should pass
        VirtualMachine(name='vm1', site=self.sites[0]).full_clean()

        # VM with site, cluster non-site should pass
        VirtualMachine(name='vm2', site=self.sites[0], cluster=self.cluster_no_site).full_clean()

        # VM with non-site cluster only should pass
        VirtualMachine(name='vm3', cluster=self.cluster_no_site).full_clean()

        # VM with mismatched site & cluster should fail
        with self.assertRaises(ValidationError):
            VirtualMachine(name='vm4', site=self.sites[0], cluster=self.cluster_with_site2).full_clean()

        # VM with a cluster site but no direct site should have its site set automatically
        vm = VirtualMachine(name='vm5', site=None, cluster=self.cluster_with_site)
        vm.save()
        self.assertEqual(vm.site, self.sites[0])

    def test_vm_name_case_sensitivity(self):
        vm1 = VirtualMachine(
            cluster=self.cluster_with_site,
            name='virtual machine 1',
        )
        vm1.save()

        vm2 = VirtualMachine(
            cluster=vm1.cluster,
            name='VIRTUAL MACHINE 1',
        )

        # Uniqueness validation for name should ignore case
        with self.assertRaises(ValidationError):
            vm2.full_clean()

    def test_disk_size(self):
        vm = VirtualMachine(
            cluster=self.cluster_with_site,
            name='VM Disk Test',
        )
        vm.save()
        vm.refresh_from_db()
        self.assertEqual(vm.disk, None)

        # Create two VirtualDisks
        VirtualDisk.objects.create(virtual_machine=vm, name='Virtual Disk 1', size=10)
        VirtualDisk.objects.create(virtual_machine=vm, name='Virtual Disk 2', size=10)
        vm.refresh_from_db()
        self.assertEqual(vm.disk, 20)

        # Delete one VirtualDisk
        VirtualDisk.objects.filter(virtual_machine=vm).first().delete()
        vm.refresh_from_db()
        self.assertEqual(vm.disk, 10)

        # Attempt to manually overwrite the aggregate disk size
        vm.disk = 30
        with self.assertRaises(ValidationError):
            vm.full_clean()

    #
    # Virtual Machine Type tests
    #

    def test_vm_type_defaults_applied_on_create(self):
        """
        When a new VirtualMachine is created with a VirtualMachineType and no
        explicit platform, vcpus, or memory, the type's defaults should be
        automatically applied via apply_type_defaults().
        """
        vm = VirtualMachine(
            name='vm-type-defaults',
            cluster=self.cluster_with_site,
            virtual_machine_type=self.vm_types[0],
        )
        vm.full_clean()
        vm.save()
        vm.refresh_from_db()

        self.assertEqual(vm.platform, self.platforms[0])
        self.assertEqual(vm.vcpus, Decimal('2.00'))
        self.assertEqual(vm.memory, 4096)

    def test_vm_type_defaults_do_not_override_explicit_values(self):
        """
        When a new VirtualMachine specifies explicit values for a platform,
        vcpus, and memory, those values must be preserved even if the
        assigned VirtualMachineType defines different defaults.
        """
        vm = VirtualMachine(
            name='vm-type-explicit',
            cluster=self.cluster_with_site,
            virtual_machine_type=self.vm_types[0],
            platform=self.platforms[1],
            vcpus=Decimal('4.00'),
            memory=8192,
        )
        vm.full_clean()
        vm.save()
        vm.refresh_from_db()

        self.assertEqual(vm.platform, self.platforms[1])
        self.assertEqual(vm.vcpus, Decimal('4.00'))
        self.assertEqual(vm.memory, 8192)

    def test_vm_type_added_to_existing_vm_does_not_backfill_defaults(self):
        """
        Assigning a VirtualMachineType to an already-saved VirtualMachine
        (i.e. an update, not a creation) must not retroactively populate
        the VM's fields with the type's defaults, since apply_type_defaults()
        only runs on initial creation.
        """
        vm = VirtualMachine(
            name='vm-type-added-later',
            cluster=self.cluster_with_site,
        )
        vm.full_clean()
        vm.save()

        vm.virtual_machine_type = self.vm_types[0]
        vm.full_clean()
        vm.save()
        vm.refresh_from_db()

        self.assertEqual(vm.virtual_machine_type, self.vm_types[0])
        self.assertIsNone(vm.platform)
        self.assertIsNone(vm.vcpus)
        self.assertIsNone(vm.memory)

    def test_vm_type_change_does_not_overwrite_existing_values(self):
        """
        Changing the VirtualMachineType on an existing VirtualMachine must
        not overwrite field values that were previously set — either
        explicitly or via earlier type defaults.
        """
        vm = VirtualMachine(
            name='vm-type-change',
            cluster=self.cluster_with_site,
            virtual_machine_type=self.vm_types[0],
        )
        vm.full_clean()
        vm.save()
        vm.refresh_from_db()

        self.assertEqual(vm.platform, self.platforms[0])
        self.assertEqual(vm.vcpus, Decimal('2.00'))
        self.assertEqual(vm.memory, 4096)

        vm.platform = self.platforms[1]
        vm.vcpus = Decimal('6.00')
        vm.memory = 12288
        vm.virtual_machine_type = self.vm_types[1]
        vm.full_clean()
        vm.save()
        vm.refresh_from_db()

        self.assertEqual(vm.platform, self.platforms[1])
        self.assertEqual(vm.vcpus, Decimal('6.00'))
        self.assertEqual(vm.memory, 12288)
        self.assertEqual(vm.virtual_machine_type, self.vm_types[1])

    def test_vm_type_partial_defaults(self):
        """
        A VirtualMachineType with only some defaults set should only populate
        those fields on a new VM, leaving the rest as None.
        """
        partial_type = VirtualMachineType.objects.create(
            name='Partial Defaults',
            slug='partial-defaults',
            default_vcpus=Decimal('4.00'),
            # default_platform and default_memory intentionally left None
        )

        vm = VirtualMachine(
            name='vm-partial-defaults',
            cluster=self.cluster_with_site,
            virtual_machine_type=partial_type,
        )
        vm.full_clean()
        vm.save()
        vm.refresh_from_db()

        self.assertIsNone(vm.platform)
        self.assertEqual(vm.vcpus, Decimal('4.00'))
        self.assertIsNone(vm.memory)

    def test_vm_type_no_defaults(self):
        """
        A VirtualMachineType with all default fields as None should not
        alter any VM fields on creation.
        """
        empty_type = VirtualMachineType.objects.create(
            name='Empty Type',
            slug='empty-type',
        )

        vm = VirtualMachine(
            name='vm-empty-type',
            cluster=self.cluster_with_site,
            virtual_machine_type=empty_type,
        )
        vm.full_clean()
        vm.save()
        vm.refresh_from_db()

        self.assertEqual(vm.virtual_machine_type, empty_type)
        self.assertIsNone(vm.platform)
        self.assertIsNone(vm.vcpus)
        self.assertIsNone(vm.memory)

    def test_vm_created_without_type(self):
        """
        A VM created without a VirtualMachineType should not raise any errors
        in apply_type_defaults() and should leave all fields as None.
        """
        vm = VirtualMachine(
            name='vm-no-type',
            cluster=self.cluster_with_site,
        )
        vm.full_clean()
        vm.save()
        vm.refresh_from_db()

        self.assertIsNone(vm.virtual_machine_type)
        self.assertIsNone(vm.platform)
        self.assertIsNone(vm.vcpus)
        self.assertIsNone(vm.memory)

    def test_vm_type_is_included_in_clone_fields(self):
        """
        Verify that virtual_machine_type is part of clone_fields so it
        carries over when cloning a VM.
        """
        self.assertIn('virtual_machine_type', VirtualMachine.clone_fields)

    #
    # Device assignment tests
    #

    def test_vm_assignment_valid_combinations(self):
        """
        Test valid assignment combinations for VirtualMachine.
        """
        # Valid: Site only
        VirtualMachine(name='vm-site-only', site=self.sites[0]).full_clean()

        # Valid: Cluster only (cluster has a site scope)
        VirtualMachine(name='vm-cluster-only', cluster=self.cluster_with_site).full_clean()

        # Valid: Cluster only (cluster has no site scope)
        VirtualMachine(name='vm-cluster-no-site', cluster=self.cluster_no_site).full_clean()

        # Valid: Device only (standalone device, no cluster)
        VirtualMachine(name='vm-device-standalone', device=self.standalone_device).full_clean()

        # Valid: Site + Cluster (matching)
        VirtualMachine(name='vm-site-cluster', site=self.sites[0], cluster=self.cluster_with_site).full_clean()

        # Valid: Site + Cluster (cluster has no site scope)
        VirtualMachine(name='vm-site-cluster-no-scope', site=self.sites[0], cluster=self.cluster_no_site).full_clean()

        # Valid: Cluster + Device (device belongs to the cluster)
        VirtualMachine(
            name='vm-cluster-device', cluster=self.cluster_with_site, device=self.device_in_cluster
        ).full_clean()

        # Valid: Site + Cluster + Device (all matching)
        VirtualMachine(
            name='vm-all-three',
            site=self.sites[0],
            cluster=self.cluster_with_site,
            device=self.device_in_cluster,
        ).full_clean()

    def test_vm_assignment_invalid_no_assignment(self):
        """
        Test that a VirtualMachine without any assignment fails validation.
        """
        vm = VirtualMachine(name='vm-no-assignment')
        with self.assertRaises(ValidationError) as context:
            vm.full_clean()
        self.assertIn('__all__', context.exception.message_dict)

    def test_vm_assignment_invalid_site_cluster_mismatch(self):
        """
        Test that a VirtualMachine with a mismatched site and cluster fails validation.
        """
        # VM with Site 2 but Cluster scoped to Site 1 should fail
        vm = VirtualMachine(name='vm-mismatch', site=self.sites[1], cluster=self.cluster_with_site)
        with self.assertRaises(ValidationError) as context:
            vm.full_clean()
        self.assertIn('cluster', context.exception.message_dict)

    def test_vm_assignment_invalid_device_in_cluster_without_cluster(self):
        """
        Test that assigning a VM to a device that belongs to a cluster
        without specifying the cluster fails validation.
        """
        # VM assigned to a device without specifying the cluster should fail
        vm = VirtualMachine(name='vm-device-no-cluster', device=self.device_in_cluster)
        with self.assertRaises(ValidationError) as context:
            vm.full_clean()
        self.assertIn('cluster', context.exception.message_dict)

    def test_vm_assignment_invalid_device_cluster_mismatch(self):
        """
        Test that a VirtualMachine with a device and cluster that don't match fails validation.
        """
        # VM with a device in cluster_with_site but assigned to cluster_with_site2 should fail
        vm = VirtualMachine(
            name='vm-device-wrong-cluster',
            device=self.device_in_cluster,
            cluster=self.cluster_with_site2,
        )
        with self.assertRaises(ValidationError) as context:
            vm.full_clean()
        self.assertIn('device', context.exception.message_dict)

    def test_vm_standalone_device_assignment(self):
        """
        Test that a VirtualMachine can be assigned directly to a standalone device
        (device not in any cluster).
        """
        # VM assigned to a standalone device only should pass
        vm = VirtualMachine(name='vm-standalone', device=self.standalone_device)
        vm.full_clean()
        vm.save()

        # Verify the site was automatically set from the device
        self.assertEqual(vm.site, self.sites[1])
        self.assertIsNone(vm.cluster)

    def test_vm_standalone_device_with_site(self):
        """
        Test that a VirtualMachine can be assigned to a standalone device
        with an explicit matching site.
        """
        # VM assigned to a standalone device with an explicit site should pass
        vm = VirtualMachine(name='vm-standalone-site', site=self.sites[1], device=self.standalone_device)
        vm.full_clean()
        vm.save()

        self.assertEqual(vm.site, self.sites[1])
        self.assertEqual(vm.device, self.standalone_device)
        self.assertIsNone(vm.cluster)

    def test_vm_duplicate_name_per_device(self):
        """
        Test that VirtualMachine names must be unique per standalone device (when no cluster).
        """
        vm1 = VirtualMachine(name='vm-dup', device=self.standalone_device)
        vm1.full_clean()
        vm1.save()

        vm2 = VirtualMachine(name='vm-dup', device=self.standalone_device)

        # Duplicate name on the same standalone device should fail
        with self.assertRaises(ValidationError):
            vm2.full_clean()

    def test_vm_site_auto_assignment_from_device(self):
        """
        Test that a VirtualMachine's site is automatically set from its assigned
        standalone device when no site is explicitly provided.
        """
        # VM with a device only (no explicit site)
        vm = VirtualMachine(name='vm-auto-site', device=self.standalone_device)
        vm.full_clean()
        vm.save()

        # Site should be automatically inherited from the device
        self.assertEqual(vm.site, self.sites[1])

    def test_vm_duplicate_name_per_device_with_tenant(self):
        """
        Test that VirtualMachine names can be duplicated across different tenants
        on the same standalone device.
        """
        # Create VM with tenant1
        vm1 = VirtualMachine(name='vm-tenant-test', device=self.standalone_device, tenant=self.tenants[0])
        vm1.full_clean()
        vm1.save()

        # The same name with tenant2 on the same device should pass
        vm2 = VirtualMachine(name='vm-tenant-test', device=self.standalone_device, tenant=self.tenants[1])
        vm2.full_clean()
        vm2.save()

        # The same name with the same tenant should fail
        vm3 = VirtualMachine(name='vm-tenant-test', device=self.standalone_device, tenant=self.tenants[0])
        with self.assertRaises(ValidationError):
            vm3.full_clean()

    def test_vm_device_name_case_sensitivity(self):
        """
        Test that VirtualMachine name uniqueness per device is case-insensitive.
        """
        vm1 = VirtualMachine(name='test vm', device=self.standalone_device)
        vm1.full_clean()
        vm1.save()

        # The same name with a different case should fail
        vm2 = VirtualMachine(name='TEST VM', device=self.standalone_device)
        with self.assertRaises(ValidationError):
            vm2.full_clean()

    def test_vm_cluster_device_with_site(self):
        """
        Test that a VirtualMachine can be pinned to a device within a cluster
        with an explicit matching site.
        """
        # VM with site + cluster + device (all matching)
        vm = VirtualMachine(
            name='vm-cluster-device-site',
            site=self.sites[0],
            cluster=self.cluster_with_site,
            device=self.device_in_cluster,
        )
        vm.full_clean()
        vm.save()

        self.assertEqual(vm.site, self.sites[0])
        self.assertEqual(vm.cluster, self.cluster_with_site)
        self.assertEqual(vm.device, self.device_in_cluster)

    def test_vm_move_between_devices_in_cluster(self):
        """
        Test that a VirtualMachine can be moved between devices within the same cluster.
        """
        # Create a VM pinned to device_in_cluster
        vm = VirtualMachine(name='vm-movable', cluster=self.cluster_with_site, device=self.device_in_cluster)
        vm.full_clean()
        vm.save()

        # Move VM to device_in_cluster2
        vm.device = self.device_in_cluster2
        vm.full_clean()
        vm.save()

        self.assertEqual(vm.device, self.device_in_cluster2)
        self.assertEqual(vm.cluster, self.cluster_with_site)

    def test_vm_unpin_from_device(self):
        """
        Test that a VirtualMachine can be unpinned from a device while remaining
        in the cluster.
        """
        # Create a VM pinned to a device
        vm = VirtualMachine(name='vm-unpinnable', cluster=self.cluster_with_site, device=self.device_in_cluster)
        vm.full_clean()
        vm.save()

        # Unpin VM from the device (keep in cluster)
        vm.device = None
        vm.full_clean()
        vm.save()

        self.assertIsNone(vm.device)
        self.assertEqual(vm.cluster, self.cluster_with_site)
