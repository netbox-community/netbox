from circuits.models import Circuit, Provider
from utilities.prefetch import get_prefetchable_fields
from utilities.testing.base import TestCase


class GetPrefetchableFieldsTest(TestCase):
    """
    Verify the operation of get_prefetchable_fields()
    """
    def test_get_prefetchable_fields(self):
        field_names = get_prefetchable_fields(Provider)
        self.assertIn('asns', field_names)  # ManyToManyField
        self.assertIn('circuits', field_names)  # Reverse relation
        self.assertIn('tags', field_names)  # Tags

        field_names = get_prefetchable_fields(Circuit)
        self.assertIn('group_assignments', field_names)  # Generic relation
