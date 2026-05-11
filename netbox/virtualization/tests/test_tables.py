from utilities.testing import TableTestCases
from virtualization.tables import *


class ClusterTypeTableTestCase(TableTestCases.StandardTableTestCase):
    table = ClusterTypeTable


class ClusterGroupTableTestCase(TableTestCases.StandardTableTestCase):
    table = ClusterGroupTable


class ClusterTableTestCase(TableTestCases.StandardTableTestCase):
    table = ClusterTable


class VirtualMachineTableTestCase(TableTestCases.StandardTableTestCase):
    table = VirtualMachineTable


class VMInterfaceTableTestCase(TableTestCases.StandardTableTestCase):
    table = VMInterfaceTable


class VirtualDiskTableTestCase(TableTestCases.StandardTableTestCase):
    table = VirtualDiskTable
