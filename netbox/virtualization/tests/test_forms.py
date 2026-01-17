from django.test import TestCase, override_settings

from virtualization.forms import VirtualMachineForm, VirtualDiskForm
from virtualization.models import VirtualMachine, ClusterType, Cluster
from dcim.models import Site

class VirtualMachineFormTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        cluster_type = ClusterType.objects.create(name='Test Cluster Type')
        cls.cluster = Cluster.objects.create(name='Test Cluster', type=cluster_type)
        cls.site = Site.objects.create(name='Test Site')


    def test_default_labels(self):
        form = VirtualMachineForm()
        self.assertEqual(form.fields['memory'].label, 'Memory (MB)')
        self.assertEqual(form.fields['disk'].label, 'Disk (MB)')

    @override_settings(RAM_BASE_UNIT=1024, DISK_BASE_UNIT=1024)
    def test_binary_labels(self):
        form = VirtualMachineForm()
        self.assertEqual(form.fields['memory'].label, 'Memory (MiB)')
        self.assertEqual(form.fields['disk'].label, 'Disk (MiB)')

    def test_pk_init(self):
        vm = VirtualMachine(
            name='Test VM',
            cluster=self.cluster,
            site=self.site
        )
        vm.save()
        form = VirtualMachineForm(instance=vm)
        self.assertIn('primary_ip4', form.fields)
        self.assertIn('primary_ip6', form.fields)


class VirtualDiskFormTest(TestCase):

    def test_default_labels(self):
        form = VirtualDiskForm()
        self.assertEqual(form.fields['size'].label, 'Size (MB)')

    @override_settings(DISK_BASE_UNIT=1024)
    def test_binary_labels(self):
        form = VirtualDiskForm()
        self.assertEqual(form.fields['size'].label, 'Size (MiB)')
