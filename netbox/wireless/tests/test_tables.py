from utilities.testing import TableTestCases
from wireless.tables import *


class WirelessLANGroupTableTestCase(TableTestCases.StandardTableTestCase):
    table = WirelessLANGroupTable


class WirelessLANTableTestCase(TableTestCases.StandardTableTestCase):
    table = WirelessLANTable


class WirelessLinkTableTestCase(TableTestCases.StandardTableTestCase):
    table = WirelessLinkTable
