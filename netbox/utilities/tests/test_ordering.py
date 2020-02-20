from django.test import TestCase

from utilities.ordering import naturalize, naturalize_interface


class NaturalizationTestCase(TestCase):
    """
    Validate the operation of the functions which generate values suitable for natural ordering.
    """
    def test_naturalize(self):

        # Original, naturalized
        data = (
            ('abc', 'abc'),
            ('123', '00000123'),
            ('abc123', 'abc00000123'),
            ('123abc', '00000123abc'),
            ('123abc456', '00000123abc00000456'),
            ('abc123def', 'abc00000123def'),
            ('abc123def456', 'abc00000123def00000456'),
        )

        for origin, naturalized in data:
            self.assertEqual(naturalize(origin, max_length=100), naturalized)

    def test_naturalize_max_length(self):
        self.assertEqual(naturalize('abc123def456', max_length=10), 'abc0000012')

    def test_naturalize_interface(self):

        # Original, naturalized
        data = (
            # IOS/JunOS-style
            ('Gi', '9999999999999999Gi000000000000000000'),
            ('Gi1', '9999999999999999Gi000001000000000000'),
            ('Gi1/2', '0001999999999999Gi000002000000000000'),
            ('Gi1/2/3', '0001000299999999Gi000003000000000000'),
            ('Gi1/2/3/4', '0001000200039999Gi000004000000000000'),
            ('Gi1/2/3/4/5', '0001000200030004Gi000005000000000000'),
            ('Gi1/2/3/4/5:6', '0001000200030004Gi000005000006000000'),
            ('Gi1/2/3/4/5:6.7', '0001000200030004Gi000005000006000007'),
            ('Gi1:2', '9999999999999999Gi000001000002000000'),
            ('Gi1:2.3', '9999999999999999Gi000001000002000003'),
            # Generic
            ('Interface 1', '9999999999999999Interface 000001000000000000'),
            ('Interface 1 (other)', '9999999999999999Interface 000001000000000000 (other)'),
            ('Interface 99', '9999999999999999Interface 000099000000000000'),
            ('PCIe1-p1', '9999999999999999PCIe000001000000000000-p00000001'),
            ('PCIe1-p99', '9999999999999999PCIe000001000000000000-p00000099'),
        )

        for origin, naturalized in data:
            self.assertEqual(naturalize_interface(origin, max_length=100), naturalized)

    def test_naturalize_interface_max_length(self):
        self.assertEqual(naturalize_interface('Gi1/2/3', max_length=20), '0001000299999999Gi00')
