from dcim.models import DeviceRole, Platform, Site
from utilities.testing import StandardTestCases
from virtualization.choices import *
from virtualization.models import Cluster, ClusterGroup, ClusterType, VirtualMachine


class ClusterGroupTestCase(StandardTestCases.Views):
    model = ClusterGroup

    # Disable inapplicable tests
    test_get_object = None
    test_delete_object = None
    test_bulk_edit_objects = None

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
    test_bulk_edit_objects = None

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

        Cluster.objects.bulk_create([
            Cluster(name='Cluster 1', group=clustergroups[0], type=clustertypes[0], site=sites[0]),
            Cluster(name='Cluster 2', group=clustergroups[0], type=clustertypes[0], site=sites[0]),
            Cluster(name='Cluster 3', group=clustergroups[0], type=clustertypes[0], site=sites[0]),
        ])

        cls.form_data = {
            'name': 'Cluster X',
            'group': clustergroups[1].pk,
            'type': clustertypes[1].pk,
            'tenant': None,
            'site': sites[1].pk,
            'comments': 'Some comments',
            'tags': 'Alpha,Bravo,Charlie',
        }

        cls.csv_data = (
            "name,type",
            "Cluster 4,Cluster Type 1",
            "Cluster 5,Cluster Type 1",
            "Cluster 6,Cluster Type 1",
        )

        cls.bulk_edit_data = {
            'group': clustergroups[1].pk,
            'type': clustertypes[1].pk,
            'tenant': None,
            'site': sites[1].pk,
            'comments': 'New comments',
        }


class VirtualMachineTestCase(StandardTestCases.Views):
    model = VirtualMachine

    @classmethod
    def setUpTestData(cls):

        deviceroles = (
            DeviceRole(name='Device Role 1', slug='device-role-1'),
            DeviceRole(name='Device Role 2', slug='device-role-2'),
        )
        DeviceRole.objects.bulk_create(deviceroles)

        platforms = (
            Platform(name='Platform 1', slug='platform-1'),
            Platform(name='Platform 2', slug='platform-2'),
        )
        Platform.objects.bulk_create(platforms)

        clustertype = ClusterType.objects.create(name='Cluster Type 1', slug='cluster-type-1')

        clusters = (
            Cluster(name='Cluster 1', type=clustertype),
            Cluster(name='Cluster 2', type=clustertype),
        )
        Cluster.objects.bulk_create(clusters)

        VirtualMachine.objects.bulk_create([
            VirtualMachine(name='Virtual Machine 1', cluster=clusters[0], role=deviceroles[0], platform=platforms[0]),
            VirtualMachine(name='Virtual Machine 2', cluster=clusters[0], role=deviceroles[0], platform=platforms[0]),
            VirtualMachine(name='Virtual Machine 3', cluster=clusters[0], role=deviceroles[0], platform=platforms[0]),
        ])

        cls.form_data = {
            'cluster': clusters[1].pk,
            'tenant': None,
            'platform': platforms[1].pk,
            'name': 'Virtual Machine X',
            'status': VirtualMachineStatusChoices.STATUS_STAGED,
            'role': deviceroles[1].pk,
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

        cls.bulk_edit_data = {
            'cluster': clusters[1].pk,
            'tenant': None,
            'platform': platforms[1].pk,
            'status': VirtualMachineStatusChoices.STATUS_STAGED,
            'role': deviceroles[1].pk,
            'vcpus': 8,
            'memory': 65535,
            'disk': 8000,
            'comments': 'New comments',
        }
