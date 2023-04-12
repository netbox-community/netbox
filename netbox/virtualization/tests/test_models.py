from django.core.exceptions import ValidationError
from django.test import TestCase

from dcim.models import Site
from virtualization.models import *
from tenancy.models import Tenant


class VirtualMachineTestCase(TestCase):

    @classmethod
    def setUpTestData(cls):
        cluster_type = ClusterType.objects.create(name='Cluster Type 1', slug='cluster-type-1')
        Cluster.objects.create(name='Cluster 1', type=cluster_type)

    def test_vm_duplicate_name_per_cluster(self):
        vm1 = VirtualMachine(
            cluster=Cluster.objects.first(),
            name='Test VM 1'
        )
        vm1.save()

        vm2 = VirtualMachine(
            cluster=vm1.cluster,
            name=vm1.name
        )

        # Two VMs assigned to the same Cluster and no Tenant should fail validation
        with self.assertRaises(ValidationError):
            vm2.full_clean()

        tenant = Tenant.objects.create(name='Test Tenant 1', slug='test-tenant-1')
        vm1.tenant = tenant
        vm1.save()
        vm2.tenant = tenant

        # Two VMs assigned to the same Cluster and the same Tenant should fail validation
        with self.assertRaises(ValidationError):
            vm2.full_clean()

        vm2.tenant = None

        # Two VMs assigned to the same Cluster and different Tenants should pass validation
        vm2.full_clean()
        vm2.save()

    def test_vm_mismatched_site_cluster(self):
        cluster_type = ClusterType.objects.first()

        sites = (
            Site(name='Site 1', slug='site-1'),
            Site(name='Site 2', slug='site-2'),
        )
        Site.objects.bulk_create(sites)

        clusters = (
            Cluster(name='Cluster 1', type=cluster_type, site=sites[0]),
            Cluster(name='Cluster 2', type=cluster_type, site=sites[1]),
            Cluster(name='Cluster 3', type=cluster_type, site=None),
        )
        Cluster.objects.bulk_create(clusters)

        # VM with site only should pass
        VirtualMachine(name='vm1', site=sites[0]).full_clean()

        # VM with non-site cluster only should pass
        VirtualMachine(name='vm1', cluster=clusters[2]).full_clean()

        # VM with mismatched site & cluster should fail
        with self.assertRaises(ValidationError):
            VirtualMachine(name='vm1', site=sites[0], cluster=clusters[1]).full_clean()

        # VM with cluster site but no direct site should have its site set automatically
        vm = VirtualMachine(name='vm1', site=None, cluster=clusters[0])
        vm.save()
        self.assertEqual(vm.site, sites[0])

    def test_vm_name_case_sensitivity(self):
        vm1 = VirtualMachine(
            cluster=Cluster.objects.first(),
            name='virtual machine 1'
        )
        vm1.save()

        vm2 = VirtualMachine(
            cluster=vm1.cluster,
            name='VIRTUAL MACHINE 1'
        )

        # Uniqueness validation for name should ignore case
        with self.assertRaises(ValidationError):
            vm2.full_clean()
