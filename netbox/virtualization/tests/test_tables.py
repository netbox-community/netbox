from utilities.testing import TableTestCases
from virtualization.tables import *


class ClusterTypeTableTest(TableTestCases.StandardTableTestCase):
    table = ClusterTypeTable


class ClusterGroupTableTest(TableTestCases.StandardTableTestCase):
    table = ClusterGroupTable


class ClusterTableTest(TableTestCases.StandardTableTestCase):
    table = ClusterTable


class VirtualMachineTableTest(TableTestCases.StandardTableTestCase):
    table = VirtualMachineTable


class VMInterfaceTableTest(TableTestCases.StandardTableTestCase):
    table = VMInterfaceTable


class VirtualDiskTableTest(TableTestCases.StandardTableTestCase):
    table = VirtualDiskTable
