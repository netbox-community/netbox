import datetime

from django.contrib.contenttypes.models import ContentType
from django.urls import reverse
from model_bakery import baker

from circuits.choices import *
from circuits.models import *
from core.models import ObjectType
from dcim.choices import InterfaceTypeChoices
from dcim.models import Cable, Interface, Site
from netbox.choices import ImportFormatChoices
from users.models import ObjectPermission
from utilities.testing import ViewTestCases, create_tags, create_test_device


class ProviderTestCase(ViewTestCases.PrimaryObjectViewTestCase):
    model = Provider

    @classmethod
    def setUpTestData(cls):

        rir = baker.make('ipam.RIR', is_private=True)
        asns = [baker.make('ipam.ASN', asn=65000 + i, rir=rir) for i in range(8)]

        providers = baker.make('circuits.Provider', _quantity=3)
        providers[0].asns.set([asns[0], asns[1]])
        providers[1].asns.set([asns[2], asns[3]])
        providers[2].asns.set([asns[4], asns[5]])

        tags = create_tags('Alpha', 'Bravo', 'Charlie')

        cls.form_data = {
            'name': 'Provider X',
            'slug': 'provider-x',
            'asns': [asns[6].pk, asns[7].pk],
            'comments': 'Another provider',
            'tags': [t.pk for t in tags],
        }

        cls.csv_data = (
            "name,slug",
            "Provider 4,provider-4",
            "Provider 5,provider-5",
            "Provider 6,provider-6",
        )

        cls.csv_update_data = (
            "id,name,comments",
            f"{providers[0].pk},Provider 7,New comment7",
            f"{providers[1].pk},Provider 8,New comment8",
            f"{providers[2].pk},Provider 9,New comment9",
        )

        cls.bulk_edit_data = {
            'comments': 'New comments',
        }


class CircuitTypeTestCase(ViewTestCases.OrganizationalObjectViewTestCase):
    model = CircuitType

    @classmethod
    def setUpTestData(cls):

        circuit_types = baker.make('circuits.CircuitType', _quantity=3)

        tags = create_tags('Alpha', 'Bravo', 'Charlie')

        cls.form_data = {
            'name': 'Circuit Type X',
            'slug': 'circuit-type-x',
            'description': 'A new circuit type',
            'tags': [t.pk for t in tags],
        }

        cls.csv_data = (
            "name,slug",
            "Circuit Type 4,circuit-type-4",
            "Circuit Type 5,circuit-type-5",
            "Circuit Type 6,circuit-type-6",
        )

        cls.csv_update_data = (
            "id,name,description",
            f"{circuit_types[0].pk},Circuit Type 7,New description7",
            f"{circuit_types[1].pk},Circuit Type 8,New description8",
            f"{circuit_types[2].pk},Circuit Type 9,New description9",
        )

        cls.bulk_edit_data = {
            'description': 'Foo',
        }


class CircuitTestCase(ViewTestCases.PrimaryObjectViewTestCase):
    model = Circuit

    def setUp(self):
        super().setUp()

        self.add_permissions(
            'circuits.add_circuittermination',
        )

    @classmethod
    def setUpTestData(cls):
        cls.site = baker.make('dcim.Site', name='Site 1', slug='site-1')

        cls.providers = providers = baker.make('circuits.Provider', _quantity=2)

        provider_accounts = [
            baker.make('circuits.ProviderAccount', provider=providers[0]),
            baker.make('circuits.ProviderAccount', provider=providers[1]),
        ]

        cls.circuittypes = circuittypes = baker.make('circuits.CircuitType', _quantity=2)

        circuits = baker.make(
            'circuits.Circuit',
            provider=providers[0],
            provider_account=provider_accounts[0],
            type=circuittypes[0],
            _quantity=3,
        )

        tags = create_tags('Alpha', 'Bravo', 'Charlie')

        cls.form_data = {
            'cid': 'Circuit X',
            'provider': providers[1].pk,
            'provider_account': provider_accounts[1].pk,
            'type': circuittypes[1].pk,
            'status': CircuitStatusChoices.STATUS_DECOMMISSIONED,
            'tenant': None,
            'install_date': datetime.date(2020, 1, 1),
            'termination_date': datetime.date(2021, 1, 1),
            'commit_rate': 1000,
            'description': 'A new circuit',
            'comments': 'Some comments',
            'tags': [t.pk for t in tags],
        }

        cls.csv_data = (
            "cid,provider,provider_account,type,status",
            f"Circuit 4,{providers[0].name},{provider_accounts[0].name},{circuittypes[0].name},active",
            f"Circuit 5,{providers[0].name},{provider_accounts[0].name},{circuittypes[0].name},active",
            f"Circuit 6,{providers[0].name},{provider_accounts[0].name},{circuittypes[0].name},active",
        )

        cls.csv_update_data = (
            "id,cid,description,status",
            f"{circuits[0].pk},Circuit 7,New description7,{CircuitStatusChoices.STATUS_DECOMMISSIONED}",
            f"{circuits[1].pk},Circuit 8,New description8,{CircuitStatusChoices.STATUS_DECOMMISSIONED}",
            f"{circuits[2].pk},Circuit 9,New description9,{CircuitStatusChoices.STATUS_DECOMMISSIONED}",
        )

        cls.bulk_edit_data = {
            'provider': providers[1].pk,
            'provider_account': provider_accounts[1].pk,
            'type': circuittypes[1].pk,
            'status': CircuitStatusChoices.STATUS_DECOMMISSIONED,
            'tenant': None,
            'commit_rate': 2000,
            'description': 'New description',
            'comments': 'New comments',
        }

    def test_circuit_type_display_colored(self):
        circuit = Circuit.objects.first()
        circuit_type = circuit.type
        circuit_type.color = '12ab34'
        circuit_type.save()

        self.add_permissions('circuits.view_circuit')
        response = self.client.get(circuit.get_absolute_url())

        self.assertHttpStatus(response, 200)
        self.assertContains(response, circuit_type.name)
        self.assertContains(response, 'background-color: #12ab34')

    def test_bulk_import_objects_with_terminations(self):
        self.add_permissions(
            'circuits.view_circuit',
            'circuits.view_provider',
            'circuits.view_circuittype',
            'dcim.view_site',
        )
        json_data = f"""
            [
              {{
                "cid": "Circuit 7",
                "provider": "{self.providers[0].name}",
                "type": "{self.circuittypes[0].name}",
                "status": "active",
                "description": "Testing Import",
                "terminations": [
                  {{
                    "term_side": "A",
                    "termination_type": "dcim.site",
                    "termination_id": "{self.site.pk}"
                  }},
                  {{
                    "term_side": "Z",
                    "termination_type": "dcim.site",
                    "termination_id": "{self.site.pk}"
                  }}
                ]
              }}
            ]
        """

        initial_count = self._get_queryset().count()
        data = {
            'data': json_data,
            'format': ImportFormatChoices.JSON,
        }

        # Assign model-level permission
        obj_perm = ObjectPermission(
            name='Test permission',
            actions=['add']
        )
        obj_perm.save()
        obj_perm.users.add(self.user)
        obj_perm.object_types.add(ObjectType.objects.get_for_model(self.model))

        # Try GET with model-level permission
        self.assertHttpStatus(self.client.get(self._get_url('bulk_import')), 200)

        # Test POST with permission
        self.assertHttpStatus(self.client.post(self._get_url('bulk_import'), data), 302)
        self.assertEqual(self._get_queryset().count(), initial_count + 1)


class ProviderAccountTestCase(ViewTestCases.PrimaryObjectViewTestCase):
    model = ProviderAccount

    @classmethod
    def setUpTestData(cls):

        providers = baker.make('circuits.Provider', _quantity=2)

        provider_accounts = baker.make('circuits.ProviderAccount', provider=providers[0], _quantity=3)

        tags = create_tags('Alpha', 'Bravo', 'Charlie')

        cls.form_data = {
            'name': 'Provider Account X',
            'provider': providers[1].pk,
            'account': 'XXXX',
            'description': 'A new provider network',
            'comments': 'Longer description goes here',
            'tags': [t.pk for t in tags],
        }

        cls.csv_data = (
            "name,provider,account,description",
            f"Provider Account 4,{providers[0].name},4567,Foo",
            f"Provider Account 5,{providers[0].name},5678,Bar",
            f"Provider Account 6,{providers[0].name},6789,Baz",
        )

        cls.csv_update_data = (
            "id,name,account,description",
            f"{provider_accounts[0].pk},Provider Network 7,7890,New description7",
            f"{provider_accounts[1].pk},Provider Network 8,8901,New description8",
            f"{provider_accounts[2].pk},Provider Network 9,9012,New description9",
        )

        cls.bulk_edit_data = {
            'provider': providers[1].pk,
            'description': 'New description',
            'comments': 'New comments',
        }


class ProviderNetworkTestCase(ViewTestCases.PrimaryObjectViewTestCase):
    model = ProviderNetwork

    @classmethod
    def setUpTestData(cls):

        providers = baker.make('circuits.Provider', _quantity=2)

        provider_networks = baker.make('circuits.ProviderNetwork', provider=providers[0], _quantity=3)

        tags = create_tags('Alpha', 'Bravo', 'Charlie')

        cls.form_data = {
            'name': 'Provider Network X',
            'provider': providers[1].pk,
            'description': 'A new provider network',
            'comments': 'Longer description goes here',
            'tags': [t.pk for t in tags],
        }

        cls.csv_data = (
            "name,provider,description",
            f"Provider Network 4,{providers[0].name},Foo",
            f"Provider Network 5,{providers[0].name},Bar",
            f"Provider Network 6,{providers[0].name},Baz",
        )

        cls.csv_update_data = (
            "id,name,description",
            f"{provider_networks[0].pk},Provider Network 7,New description7",
            f"{provider_networks[1].pk},Provider Network 8,New description8",
            f"{provider_networks[2].pk},Provider Network 9,New description9",
        )

        cls.bulk_edit_data = {
            'provider': providers[1].pk,
            'description': 'New description',
            'comments': 'New comments',
        }


class CircuitTerminationTestCase(ViewTestCases.PrimaryObjectViewTestCase):
    model = CircuitTermination

    @classmethod
    def setUpTestData(cls):

        sites = baker.make('dcim.Site', _quantity=3)
        provider = baker.make('circuits.Provider')
        circuittype = baker.make('circuits.CircuitType')

        circuits = baker.make('circuits.Circuit', provider=provider, type=circuittype, _quantity=3)

        circuit_terminations = (
            CircuitTermination(circuit=circuits[0], term_side='A', termination=sites[0]),
            CircuitTermination(circuit=circuits[0], term_side='Z', termination=sites[1]),
            CircuitTermination(circuit=circuits[1], term_side='A', termination=sites[0]),
            CircuitTermination(circuit=circuits[1], term_side='Z', termination=sites[1]),
        )
        for ct in circuit_terminations:
            ct.save()

        cls.form_data = {
            'circuit': circuits[2].pk,
            'term_side': 'A',
            'termination_type': ContentType.objects.get_for_model(Site).pk,
            'termination': sites[2].pk,
            'description': 'New description',
        }

        site = sites[0].pk
        cls.csv_data = (
            "circuit,term_side,termination_type,termination_id,description",
            f"{circuits[2].cid},A,dcim.site,{site},Foo",
            f"{circuits[2].cid},Z,dcim.site,{site},Bar",
        )

        cls.csv_update_data = (
            "id,port_speed,description",
            f"{circuit_terminations[0].pk},100,New description7",
            f"{circuit_terminations[1].pk},200,New description8",
            f"{circuit_terminations[2].pk},300,New description9",
        )

        cls.bulk_edit_data = {
            'port_speed': 400,
            'description': 'New description',
        }

    def test_trace(self):
        self.add_permissions(
            'circuits.view_circuittermination',
            'dcim.view_cable',
            'dcim.view_interface',
            'dcim.view_device',
        )
        device = create_test_device('Device 1')

        circuittermination = CircuitTermination.objects.first()
        interface = Interface.objects.create(
            device=device,
            name='Interface 1'
        )
        Cable(a_terminations=[circuittermination], b_terminations=[interface]).save()

        response = self.client.get(reverse('circuits:circuittermination_trace', kwargs={'pk': circuittermination.pk}))
        self.assertHttpStatus(response, 200)


class CircuitGroupTestCase(ViewTestCases.OrganizationalObjectViewTestCase):
    model = CircuitGroup

    @classmethod
    def setUpTestData(cls):

        circuit_groups = baker.make('circuits.CircuitGroup', _quantity=3)

        tags = create_tags('Alpha', 'Bravo', 'Charlie')

        cls.form_data = {
            'name': 'Circuit Group X',
            'slug': 'circuit-group-x',
            'description': 'A new Circuit Group',
            'tags': [t.pk for t in tags],
        }

        cls.csv_data = (
            "name,slug",
            "Circuit Group 4,circuit-group-4",
            "Circuit Group 5,circuit-group-5",
            "Circuit Group 6,circuit-group-6",
        )

        cls.csv_update_data = (
            "id,name,description",
            f"{circuit_groups[0].pk},Circuit Group 7,New description7",
            f"{circuit_groups[1].pk},Circuit Group 8,New description8",
            f"{circuit_groups[2].pk},Circuit Group 9,New description9",
        )

        cls.bulk_edit_data = {
            'description': 'Foo',
        }


class CircuitGroupAssignmentTestCase(
    ViewTestCases.CreateObjectViewTestCase,
    ViewTestCases.EditObjectViewTestCase,
    ViewTestCases.DeleteObjectViewTestCase,
    ViewTestCases.ListObjectsViewTestCase,
    ViewTestCases.BulkEditObjectsViewTestCase,
    ViewTestCases.BulkImportObjectsViewTestCase,
    ViewTestCases.BulkDeleteObjectsViewTestCase
):
    model = CircuitGroupAssignment

    @classmethod
    def setUpTestData(cls):

        circuit_groups = baker.make('circuits.CircuitGroup', _quantity=4)

        provider = baker.make('circuits.Provider')
        circuittype = baker.make('circuits.CircuitType')

        circuits = baker.make('circuits.Circuit', provider=provider, type=circuittype, _quantity=4)

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

        tags = create_tags('Alpha', 'Bravo', 'Charlie')

        cls.form_data = {
            'group': circuit_groups[3].pk,
            'member_type': ContentType.objects.get_for_model(Circuit).pk,
            'member': circuits[3].pk,
            'priority': CircuitPriorityChoices.PRIORITY_INACTIVE,
            'tags': [t.pk for t in tags],
        }

        cls.csv_data = (
            "member_type,member_id,group,priority",
            f"circuits.circuit,{circuits[0].pk},{circuit_groups[3].pk},primary",
            f"circuits.circuit,{circuits[1].pk},{circuit_groups[3].pk},secondary",
            f"circuits.circuit,{circuits[2].pk},{circuit_groups[3].pk},tertiary",
        )

        cls.csv_update_data = (
            "id,priority",
            f"{assignments[0].pk},inactive",
            f"{assignments[1].pk},inactive",
            f"{assignments[2].pk},inactive",
        )

        cls.bulk_edit_data = {
            'priority': CircuitPriorityChoices.PRIORITY_INACTIVE,
        }


class VirtualCircuitTypeTestCase(ViewTestCases.OrganizationalObjectViewTestCase):
    model = VirtualCircuitType

    @classmethod
    def setUpTestData(cls):

        virtual_circuit_types = baker.make('circuits.VirtualCircuitType', _quantity=3)

        tags = create_tags('Alpha', 'Bravo', 'Charlie')

        cls.form_data = {
            'name': 'Virtual Circuit Type X',
            'slug': 'virtual-circuit-type-x',
            'description': 'A new virtual circuit type',
            'tags': [t.pk for t in tags],
        }

        cls.csv_data = (
            "name,slug",
            "Virtual Circuit Type 4,circuit-type-4",
            "Virtual Circuit Type 5,circuit-type-5",
            "Virtual Circuit Type 6,circuit-type-6",
        )

        cls.csv_update_data = (
            "id,name,description",
            f"{virtual_circuit_types[0].pk},Virtual Circuit Type 7,New description7",
            f"{virtual_circuit_types[1].pk},Virtual Circuit Type 8,New description8",
            f"{virtual_circuit_types[2].pk},Virtual Circuit Type 9,New description9",
        )

        cls.bulk_edit_data = {
            'description': 'Foo',
        }


class VirtualCircuitTestCase(ViewTestCases.PrimaryObjectViewTestCase):
    model = VirtualCircuit

    def setUp(self):
        super().setUp()

        self.add_permissions(
            'circuits.add_virtualcircuittermination',
        )

    @classmethod
    def setUpTestData(cls):
        provider = baker.make('circuits.Provider')
        cls.provider_networks = provider_networks = baker.make(
            'circuits.ProviderNetwork', provider=provider, _quantity=2
        )
        provider_accounts = baker.make('circuits.ProviderAccount', provider=provider, _quantity=2)
        cls.virtual_circuit_types = virtual_circuit_types = baker.make(
            'circuits.VirtualCircuitType', _quantity=2
        )

        virtual_circuits = baker.make(
            'circuits.VirtualCircuit',
            provider_network=provider_networks[0],
            provider_account=provider_accounts[0],
            type=virtual_circuit_types[0],
            _quantity=3,
        )

        device = create_test_device('Device 1')
        interfaces = []
        for i in range(3):
            interfaces.append(
                Interface.objects.create(
                    device=device, name=f'Interface {i + 1}', type=InterfaceTypeChoices.TYPE_VIRTUAL
                )
            )

        tags = create_tags('Alpha', 'Bravo', 'Charlie')

        cls.form_data = {
            'cid': 'Virtual Circuit X',
            'provider_network': provider_networks[1].pk,
            'provider_account': provider_accounts[1].pk,
            'type': virtual_circuit_types[1].pk,
            'status': CircuitStatusChoices.STATUS_PLANNED,
            'description': 'A new virtual circuit',
            'comments': 'Some comments',
            'tags': [t.pk for t in tags],
        }

        cls.csv_data = (
            "cid,provider_network,provider_account,type,status",
            (
                f"Virtual Circuit 4,{provider_networks[0].name},{provider_accounts[0].account},"
                f"{virtual_circuit_types[0].name},{CircuitStatusChoices.STATUS_PLANNED}"
            ),
            (
                f"Virtual Circuit 5,{provider_networks[0].name},{provider_accounts[0].account},"
                f"{virtual_circuit_types[0].name},{CircuitStatusChoices.STATUS_PLANNED}"
            ),
            (
                f"Virtual Circuit 6,{provider_networks[0].name},{provider_accounts[0].account},"
                f"{virtual_circuit_types[0].name},{CircuitStatusChoices.STATUS_PLANNED}"
            ),
        )

        cls.csv_update_data = (
            "id,cid,description,type,status",
            (
                f"{virtual_circuits[0].pk},Virtual Circuit A,New description,{virtual_circuit_types[1].name},"
                f"{CircuitStatusChoices.STATUS_DECOMMISSIONED}"
            ),
            (
                f"{virtual_circuits[1].pk},Virtual Circuit B,New description,{virtual_circuit_types[1].name},"
                f"{CircuitStatusChoices.STATUS_DECOMMISSIONED}"
            ),
            (
                f"{virtual_circuits[2].pk},Virtual Circuit C,New description,{virtual_circuit_types[1].name},"
                f"{CircuitStatusChoices.STATUS_DECOMMISSIONED}"
            ),
        )

        cls.bulk_edit_data = {
            'provider_network': provider_networks[1].pk,
            'provider_account': provider_accounts[1].pk,
            'type': virtual_circuit_types[1].pk,
            'status': CircuitStatusChoices.STATUS_DECOMMISSIONED,
            'description': 'New description',
            'comments': 'New comments',
        }

    def test_bulk_import_objects_with_terminations(self):
        self.add_permissions(
            'circuits.view_virtualcircuit',
            'circuits.view_providernetwork',
            'circuits.view_virtualcircuittype',
            'dcim.view_interface',
        )
        interfaces = Interface.objects.filter(type=InterfaceTypeChoices.TYPE_VIRTUAL)
        json_data = f"""
            [
              {{
                "cid": "Virtual Circuit 7",
                "provider_network": "{self.provider_networks[0].name}",
                "type": "{self.virtual_circuit_types[0].name}",
                "status": "active",
                "terminations": [
                  {{
                    "role": "hub",
                    "interface": {interfaces[0].pk}
                  }},
                  {{
                    "role": "spoke",
                    "interface": {interfaces[1].pk}
                  }},
                  {{
                    "role": "spoke",
                    "interface": {interfaces[2].pk}
                  }}
                ]
              }}
            ]
        """

        initial_count = self._get_queryset().count()
        data = {
            'data': json_data,
            'format': ImportFormatChoices.JSON,
        }

        # Assign model-level permission
        obj_perm = ObjectPermission(
            name='Test permission',
            actions=['add']
        )
        obj_perm.save()
        obj_perm.users.add(self.user)
        obj_perm.object_types.add(ObjectType.objects.get_for_model(self.model))

        # Try GET with model-level permission
        self.assertHttpStatus(self.client.get(self._get_url('bulk_import')), 200)

        # Test POST with permission
        self.assertHttpStatus(self.client.post(self._get_url('bulk_import'), data), 302)
        self.assertEqual(self._get_queryset().count(), initial_count + 1)


class VirtualCircuitTerminationTestCase(ViewTestCases.PrimaryObjectViewTestCase):
    model = VirtualCircuitTermination

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

        cls.form_data = {
            'virtual_circuit': virtual_circuits[3].pk,
            'role': VirtualCircuitTerminationRoleChoices.ROLE_HUB,
            'interface': virtual_interfaces[6].pk
        }

        vc_cid = virtual_circuits[3].cid
        hub = VirtualCircuitTerminationRoleChoices.ROLE_HUB
        spoke = VirtualCircuitTerminationRoleChoices.ROLE_SPOKE
        cls.csv_data = (
            "virtual_circuit,role,interface,description",
            f"{vc_cid},{hub},{virtual_interfaces[6].pk},Hub",
            f"{vc_cid},{spoke},{virtual_interfaces[7].pk},Spoke 1",
            f"{vc_cid},{spoke},{virtual_interfaces[8].pk},Spoke 2",
            f"{vc_cid},{spoke},{virtual_interfaces[9].pk},Spoke 3",
        )

        cls.csv_update_data = (
            "id,role,description",
            f"{virtual_circuit_terminations[0].pk},{VirtualCircuitTerminationRoleChoices.ROLE_SPOKE},New description",
            f"{virtual_circuit_terminations[1].pk},{VirtualCircuitTerminationRoleChoices.ROLE_SPOKE},New description",
            f"{virtual_circuit_terminations[2].pk},{VirtualCircuitTerminationRoleChoices.ROLE_SPOKE},New description",
        )

        cls.bulk_edit_data = {
            'description': 'New description',
        }
