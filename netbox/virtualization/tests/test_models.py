from django.core.exceptions import ValidationError
from django.test import TestCase

from virtualization.models import *
from tenancy.models import Tenant


class VirtualMachineTestCase(TestCase):

    def setUp(self):

        cluster_type = ClusterType.objects.create(name='Test Cluster Type 1', slug='Test Cluster Type 1')
        self.cluster = Cluster.objects.create(name='Test Cluster 1', type=cluster_type)

    def test_vm_duplicate_name_per_cluster(self):

        vm1 = VirtualMachine(
            cluster=self.cluster,
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
