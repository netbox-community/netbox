from dcim.models import DeviceRole, Platform, Site
from utilities.testing import StandardTestCases
from virtualization.choices import *
from virtualization.models import Cluster, ClusterGroup, ClusterType, VirtualMachine


class ClusterGroupTestCase(StandardTestCases.Views):
    model = ClusterGroup

    # Disable inapplicable tests
    test_get_object = None
    test_delete_object = None

    @classmethod
    def setUpTestData(cls):

        ClusterGroup.objects.bulk_create([
            ClusterGroup(name='Cluster Group 1', slug='cluster-group-1'),
            ClusterGroup(name='Cluster Group 2', slug='cluster-group-2'),
            ClusterGroup(name='Cluster Group 3', slug='cluster-group-3'),
        ])

        cls.form_data = {
            'name': 'Cluster Group X',
            'slug': 'cluster-group-x',
        }

        cls.csv_data = (
            "name,slug",
            "Cluster Group 4,cluster-group-4",
            "Cluster Group 5,cluster-group-5",
            "Cluster Group 6,cluster-group-6",
        )


class ClusterTypeTestCase(StandardTestCases.Views):
    model = ClusterType

    # Disable inapplicable tests
    test_get_object = None
    test_delete_object = None

    @classmethod
    def setUpTestData(cls):

        ClusterType.objects.bulk_create([
            ClusterType(name='Cluster Type 1', slug='cluster-type-1'),
            ClusterType(name='Cluster Type 2', slug='cluster-type-2'),
            ClusterType(name='Cluster Type 3', slug='cluster-type-3'),
        ])

        cls.form_data = {
            'name': 'Cluster Type X',
            'slug': 'cluster-type-x',
        }

        cls.csv_data = (
            "name,slug",
            "Cluster Type 4,cluster-type-4",
            "Cluster Type 5,cluster-type-5",
            "Cluster Type 6,cluster-type-6",
        )


class ClusterTestCase(StandardTestCases.Views):
    model = Cluster

    @classmethod
    def setUpTestData(cls):

        site = Site.objects.create(name='Site 1', slug='site-1')
        clustergroup = ClusterGroup.objects.create(name='Cluster Group 1', slug='cluster-group-1')
        clustertype = ClusterType.objects.create(name='Cluster Type 1', slug='cluster-type-1')

        Cluster.objects.bulk_create([
            Cluster(name='Cluster 1', group=clustergroup, type=clustertype),
            Cluster(name='Cluster 2', group=clustergroup, type=clustertype),
            Cluster(name='Cluster 3', group=clustergroup, type=clustertype),
        ])

        cls.form_data = {
            'name': 'Cluster X',
            'group': clustergroup.pk,
            'type': clustertype.pk,
            'tenant': None,
            'site': site.pk,
            'comments': 'Some comments',
            'tags': 'Alpha,Bravo,Charlie',
        }

        cls.csv_data = (
            "name,type",
            "Cluster 4,Cluster Type 1",
            "Cluster 5,Cluster Type 1",
            "Cluster 6,Cluster Type 1",
        )


class VirtualMachineTestCase(StandardTestCases.Views):
    model = VirtualMachine

    @classmethod
    def setUpTestData(cls):

        devicerole = DeviceRole.objects.create(name='Device Role 1', slug='device-role-1')
        platform = Platform.objects.create(name='Platform 1', slug='platform-1')
        clustertype = ClusterType.objects.create(name='Cluster Type 1', slug='cluster-type-1')
        cluster = Cluster.objects.create(name='Cluster 1', type=clustertype)

        VirtualMachine.objects.bulk_create([
            VirtualMachine(name='Virtual Machine 1', cluster=cluster),
            VirtualMachine(name='Virtual Machine 2', cluster=cluster),
            VirtualMachine(name='Virtual Machine 3', cluster=cluster),
        ])

        cls.form_data = {
            'cluster': cluster.pk,
            'tenant': None,
            'platform': None,
            'name': 'Virtual Machine X',
            'status': VirtualMachineStatusChoices.STATUS_STAGED,
            'role': devicerole.pk,
            'primary_ip4': None,
            'primary_ip6': None,
            'vcpus': 4,
            'memory': 32768,
            'disk': 4000,
            'comments': 'Some comments',
            'tags': 'Alpha,Bravo,Charlie',
            'local_context_data': None,
        }

        cls.csv_data = (
            "name,cluster",
            "Virtual Machine 4,Cluster 1",
            "Virtual Machine 5,Cluster 1",
            "Virtual Machine 6,Cluster 1",
        )
