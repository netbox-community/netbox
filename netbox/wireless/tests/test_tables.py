from utilities.testing import TableTestCases
from wireless.tables import *


class WirelessLANGroupTableTest(TableTestCases.StandardTableTestCase):
    table = WirelessLANGroupTable


class WirelessLANTableTest(TableTestCases.StandardTableTestCase):
    table = WirelessLANTable


class WirelessLinkTableTest(TableTestCases.StandardTableTestCase):
    table = WirelessLinkTable
