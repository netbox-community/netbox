from django.test import TestCase

from utilities.forms import *


class ExpandIPAddress(TestCase):
    """
    Validate the operation of expand_ipaddress_pattern().
    """
    def test_ipv4_range(self):
        input = '1.2.3.[9-10]/32'
        output = sorted([
            '1.2.3.9/32',
            '1.2.3.10/32',
        ])

        self.assertEqual(sorted(expand_ipaddress_pattern(input, 4)), output)

    def test_ipv4_set(self):
        input = '1.2.3.[4,44]/32'
        output = sorted([
            '1.2.3.4/32',
            '1.2.3.44/32',
        ])

        self.assertEqual(sorted(expand_ipaddress_pattern(input, 4)), output)

    def test_ipv4_multiple_ranges(self):
        input = '1.[9-10].3.[9-11]/32'
        output = sorted([
            '1.9.3.9/32',
            '1.9.3.10/32',
            '1.9.3.11/32',
            '1.10.3.9/32',
            '1.10.3.10/32',
            '1.10.3.11/32',
        ])

        self.assertEqual(sorted(expand_ipaddress_pattern(input, 4)), output)

    def test_ipv4_multiple_sets(self):
        input = '1.[2,22].3.[4,44]/32'
        output = sorted([
            '1.2.3.4/32',
            '1.2.3.44/32',
            '1.22.3.4/32',
            '1.22.3.44/32',
        ])

        self.assertEqual(sorted(expand_ipaddress_pattern(input, 4)), output)

    def test_ipv4_set_and_range(self):
        input = '1.[2,22].3.[9-11]/32'
        output = sorted([
            '1.2.3.9/32',
            '1.2.3.10/32',
            '1.2.3.11/32',
            '1.22.3.9/32',
            '1.22.3.10/32',
            '1.22.3.11/32',
        ])

        self.assertEqual(sorted(expand_ipaddress_pattern(input, 4)), output)

    # TODO: IPv6
    # TODO: negative tests

# TODO: alphanumeric
