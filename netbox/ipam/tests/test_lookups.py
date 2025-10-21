from django.test import TestCase
from django.db.backends.postgresql.psycopg_any import NumericRange
from ipam.models import VLANGroup


class VLANGroupRangeContainsLookupTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Two ranges: [1,11) and [20,31)
        cls.g1 = VLANGroup.objects.create(
            name='VlanGroup-A',
            slug='VlanGroup-A',
            vid_ranges=[NumericRange(1, 11), NumericRange(20, 31)],
        )
        # One range: [100,201)
        cls.g2 = VLANGroup.objects.create(
            name='VlanGroup-B',
            slug='VlanGroup-B',
            vid_ranges=[NumericRange(100, 201)],
        )
        cls.g_empty = VLANGroup.objects.create(
            name='VlanGroup-empty',
            slug='VlanGroup-empty',
            vid_ranges=[],
        )

    def test_contains_value_in_first_range(self):
        """
        Tests whether a specific value is contained within the first range in a queried
        set of VLANGroup objects.
        """
        names = list(
            VLANGroup.objects.filter(vid_ranges__range_contains=10).values_list('name', flat=True).order_by('name')
        )
        self.assertEqual(names, ['VlanGroup-A'])

    def test_contains_value_in_second_range(self):
        """
        Tests if a value exists in the second range of VLANGroup objects and
        validates the result against the expected list of names.
        """
        names = list(
            VLANGroup.objects.filter(vid_ranges__range_contains=25).values_list('name', flat=True).order_by('name')
        )
        self.assertEqual(names, ['VlanGroup-A'])

    def test_upper_bound_is_exclusive(self):
        """
        Tests if the upper bound of the range is exclusive in the filter method.
        """
        # 11 is NOT in [1,11)
        self.assertFalse(VLANGroup.objects.filter(vid_ranges__range_contains=11).exists())

    def test_no_match_far_outside(self):
        """
        Tests that no VLANGroup contains a VID within a specified range far outside
        common VID bounds and returns `False`.
        """
        self.assertFalse(VLANGroup.objects.filter(vid_ranges__range_contains=4095).exists())

    def test_empty_array_never_matches(self):
        """
        Tests the behavior of VLANGroup objects when an empty array is used to match a
        specific condition.
        """
        self.assertFalse(VLANGroup.objects.filter(pk=self.g_empty.pk, vid_ranges__range_contains=1).exists())
