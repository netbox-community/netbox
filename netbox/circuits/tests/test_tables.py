from django.test import tag

from circuits.choices import CircuitPriorityChoices
from circuits.models import (
    Circuit,
    CircuitGroup,
    CircuitGroupAssignment,
    CircuitType,
    Provider,
    ProviderNetwork,
    VirtualCircuit,
    VirtualCircuitType,
)
from circuits.tables import *
from utilities.testing import TableTestCases


class CircuitTypeTableTestCase(TableTestCases.StandardTableTestCase):
    table = CircuitTypeTable


class CircuitTableTestCase(TableTestCases.StandardTableTestCase):
    table = CircuitTable

    @classmethod
    def setUpTestData(cls):
        provider = Provider.objects.create(name='Provider 1', slug='provider-1')
        circuit_type = CircuitType.objects.create(name='Circuit Type 1', slug='circuit-type-1')
        circuits = (
            Circuit(cid='Circuit 1', provider=provider, type=circuit_type),
            Circuit(cid='Circuit 2', provider=provider, type=circuit_type),
            Circuit(cid='Circuit 3', provider=provider, type=circuit_type),
        )
        Circuit.objects.bulk_create(circuits)
        circuit_groups = (
            CircuitGroup(name='Circuit Group 1', slug='circuit-group-1'),
            CircuitGroup(name='Circuit Group 2', slug='circuit-group-2'),
        )
        CircuitGroup.objects.bulk_create(circuit_groups)
        cls.assignments = (
            CircuitGroupAssignment(
                member=circuits[0], group=circuit_groups[0], priority=CircuitPriorityChoices.PRIORITY_PRIMARY
            ),
            CircuitGroupAssignment(member=circuits[0], group=circuit_groups[1]),
            CircuitGroupAssignment(
                member=circuits[1], group=circuit_groups[0], priority=CircuitPriorityChoices.PRIORITY_SECONDARY
            ),
        )
        CircuitGroupAssignment.objects.bulk_create(cls.assignments)

    @tag('regression')  # Ref: #23342
    def test_assignments_column(self):
        """The assignments column links the group assignments of each circuit."""
        url1, url2, url3 = (assignment.get_absolute_url() for assignment in self.assignments)
        self.user.config.set('tables.CircuitTable.columns', ['cid', 'assignments'], commit=True)
        table = CircuitTable(Circuit.objects.all())
        table.configure(self.get_request())
        cells = {row.record.cid: row.get_cell('assignments') for row in table.rows}

        self.assertHTMLEqual(
            cells['Circuit 1'],
            f'<a href="{url1}">Circuit Group 1 (Primary)</a>, <a href="{url2}">Circuit Group 2</a>'
        )
        self.assertHTMLEqual(cells['Circuit 2'], f'<a href="{url3}">Circuit Group 1 (Secondary)</a>')
        self.assertEqual(cells['Circuit 3'], table.columns['assignments'].default)

    @tag('regression')  # Ref: #23342
    def test_assignments_export(self):
        """An export lists the group assignments of each circuit."""
        table = CircuitTable(Circuit.objects.all())
        table.configure(self.get_request())
        # An "All Data" export prefetches for every column, hidden or not
        table._apply_prefetching(columns=table.columns.names())
        values = {row.record.cid: row.get_cell_value('assignments') for row in table.rows}

        self.assertEqual(values, {
            'Circuit 1': 'Circuit Group 1 (Primary), Circuit Group 2',
            'Circuit 2': 'Circuit Group 1 (Secondary)',
            'Circuit 3': None,
        })


class CircuitTerminationTableTestCase(TableTestCases.StandardTableTestCase):
    table = CircuitTerminationTable


class CircuitGroupTableTestCase(TableTestCases.StandardTableTestCase):
    table = CircuitGroupTable


class CircuitGroupAssignmentTableTestCase(TableTestCases.StandardTableTestCase):
    table = CircuitGroupAssignmentTable


class ProviderTableTestCase(TableTestCases.StandardTableTestCase):
    table = ProviderTable


class ProviderAccountTableTestCase(TableTestCases.StandardTableTestCase):
    table = ProviderAccountTable


class ProviderNetworkTableTestCase(TableTestCases.StandardTableTestCase):
    table = ProviderNetworkTable


class VirtualCircuitTypeTableTestCase(TableTestCases.StandardTableTestCase):
    table = VirtualCircuitTypeTable


class VirtualCircuitTableTestCase(TableTestCases.StandardTableTestCase):
    table = VirtualCircuitTable

    @classmethod
    def setUpTestData(cls):
        provider = Provider.objects.create(name='Provider 1', slug='provider-1')
        provider_network = ProviderNetwork.objects.create(name='Provider Network 1', provider=provider)
        virtual_circuit_type = VirtualCircuitType.objects.create(
            name='Virtual Circuit Type 1', slug='virtual-circuit-type-1'
        )
        virtual_circuits = (
            VirtualCircuit(cid='Virtual Circuit 1', provider_network=provider_network, type=virtual_circuit_type),
            VirtualCircuit(cid='Virtual Circuit 2', provider_network=provider_network, type=virtual_circuit_type),
            VirtualCircuit(cid='Virtual Circuit 3', provider_network=provider_network, type=virtual_circuit_type),
        )
        VirtualCircuit.objects.bulk_create(virtual_circuits)
        circuit_groups = (
            CircuitGroup(name='Circuit Group 1', slug='circuit-group-1'),
            CircuitGroup(name='Circuit Group 2', slug='circuit-group-2'),
        )
        CircuitGroup.objects.bulk_create(circuit_groups)
        cls.assignments = (
            CircuitGroupAssignment(
                member=virtual_circuits[0], group=circuit_groups[0], priority=CircuitPriorityChoices.PRIORITY_PRIMARY
            ),
            CircuitGroupAssignment(member=virtual_circuits[0], group=circuit_groups[1]),
            CircuitGroupAssignment(
                member=virtual_circuits[1], group=circuit_groups[0], priority=CircuitPriorityChoices.PRIORITY_SECONDARY
            ),
        )
        CircuitGroupAssignment.objects.bulk_create(cls.assignments)

    def test_assignments_column(self):
        """The assignments column links the group assignments of each virtual circuit."""
        url1, url2, url3 = (assignment.get_absolute_url() for assignment in self.assignments)
        self.user.config.set('tables.VirtualCircuitTable.columns', ['cid', 'assignments'], commit=True)
        table = VirtualCircuitTable(VirtualCircuit.objects.all())
        table.configure(self.get_request())
        cells = {row.record.cid: row.get_cell('assignments') for row in table.rows}

        self.assertHTMLEqual(
            cells['Virtual Circuit 1'],
            f'<a href="{url1}">Circuit Group 1 (Primary)</a>, <a href="{url2}">Circuit Group 2</a>'
        )
        self.assertHTMLEqual(cells['Virtual Circuit 2'], f'<a href="{url3}">Circuit Group 1 (Secondary)</a>')
        self.assertEqual(cells['Virtual Circuit 3'], table.columns['assignments'].default)

    def test_assignments_export(self):
        """An export lists the group assignments of each virtual circuit."""
        table = VirtualCircuitTable(VirtualCircuit.objects.all())
        table.configure(self.get_request())
        # An "All Data" export prefetches for every column, hidden or not
        table._apply_prefetching(columns=table.columns.names())
        values = {row.record.cid: row.get_cell_value('assignments') for row in table.rows}

        self.assertEqual(values, {
            'Virtual Circuit 1': 'Circuit Group 1 (Primary), Circuit Group 2',
            'Virtual Circuit 2': 'Circuit Group 1 (Secondary)',
            'Virtual Circuit 3': None,
        })


class VirtualCircuitTerminationTableTestCase(TableTestCases.StandardTableTestCase):
    table = VirtualCircuitTerminationTable
