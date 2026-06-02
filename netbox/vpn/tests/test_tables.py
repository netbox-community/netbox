from utilities.testing import TableTestCases
from vpn.tables import *


class TunnelGroupTableTestCase(TableTestCases.StandardTableTestCase):
    table = TunnelGroupTable


class TunnelTableTestCase(TableTestCases.StandardTableTestCase):
    table = TunnelTable


class TunnelTerminationTableTestCase(TableTestCases.StandardTableTestCase):
    table = TunnelTerminationTable


class IKEProposalTableTestCase(TableTestCases.StandardTableTestCase):
    table = IKEProposalTable


class IKEPolicyTableTestCase(TableTestCases.StandardTableTestCase):
    table = IKEPolicyTable


class IPSecProposalTableTestCase(TableTestCases.StandardTableTestCase):
    table = IPSecProposalTable


class IPSecPolicyTableTestCase(TableTestCases.StandardTableTestCase):
    table = IPSecPolicyTable


class IPSecProfileTableTestCase(TableTestCases.StandardTableTestCase):
    table = IPSecProfileTable


class L2VPNTableTestCase(TableTestCases.StandardTableTestCase):
    table = L2VPNTable


class L2VPNTerminationTableTestCase(TableTestCases.StandardTableTestCase):
    table = L2VPNTerminationTable
