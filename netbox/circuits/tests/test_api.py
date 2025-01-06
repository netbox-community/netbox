from django.urls import reverse

from circuits.choices import *
from circuits.models import *
from dcim.choices import InterfaceTypeChoices
from dcim.models import Device, DeviceRole, DeviceType, Interface, Manufacturer, Site
from ipam.models import ASN, RIR
from utilities.testing import APITestCase, APIViewTestCases


class AppTest(APITestCase):

    def test_root(self):
        url = reverse('circuits-api:api-root')
        response = self.client.get('{}?format=api'.format(url), **self.header)

        self.assertEqual(response.status_code, 200)


class ProviderTest(APIViewTestCases.APIViewTestCase):
    model = Provider
    brief_fields = ['circuit_count', 'description', 'display', 'id', 'name', 'slug', 'url']
    bulk_update_data = {
        'comments': 'New comments',
    }

    @classmethod
    def setUpTestData(cls):

        rir = RIR.objects.create(name='RFC 6996', is_private=True)
        asns = [
            ASN(asn=65000 + i, rir=rir) for i in range(8)
        ]
        ASN.objects.bulk_create(asns)

        providers = (
            Provider(name='Provider 1', slug='provider-1'),
            Provider(name='Provider 2', slug='provider-2'),
            Provider(name='Provider 3', slug='provider-3'),
        )
        Provider.objects.bulk_create(providers)

        cls.create_data = [
            {
                'name': 'Provider 4',
                'slug': 'provider-4',
                'asns': [asns[0].pk, asns[1].pk],
            },
            {
                'name': 'Provider 5',
                'slug': 'provider-5',
                'asns': [asns[2].pk, asns[3].pk],
            },
            {
                'name': 'Provider 6',
                'slug': 'provider-6',
                'asns': [asns[4].pk, asns[5].pk],
            },
        ]


class CircuitTypeTest(APIViewTestCases.APIViewTestCase):
    model = CircuitType
    brief_fields = ['circuit_count', 'description', 'display', 'id', 'name', 'slug', 'url']
    create_data = (
        {
            'name': 'Circuit Type 4',
            'slug': 'circuit-type-4',
        },
        {
            'name': 'Circuit Type 5',
            'slug': 'circuit-type-5',
        },
        {
            'name': 'Circuit Type 6',
            'slug': 'circuit-type-6',
        },
    )
    bulk_update_data = {
        'description': 'New description',
    }

    @classmethod
    def setUpTestData(cls):

        circuit_types = (
            CircuitType(name='Circuit Type 1', slug='circuit-type-1'),
            CircuitType(name='Circuit Type 2', slug='circuit-type-2'),
            CircuitType(name='Circuit Type 3', slug='circuit-type-3'),
        )
        CircuitType.objects.bulk_create(circuit_types)


class CircuitTest(APIViewTestCases.APIViewTestCase):
    model = Circuit
    brief_fields = ['cid', 'description', 'display', 'id', 'provider', 'url']
    bulk_update_data = {
        'status': 'planned',
    }
    user_permissions = ('circuits.view_provider', 'circuits.view_circuittype')

    @classmethod
    def setUpTestData(cls):

        providers = (
            Provider(name='Provider 1', slug='provider-1'),
            Provider(name='Provider 2', slug='provider-2'),
        )
        Provider.objects.bulk_create(providers)

        provider_accounts = (
            ProviderAccount(name='Provider Account 1', provider=providers[0], account='1234'),
            ProviderAccount(name='Provider Account 2', provider=providers[1], account='2345'),
        )
        ProviderAccount.objects.bulk_create(provider_accounts)

        circuit_types = (
            CircuitType(name='Circuit Type 1', slug='circuit-type-1'),
            CircuitType(name='Circuit Type 2', slug='circuit-type-2'),
        )
        CircuitType.objects.bulk_create(circuit_types)

        circuits = (
            Circuit(
                cid='Circuit 1', provider=providers[0], provider_account=provider_accounts[0], type=circuit_types[0]
            ),
            Circuit(
                cid='Circuit 2', provider=providers[0], provider_account=provider_accounts[0], type=circuit_types[0]
            ),
            Circuit(
                cid='Circuit 3', provider=providers[0], provider_account=provider_accounts[0], type=circuit_types[0]
            ),
        )
        Circuit.objects.bulk_create(circuits)

        cls.create_data = [
            {
                'cid': 'Circuit 4',
                'provider': providers[1].pk,
                'provider_account': provider_accounts[1].pk,
                'type': circuit_types[1].pk,
            },
            {
                'cid': 'Circuit 5',
                'provider': providers[1].pk,
                'provider_account': provider_accounts[1].pk,
                'type': circuit_types[1].pk,
            },
            {
                'cid': 'Circuit 6',
                'provider': providers[1].pk,
                # Omit provider account to test uniqueness constraint
                'type': circuit_types[1].pk,
            },
        ]


class CircuitTerminationTest(APIViewTestCases.APIViewTestCase):
    model = CircuitTermination
    brief_fields = ['_occupied', 'cable', 'circuit', 'description', 'display', 'id', 'term_side', 'url']
    user_permissions = ('circuits.view_circuit', )

    @classmethod
    def setUpTestData(cls):
        SIDE_A = CircuitTerminationSideChoices.SIDE_A
        SIDE_Z = CircuitTerminationSideChoices.SIDE_Z

        provider = Provider.objects.create(name='Provider 1', slug='provider-1')
        circuit_type = CircuitType.objects.create(name='Circuit Type 1', slug='circuit-type-1')

        sites = (
            Site(name='Site 1', slug='site-1'),
            Site(name='Site 2', slug='site-2'),
        )
        Site.objects.bulk_create(sites)

        provider_networks = (
            ProviderNetwork(provider=provider, name='Provider Network 1'),
            ProviderNetwork(provider=provider, name='Provider Network 2'),
        )
        ProviderNetwork.objects.bulk_create(provider_networks)

        circuits = (
            Circuit(cid='Circuit 1', provider=provider, type=circuit_type),
            Circuit(cid='Circuit 2', provider=provider, type=circuit_type),
            Circuit(cid='Circuit 3', provider=provider, type=circuit_type),
        )
        Circuit.objects.bulk_create(circuits)

        circuit_terminations = (
            CircuitTermination(circuit=circuits[0], term_side=SIDE_A, termination=sites[0]),
            CircuitTermination(circuit=circuits[0], term_side=SIDE_Z, termination=provider_networks[0]),
            CircuitTermination(circuit=circuits[1], term_side=SIDE_A, termination=sites[1]),
            CircuitTermination(circuit=circuits[1], term_side=SIDE_Z, termination=provider_networks[1]),
        )
        CircuitTermination.objects.bulk_create(circuit_terminations)

        cls.create_data = [
            {
                'circuit': circuits[2].pk,
                'term_side': SIDE_A,
                'termination_type': 'dcim.site',
                'termination_id': sites[0].pk,
                'port_speed': 200000,
            },
            {
                'circuit': circuits[2].pk,
                'term_side': SIDE_Z,
                'termination_type': 'circuits.providernetwork',
                'termination_id': provider_networks[0].pk,
                'port_speed': 200000,
            },
        ]

        cls.bulk_update_data = {
            'port_speed': 123456
        }


class CircuitGroupTest(APIViewTestCases.APIViewTestCase):
    model = CircuitGroup
    brief_fields = ['display', 'id', 'name', 'url']
    bulk_update_data = {
        'description': 'New description',
    }

    @classmethod
    def setUpTestData(cls):
        circuit_groups = (
            CircuitGroup(name="Circuit Group 1", slug='circuit-group-1'),
            CircuitGroup(name="Circuit Group 2", slug='circuit-group-2'),
            CircuitGroup(name="Circuit Group 3", slug='circuit-group-3'),
        )
        CircuitGroup.objects.bulk_create(circuit_groups)

        cls.create_data = [
            {
                'name': 'Circuit Group 4',
                'slug': 'circuit-group-4',
            },
            {
                'name': 'Circuit Group 5',
                'slug': 'circuit-group-5',
            },
            {
                'name': 'Circuit Group 6',
                'slug': 'circuit-group-6',
            },
        ]


class ProviderAccountTest(APIViewTestCases.APIViewTestCase):
    model = ProviderAccount
    brief_fields = ['account', 'description', 'display', 'id', 'name', 'url']
    user_permissions = ('circuits.view_provider',)

    @classmethod
    def setUpTestData(cls):
        providers = (
            Provider(name='Provider 1', slug='provider-1'),
            Provider(name='Provider 2', slug='provider-2'),
        )
        Provider.objects.bulk_create(providers)

        provider_accounts = (
            ProviderAccount(name='Provider Account 1', provider=providers[0], account='1234'),
            ProviderAccount(name='Provider Account 2', provider=providers[0], account='2345'),
            ProviderAccount(name='Provider Account 3', provider=providers[0], account='3456'),
        )
        ProviderAccount.objects.bulk_create(provider_accounts)

        cls.create_data = [
            {
                'name': 'Provider Account 4',
                'provider': providers[0].pk,
                'account': '4567',
            },
            {
                'name': 'Provider Account 5',
                'provider': providers[0].pk,
                'account': '5678',
            },
            {
                # Omit name to test uniqueness constraint
                'provider': providers[0].pk,
                'account': '6789',
            },
        ]

        cls.bulk_update_data = {
            'provider': providers[1].pk,
            'description': 'New description',
        }


class CircuitGroupAssignmentTest(APIViewTestCases.APIViewTestCase):
    model = CircuitGroupAssignment
    brief_fields = ['display', 'group', 'id', 'member', 'member_id', 'member_type', 'priority', 'url']
    bulk_update_data = {
        'priority': CircuitPriorityChoices.PRIORITY_INACTIVE,
    }
    user_permissions = ('circuits.view_circuit', 'circuits.view_circuitgroup')

    @classmethod
    def setUpTestData(cls):

        circuit_groups = (
            CircuitGroup(name='Circuit Group 1', slug='circuit-group-1'),
            CircuitGroup(name='Circuit Group 2', slug='circuit-group-2'),
            CircuitGroup(name='Circuit Group 3', slug='circuit-group-3'),
            CircuitGroup(name='Circuit Group 4', slug='circuit-group-4'),
            CircuitGroup(name='Circuit Group 5', slug='circuit-group-5'),
            CircuitGroup(name='Circuit Group 6', slug='circuit-group-6'),
        )
        CircuitGroup.objects.bulk_create(circuit_groups)

        provider = Provider.objects.create(name='Provider 1', slug='provider-1')
        circuittype = CircuitType.objects.create(name='Circuit Type 1', slug='circuit-type-1')

        circuits = (
            Circuit(cid='Circuit 1', provider=provider, type=circuittype),
            Circuit(cid='Circuit 2', provider=provider, type=circuittype),
            Circuit(cid='Circuit 3', provider=provider, type=circuittype),
            Circuit(cid='Circuit 4', provider=provider, type=circuittype),
            Circuit(cid='Circuit 5', provider=provider, type=circuittype),
            Circuit(cid='Circuit 6', provider=provider, type=circuittype),
        )
        Circuit.objects.bulk_create(circuits)

        assignments = (
            CircuitGroupAssignment(
                group=circuit_groups[0],
                member=circuits[0],
                priority=CircuitPriorityChoices.PRIORITY_PRIMARY
            ),
            CircuitGroupAssignment(
                group=circuit_groups[1],
                member=circuits[1],
                priority=CircuitPriorityChoices.PRIORITY_SECONDARY
            ),
            CircuitGroupAssignment(
                group=circuit_groups[2],
                member=circuits[2],
                priority=CircuitPriorityChoices.PRIORITY_TERTIARY
            ),
        )
        CircuitGroupAssignment.objects.bulk_create(assignments)

        cls.create_data = [
            {
                'group': circuit_groups[3].pk,
                'member_type': 'circuits.circuit',
                'member_id': circuits[3].pk,
                'priority': CircuitPriorityChoices.PRIORITY_PRIMARY,
            },
            {
                'group': circuit_groups[4].pk,
                'member_type': 'circuits.circuit',
                'member_id': circuits[4].pk,
                'priority': CircuitPriorityChoices.PRIORITY_SECONDARY,
            },
            {
                'group': circuit_groups[5].pk,
                'member_type': 'circuits.circuit',
                'member_id': circuits[5].pk,
                'priority': CircuitPriorityChoices.PRIORITY_TERTIARY,
            },
        ]


class ProviderNetworkTest(APIViewTestCases.APIViewTestCase):
    model = ProviderNetwork
    brief_fields = ['description', 'display', 'id', 'name', 'url']
    user_permissions = ('circuits.view_provider', )

    @classmethod
    def setUpTestData(cls):
        providers = (
            Provider(name='Provider 1', slug='provider-1'),
            Provider(name='Provider 2', slug='provider-2'),
        )
        Provider.objects.bulk_create(providers)

        provider_networks = (
            ProviderNetwork(name='Provider Network 1', provider=providers[0]),
            ProviderNetwork(name='Provider Network 2', provider=providers[0]),
            ProviderNetwork(name='Provider Network 3', provider=providers[0]),
        )
        ProviderNetwork.objects.bulk_create(provider_networks)

        cls.create_data = [
            {
                'name': 'Provider Network 4',
                'provider': providers[0].pk,
            },
            {
                'name': 'Provider Network 5',
                'provider': providers[0].pk,
            },
            {
                'name': 'Provider Network 6',
                'provider': providers[0].pk,
            },
        ]

        cls.bulk_update_data = {
            'provider': providers[1].pk,
            'description': 'New description',
        }


class VirtualCircuitTypeTest(APIViewTestCases.APIViewTestCase):
    model = VirtualCircuitType
    brief_fields = ['description', 'display', 'id', 'name', 'slug', 'url', 'virtual_circuit_count']
    create_data = (
        {
            'name': 'Virtual Circuit Type 4',
            'slug': 'virtual-circuit-type-4',
        },
        {
            'name': 'Virtual Circuit Type 5',
            'slug': 'virtual-circuit-type-5',
        },
        {
            'name': 'Virtual Circuit Type 6',
            'slug': 'virtual-circuit-type-6',
        },
    )
    bulk_update_data = {
        'description': 'New description',
    }

    @classmethod
    def setUpTestData(cls):

        virtual_circuit_types = (
            VirtualCircuitType(name='Virtual Circuit Type 1', slug='virtual-circuit-type-1'),
            VirtualCircuitType(name='Virtual Circuit Type 2', slug='virtual-circuit-type-2'),
            VirtualCircuitType(name='Virtual Circuit Type 3', slug='virtual-circuit-type-3'),
        )
        VirtualCircuitType.objects.bulk_create(virtual_circuit_types)


class VirtualCircuitTest(APIViewTestCases.APIViewTestCase):
    model = VirtualCircuit
    brief_fields = ['cid', 'description', 'display', 'id', 'provider_network', 'url']
    bulk_update_data = {
        'status': 'planned',
    }

    @classmethod
    def setUpTestData(cls):
        provider = Provider.objects.create(name='Provider 1', slug='provider-1')
        provider_network = ProviderNetwork.objects.create(provider=provider, name='Provider Network 1')
        provider_account = ProviderAccount.objects.create(provider=provider, account='Provider Account 1')
        virtual_circuit_type = VirtualCircuitType.objects.create(
            name='Virtual Circuit Type 1',
            slug='virtual-circuit-type-1'
        )

        virtual_circuits = (
            VirtualCircuit(
                provider_network=provider_network,
                provider_account=provider_account,
                type=virtual_circuit_type,
                cid='Virtual Circuit 1'
            ),
            VirtualCircuit(
                provider_network=provider_network,
                provider_account=provider_account,
                type=virtual_circuit_type,
                cid='Virtual Circuit 2'
            ),
            VirtualCircuit(
                provider_network=provider_network,
                provider_account=provider_account,
                type=virtual_circuit_type,
                cid='Virtual Circuit 3'
            ),
        )
        VirtualCircuit.objects.bulk_create(virtual_circuits)

        cls.create_data = [
            {
                'cid': 'Virtual Circuit 4',
                'provider_network': provider_network.pk,
                'provider_account': provider_account.pk,
                'type': virtual_circuit_type.pk,
                'status': CircuitStatusChoices.STATUS_PLANNED,
            },
            {
                'cid': 'Virtual Circuit 5',
                'provider_network': provider_network.pk,
                'provider_account': provider_account.pk,
                'type': virtual_circuit_type.pk,
                'status': CircuitStatusChoices.STATUS_PLANNED,
            },
            {
                'cid': 'Virtual Circuit 6',
                'provider_network': provider_network.pk,
                'provider_account': provider_account.pk,
                'type': virtual_circuit_type.pk,
                'status': CircuitStatusChoices.STATUS_PLANNED,
            },
        ]


class VirtualCircuitTerminationTest(APIViewTestCases.APIViewTestCase):
    model = VirtualCircuitTermination
    brief_fields = ['description', 'display', 'id', 'interface', 'role', 'url', 'virtual_circuit']
    bulk_update_data = {
        'description': 'New description',
    }

    @classmethod
    def setUpTestData(cls):
        manufacturer = Manufacturer.objects.create(name='Manufacturer 1', slug='manufacturer-1')
        device_type = DeviceType.objects.create(manufacturer=manufacturer, model='Device Type 1')
        device_role = DeviceRole.objects.create(name='Device Role 1', slug='device-role-1')
        site = Site.objects.create(name='Site 1', slug='site-1')

        devices = (
            Device(site=site, name='hub', device_type=device_type, role=device_role),
            Device(site=site, name='spoke1', device_type=device_type, role=device_role),
            Device(site=site, name='spoke2', device_type=device_type, role=device_role),
            Device(site=site, name='spoke3', device_type=device_type, role=device_role),
        )
        Device.objects.bulk_create(devices)

        physical_interfaces = (
            Interface(device=devices[0], name='eth0', type=InterfaceTypeChoices.TYPE_1GE_FIXED),
            Interface(device=devices[1], name='eth0', type=InterfaceTypeChoices.TYPE_1GE_FIXED),
            Interface(device=devices[2], name='eth0', type=InterfaceTypeChoices.TYPE_1GE_FIXED),
            Interface(device=devices[3], name='eth0', type=InterfaceTypeChoices.TYPE_1GE_FIXED),
        )
        Interface.objects.bulk_create(physical_interfaces)

        virtual_interfaces = (
            # Point-to-point VCs
            Interface(
                device=devices[0],
                name='eth0.1',
                parent=physical_interfaces[0],
                type=InterfaceTypeChoices.TYPE_VIRTUAL
            ),
            Interface(
                device=devices[0],
                name='eth0.2',
                parent=physical_interfaces[0],
                type=InterfaceTypeChoices.TYPE_VIRTUAL
            ),
            Interface(
                device=devices[0],
                name='eth0.3',
                parent=physical_interfaces[0],
                type=InterfaceTypeChoices.TYPE_VIRTUAL
            ),
            Interface(
                device=devices[1],
                name='eth0.1',
                parent=physical_interfaces[1],
                type=InterfaceTypeChoices.TYPE_VIRTUAL
            ),
            Interface(
                device=devices[2],
                name='eth0.1',
                parent=physical_interfaces[2],
                type=InterfaceTypeChoices.TYPE_VIRTUAL
            ),
            Interface(
                device=devices[3],
                name='eth0.1',
                parent=physical_interfaces[3],
                type=InterfaceTypeChoices.TYPE_VIRTUAL
            ),

            # Hub and spoke VCs
            Interface(
                device=devices[0],
                name='eth0.9',
                parent=physical_interfaces[0],
                type=InterfaceTypeChoices.TYPE_VIRTUAL
            ),
            Interface(
                device=devices[1],
                name='eth0.9',
                parent=physical_interfaces[0],
                type=InterfaceTypeChoices.TYPE_VIRTUAL
            ),
            Interface(
                device=devices[2],
                name='eth0.9',
                parent=physical_interfaces[0],
                type=InterfaceTypeChoices.TYPE_VIRTUAL
            ),
            Interface(
                device=devices[3],
                name='eth0.9',
                parent=physical_interfaces[0],
                type=InterfaceTypeChoices.TYPE_VIRTUAL
            ),
        )
        Interface.objects.bulk_create(virtual_interfaces)

        provider = Provider.objects.create(name='Provider 1', slug='provider-1')
        provider_network = ProviderNetwork.objects.create(provider=provider, name='Provider Network 1')
        provider_account = ProviderAccount.objects.create(provider=provider, account='Provider Account 1')
        virtual_circuit_type = VirtualCircuitType.objects.create(
            name='Virtual Circuit Type 1',
            slug='virtual-circuit-type-1'
        )

        virtual_circuits = (
            VirtualCircuit(
                provider_network=provider_network,
                provider_account=provider_account,
                cid='Virtual Circuit 1',
                type=virtual_circuit_type
            ),
            VirtualCircuit(
                provider_network=provider_network,
                provider_account=provider_account,
                cid='Virtual Circuit 2',
                type=virtual_circuit_type
            ),
            VirtualCircuit(
                provider_network=provider_network,
                provider_account=provider_account,
                cid='Virtual Circuit 3',
                type=virtual_circuit_type
            ),
            VirtualCircuit(
                provider_network=provider_network,
                provider_account=provider_account,
                cid='Virtual Circuit 4',
                type=virtual_circuit_type
            ),
        )
        VirtualCircuit.objects.bulk_create(virtual_circuits)

        virtual_circuit_terminations = (
            VirtualCircuitTermination(
                virtual_circuit=virtual_circuits[0],
                role=VirtualCircuitTerminationRoleChoices.ROLE_PEER,
                interface=virtual_interfaces[0]
            ),
            VirtualCircuitTermination(
                virtual_circuit=virtual_circuits[0],
                role=VirtualCircuitTerminationRoleChoices.ROLE_PEER,
                interface=virtual_interfaces[3]
            ),
            VirtualCircuitTermination(
                virtual_circuit=virtual_circuits[1],
                role=VirtualCircuitTerminationRoleChoices.ROLE_PEER,
                interface=virtual_interfaces[1]
            ),
            VirtualCircuitTermination(
                virtual_circuit=virtual_circuits[1],
                role=VirtualCircuitTerminationRoleChoices.ROLE_PEER,
                interface=virtual_interfaces[4]
            ),
            VirtualCircuitTermination(
                virtual_circuit=virtual_circuits[2],
                role=VirtualCircuitTerminationRoleChoices.ROLE_PEER,
                interface=virtual_interfaces[2]
            ),
            VirtualCircuitTermination(
                virtual_circuit=virtual_circuits[2],
                role=VirtualCircuitTerminationRoleChoices.ROLE_PEER,
                interface=virtual_interfaces[5]
            ),
        )
        VirtualCircuitTermination.objects.bulk_create(virtual_circuit_terminations)

        cls.create_data = [
            {
                'virtual_circuit': virtual_circuits[3].pk,
                'role': VirtualCircuitTerminationRoleChoices.ROLE_HUB,
                'interface': virtual_interfaces[6].pk
            },
            {
                'virtual_circuit': virtual_circuits[3].pk,
                'role': VirtualCircuitTerminationRoleChoices.ROLE_SPOKE,
                'interface': virtual_interfaces[7].pk
            },
            {
                'virtual_circuit': virtual_circuits[3].pk,
                'role': VirtualCircuitTerminationRoleChoices.ROLE_SPOKE,
                'interface': virtual_interfaces[8].pk
            },
            {
                'virtual_circuit': virtual_circuits[3].pk,
                'role': VirtualCircuitTerminationRoleChoices.ROLE_SPOKE,
                'interface': virtual_interfaces[9].pk
            },
        ]
