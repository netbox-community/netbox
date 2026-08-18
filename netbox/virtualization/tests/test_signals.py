from django.contrib.contenttypes.models import ContentType
from django.test import TestCase, override_settings

from dcim.models import Site
from utilities.testing import PinnedConnectionRouter
from virtualization import signals
from virtualization.models import Cluster, ClusterType, VirtualDisk, VirtualMachine


class UpdateVirtualMachineDiskSignalTestCase(TestCase):
    """
    Verify virtualization.signals.update_virtualmachine_disk keeps VirtualMachine.disk in sync
    with the aggregate size of its VirtualDisks.
    """

    @classmethod
    def setUpTestData(cls):
        cluster_type = ClusterType.objects.create(name='Cluster Type', slug='cluster-type')
        cls.cluster = Cluster.objects.create(name='Cluster', type=cluster_type)

    def test_disk_size_is_aggregated_on_save(self):
        vm = VirtualMachine.objects.create(name='VM 1', cluster=self.cluster)
        VirtualDisk.objects.create(virtual_machine=vm, name='disk0', size=50)
        VirtualDisk.objects.create(virtual_machine=vm, name='disk1', size=75)

        vm.refresh_from_db()
        self.assertEqual(vm.disk, 125)

    def test_disk_size_is_recalculated_on_delete(self):
        vm = VirtualMachine.objects.create(name='VM 1', cluster=self.cluster)
        disk = VirtualDisk.objects.create(virtual_machine=vm, name='disk0', size=50)
        VirtualDisk.objects.create(virtual_machine=vm, name='disk1', size=75)
        vm.refresh_from_db()
        self.assertEqual(vm.disk, 125)

        disk.delete()
        vm.refresh_from_db()
        self.assertEqual(vm.disk, 75)

    def test_disk_size_is_none_when_all_disks_removed(self):
        vm = VirtualMachine.objects.create(name='VM 1', cluster=self.cluster)
        disk = VirtualDisk.objects.create(virtual_machine=vm, name='disk0', size=50)

        disk.delete()
        vm.refresh_from_db()
        self.assertIsNone(vm.disk)


class UpdateVirtualMachineSiteSignalTestCase(TestCase):
    """
    Verify virtualization.signals.update_virtualmachine_site propagates a Cluster's cached
    site to all of its VirtualMachines on save.
    """

    @classmethod
    def setUpTestData(cls):
        cls.site_a = Site.objects.create(name='Site A', slug='site-a')
        cls.site_b = Site.objects.create(name='Site B', slug='site-b')
        cls.cluster_type = ClusterType.objects.create(name='Cluster Type', slug='cluster-type')

    def test_cluster_site_change_propagates_to_vms(self):
        cluster = Cluster.objects.create(name='Cluster', type=self.cluster_type, scope=self.site_a)
        vm1 = VirtualMachine.objects.create(name='VM 1', cluster=cluster)
        vm2 = VirtualMachine.objects.create(name='VM 2', cluster=cluster)
        self.assertEqual(vm1.site, self.site_a)
        self.assertEqual(vm2.site, self.site_a)

        # Re-scope the cluster to site B; both VMs should follow.
        cluster.scope_type = ContentType.objects.get_for_model(Site)
        cluster.scope_id = self.site_b.pk
        cluster.save()

        vm1.refresh_from_db()
        vm2.refresh_from_db()
        self.assertEqual(vm1.site, self.site_b)
        self.assertEqual(vm2.site, self.site_b)

    def test_cluster_without_site_does_not_overwrite_vm_site(self):
        cluster = Cluster.objects.create(name='Cluster', type=self.cluster_type)
        vm = VirtualMachine.objects.create(name='VM 1', cluster=cluster, site=self.site_a)
        self.assertEqual(vm.site, self.site_a)

        cluster.description = 'updated'
        cluster.save()

        vm.refresh_from_db()
        self.assertEqual(vm.site, self.site_a)


class VirtualizationSignalConnectionTestCase(TestCase):
    """
    Verify the propagation handlers issue every query against the connection the saved
    object was written to, rather than letting DATABASE_ROUTERS select one. On an
    installation with routers configured (e.g. netbox_branching), a routed query reads from
    or writes to a different database than the one being saved.
    """

    @classmethod
    def setUpTestData(cls):
        cls.site_a = Site.objects.create(name='Site A', slug='site-a')
        cls.site_b = Site.objects.create(name='Site B', slug='site-b')
        cls.cluster_type = ClusterType.objects.create(name='Cluster Type', slug='cluster-type')

    def test_cluster_save_pins_vm_update_to_saving_connection(self):
        cluster = Cluster.objects.create(name='Cluster', type=self.cluster_type, scope=self.site_a)
        vm = VirtualMachine.objects.create(name='VM 1', cluster=cluster)

        # Site is deliberately absent from the router: Cluster.save() resolves its generic
        # scope through CachedScopeMixin.cache_related_objects(), which is a routed read of
        # its own and not something this handler controls.
        cluster = Cluster.objects.get(pk=cluster.pk)
        cluster.scope_id = self.site_b.pk
        with override_settings(DATABASE_ROUTERS=[PinnedConnectionRouter(VirtualMachine)]):
            cluster.save()

        vm.refresh_from_db()
        self.assertEqual(vm.site, self.site_b)

    def test_virtualdisk_save_pins_vm_update_to_saving_connection(self):
        cluster = Cluster.objects.create(name='Cluster', type=self.cluster_type)
        vm = VirtualMachine.objects.create(name='VM 1', cluster=cluster)
        disk = VirtualDisk.objects.create(virtual_machine=vm, name='disk0', size=50)

        # Re-fetch so the virtual_machine relation is uncached; resolving it to reach the VM
        # or its disks is itself a routed read.
        disk = VirtualDisk.objects.get(pk=disk.pk)
        disk.size = 80
        with override_settings(DATABASE_ROUTERS=[PinnedConnectionRouter(VirtualMachine)]):
            disk.save()

        vm.refresh_from_db()
        self.assertEqual(vm.disk, 80)

    def test_virtualdisk_handler_pins_disk_aggregate_to_given_connection(self):
        # VirtualDisk cannot be listed in the router above, as Django routes the save of the
        # disk itself; calling the handler directly leaves the aggregate over the sibling
        # disks as the only VirtualDisk query in scope.
        cluster = Cluster.objects.create(name='Cluster', type=self.cluster_type)
        vm = VirtualMachine.objects.create(name='VM 1', cluster=cluster)
        disk = VirtualDisk.objects.create(virtual_machine=vm, name='disk0', size=50)
        VirtualDisk.objects.create(virtual_machine=vm, name='disk1', size=75)

        disk = VirtualDisk.objects.get(pk=disk.pk)
        router = PinnedConnectionRouter(VirtualDisk, VirtualMachine)
        with override_settings(DATABASE_ROUTERS=[router]):
            signals.update_virtualmachine_disk(instance=disk, using='default')

        vm.refresh_from_db()
        self.assertEqual(vm.disk, 125)
