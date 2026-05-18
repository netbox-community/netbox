from django.urls import reverse
from model_bakery import baker

from circuits.choices import *
from circuits.models import *
from dcim.choices import InterfaceTypeChoices
from dcim.models import Interface
from utilities.testing import APITestCase, APIViewTestCases


class AppTestCase(APITestCase):

    def test_root(self):
        url = reverse('circuits-api:api-root')
        response = self.client.get('{}?format=api'.format(url), **self.header)

        self.assertEqual(response.status_code, 200)


class ProviderTestCase(APIViewTestCases.APIViewTestCase):
    model = Provider
    brief_fields = ['circuit_count', 'description', 'display', 'id', 'name', 'slug', 'url']
    bulk_update_data = {
        'comments': 'New comments',
    }

    @classmethod
    def setUpTestData(cls):

        rir = baker.make('ipam.RIR', is_private=True)
        asns = [baker.make('ipam.ASN', asn=65000 + i, rir=rir) for i in range(8)]

        baker.make('circuits.Provider', _quantity=3)

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


class CircuitTypeTestCase(APIViewTestCases.APIViewTestCase):
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
        baker.make('circuits.CircuitType', _quantity=3)


class CircuitTestCase(APIViewTestCases.APIViewTestCase):
    model = Circuit
    brief_fields = ['cid', 'description', 'display', 'id', 'provider', 'url']
    bulk_update_data = {
        'status': 'planned',
    }
    user_permissions = ('circuits.view_provider', 'circuits.view_circuittype')

    @classmethod
    def setUpTestData(cls):

        providers = baker.make('circuits.Provider', _quantity=2)

        provider_accounts = [
            baker.make('circuits.ProviderAccount', provider=providers[0]),
            baker.make('circuits.ProviderAccount', provider=providers[1]),
        ]

        circuit_types = baker.make('circuits.CircuitType', _quantity=2)

        baker.make(
            'circuits.Circuit',
            provider=providers[0],
            provider_account=provider_accounts[0],
            type=circuit_types[0],
            _quantity=3,
        )

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


class CircuitTerminationTestCase(APIViewTestCases.APIViewTestCase):
    model = CircuitTermination
    brief_fields = ['_occupied', 'cable', 'circuit', 'description', 'display', 'id', 'term_side', 'url']
    user_permissions = ('circuits.view_circuit', )

    @classmethod
    def setUpTestData(cls):
        SIDE_A = CircuitTerminationSideChoices.SIDE_A
        SIDE_Z = CircuitTerminationSideChoices.SIDE_Z

        provider = baker.make('circuits.Provider')
        circuit_type = baker.make('circuits.CircuitType')

        sites = baker.make('dcim.Site', _quantity=2)

        provider_networks = baker.make('circuits.ProviderNetwork', provider=provider, _quantity=2)

        circuits = baker.make('circuits.Circuit', provider=provider, type=circuit_type, _quantity=3)

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


class CircuitGroupTestCase(APIViewTestCases.APIViewTestCase):
    model = CircuitGroup
    brief_fields = ['display', 'id', 'name', 'url']
    bulk_update_data = {
        'description': 'New description',
    }

    @classmethod
    def setUpTestData(cls):
        baker.make('circuits.CircuitGroup', _quantity=3)

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


class ProviderAccountTestCase(APIViewTestCases.APIViewTestCase):
    model = ProviderAccount
    brief_fields = ['account', 'description', 'display', 'id', 'name', 'url']
    user_permissions = ('circuits.view_provider',)

    @classmethod
    def setUpTestData(cls):
        providers = baker.make('circuits.Provider', _quantity=2)

        baker.make('circuits.ProviderAccount', provider=providers[0], _quantity=3)

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


class CircuitGroupAssignmentTestCase(APIViewTestCases.APIViewTestCase):
    model = CircuitGroupAssignment
    brief_fields = ['display', 'group', 'id', 'member', 'member_id', 'member_type', 'priority', 'url']
    bulk_update_data = {
        'priority': CircuitPriorityChoices.PRIORITY_INACTIVE,
    }
    user_permissions = ('circuits.view_circuit', 'circuits.view_circuitgroup')

    @classmethod
    def setUpTestData(cls):

        circuit_groups = baker.make('circuits.CircuitGroup', _quantity=6)

        provider = baker.make('circuits.Provider')
        circuittype = baker.make('circuits.CircuitType')

        circuits = baker.make('circuits.Circuit', provider=provider, type=circuittype, _quantity=6)

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


class ProviderNetworkTestCase(APIViewTestCases.APIViewTestCase):
    model = ProviderNetwork
    brief_fields = ['description', 'display', 'id', 'name', 'url']
    user_permissions = ('circuits.view_provider', )

    @classmethod
    def setUpTestData(cls):
        providers = baker.make('circuits.Provider', _quantity=2)

        baker.make('circuits.ProviderNetwork', provider=providers[0], _quantity=3)

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


class VirtualCircuitTypeTestCase(APIViewTestCases.APIViewTestCase):
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
        baker.make('circuits.VirtualCircuitType', _quantity=3)


class VirtualCircuitTestCase(APIViewTestCases.APIViewTestCase):
    model = VirtualCircuit
    brief_fields = ['cid', 'description', 'display', 'id', 'provider_network', 'url']
    bulk_update_data = {
        'status': 'planned',
    }

    @classmethod
    def setUpTestData(cls):
        provider = baker.make('circuits.Provider')
        provider_network = baker.make('circuits.ProviderNetwork', provider=provider)
        provider_account = baker.make('circuits.ProviderAccount', provider=provider)
        virtual_circuit_type = baker.make('circuits.VirtualCircuitType')

        baker.make(
            'circuits.VirtualCircuit',
            provider_network=provider_network,
            provider_account=provider_account,
            type=virtual_circuit_type,
            _quantity=3,
        )

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


class VirtualCircuitTerminationTestCase(APIViewTestCases.APIViewTestCase):
    model = VirtualCircuitTermination
    brief_fields = ['description', 'display', 'id', 'interface', 'role', 'url', 'virtual_circuit']
    bulk_update_data = {
        'description': 'New description',
    }

    @classmethod
    def setUpTestData(cls):
        site = baker.make('dcim.Site')
        device_type = baker.make('dcim.DeviceType')
        device_role = baker.make('dcim.DeviceRole')

        devices = [
            baker.make('dcim.Device', site=site, device_type=device_type, role=device_role, name=name)
            for name in ('hub', 'spoke1', 'spoke2', 'spoke3')
        ]

        physical_interfaces = []
        for device in devices:
            physical_interfaces.append(
                Interface.objects.create(device=device, name='eth0', type=InterfaceTypeChoices.TYPE_1GE_FIXED)
            )

        virtual_interfaces = []
        # Point-to-point VCs
        for i, (device, parent) in enumerate(zip(devices, physical_interfaces)):
            count = 3 if i == 0 else 1
            for j in range(count):
                virtual_interfaces.append(
                    Interface.objects.create(
                        device=device,
                        name=f'eth0.{j + 1}',
                        parent=parent,
                        type=InterfaceTypeChoices.TYPE_VIRTUAL,
                    )
                )

        # Hub and spoke VCs
        for device in devices:
            virtual_interfaces.append(
                Interface.objects.create(
                    device=device,
                    name='eth0.9',
                    parent=physical_interfaces[0],
                    type=InterfaceTypeChoices.TYPE_VIRTUAL,
                )
            )

        provider = baker.make('circuits.Provider')
        provider_network = baker.make('circuits.ProviderNetwork', provider=provider)
        provider_account = baker.make('circuits.ProviderAccount', provider=provider)
        virtual_circuit_type = baker.make('circuits.VirtualCircuitType')

        virtual_circuits = baker.make(
            'circuits.VirtualCircuit',
            provider_network=provider_network,
            provider_account=provider_account,
            type=virtual_circuit_type,
            _quantity=4,
        )

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
