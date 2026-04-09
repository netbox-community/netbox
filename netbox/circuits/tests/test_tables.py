from circuits.tables import *
from utilities.testing import TableTestCases


class CircuitTypeTableTest(TableTestCases.StandardTableTestCase):
    table = CircuitTypeTable


class CircuitTableTest(TableTestCases.StandardTableTestCase):
    table = CircuitTable


class CircuitTerminationTableTest(TableTestCases.StandardTableTestCase):
    table = CircuitTerminationTable


class CircuitGroupTableTest(TableTestCases.StandardTableTestCase):
    table = CircuitGroupTable


class CircuitGroupAssignmentTableTest(TableTestCases.StandardTableTestCase):
    table = CircuitGroupAssignmentTable


class ProviderTableTest(TableTestCases.StandardTableTestCase):
    table = ProviderTable


class ProviderAccountTableTest(TableTestCases.StandardTableTestCase):
    table = ProviderAccountTable


class ProviderNetworkTableTest(TableTestCases.StandardTableTestCase):
    table = ProviderNetworkTable


class VirtualCircuitTypeTableTest(TableTestCases.StandardTableTestCase):
    table = VirtualCircuitTypeTable


class VirtualCircuitTableTest(TableTestCases.StandardTableTestCase):
    table = VirtualCircuitTable


class VirtualCircuitTerminationTableTest(TableTestCases.StandardTableTestCase):
    table = VirtualCircuitTerminationTable
