from django.test import TestCase

from utilities.ordering import naturalize, naturalize_interface


class NaturalizationTestCase(TestCase):
    """
    Validate the operation of the functions which generate values suitable for natural ordering.
    """
    def test_naturalize(self):

        data = (
            # Original, naturalized
            ('abc', 'abc'),
            ('123', '00000123'),
            ('abc123', 'abc00000123'),
            ('123abc', '00000123abc'),
            ('123abc456', '00000123abc00000456'),
            ('abc123def', 'abc00000123def'),
            ('abc123def456', 'abc00000123def00000456'),
        )

        for origin, naturalized in data:
            self.assertEqual(naturalize(origin), naturalized)

    def test_naturalize_interface(self):

        data = (
            # Original, naturalized
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
        )

        for origin, naturalized in data:
            self.assertEqual(naturalize_interface(origin), naturalized)
