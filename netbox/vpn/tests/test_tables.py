from utilities.testing import TableTestCases
from vpn.tables import *


class TunnelGroupTableTest(TableTestCases.StandardTableTestCase):
    table = TunnelGroupTable


class TunnelTableTest(TableTestCases.StandardTableTestCase):
    table = TunnelTable


class TunnelTerminationTableTest(TableTestCases.StandardTableTestCase):
    table = TunnelTerminationTable


class IKEProposalTableTest(TableTestCases.StandardTableTestCase):
    table = IKEProposalTable


class IKEPolicyTableTest(TableTestCases.StandardTableTestCase):
    table = IKEPolicyTable


class IPSecProposalTableTest(TableTestCases.StandardTableTestCase):
    table = IPSecProposalTable


class IPSecPolicyTableTest(TableTestCases.StandardTableTestCase):
    table = IPSecPolicyTable


class IPSecProfileTableTest(TableTestCases.StandardTableTestCase):
    table = IPSecProfileTable


class L2VPNTableTest(TableTestCases.StandardTableTestCase):
    table = L2VPNTable


class L2VPNTerminationTableTest(TableTestCases.StandardTableTestCase):
    table = L2VPNTerminationTable
