from circuits.tables import *
from utilities.testing import TableTestCases


class CircuitTypeTableTestCase(TableTestCases.StandardTableTestCase):
    table = CircuitTypeTable


class CircuitTableTestCase(TableTestCases.StandardTableTestCase):
    table = CircuitTable


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


class VirtualCircuitTerminationTableTestCase(TableTestCases.StandardTableTestCase):
    table = VirtualCircuitTerminationTable
