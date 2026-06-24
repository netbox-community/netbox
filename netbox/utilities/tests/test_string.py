from datetime import timedelta

from django.test import TestCase

from utilities.string import humanize_duration


class HumanizeDurationTest(TestCase):

    def test_none_and_zero(self):
        self.assertEqual(humanize_duration(None), '')
        self.assertEqual(humanize_duration(timedelta(0)), '')

    def test_seconds_only(self):
        self.assertEqual(humanize_duration(timedelta(seconds=45)), '45s')

    def test_minutes_and_seconds(self):
        self.assertEqual(humanize_duration(timedelta(minutes=5, seconds=23)), '5m 23s')

    def test_hours_minutes_seconds(self):
        self.assertEqual(humanize_duration(timedelta(hours=1, minutes=5, seconds=23)), '1h 5m 23s')

    def test_days(self):
        self.assertEqual(humanize_duration(timedelta(days=2, hours=3, minutes=17)), '2d 3h 17m')

    def test_whole_minute_omits_seconds(self):
        self.assertEqual(humanize_duration(timedelta(minutes=2)), '2m')

    def test_sub_second_rounds_down_to_zero(self):
        # Fractional seconds are truncated; a sub-second duration reads as 0s.
        self.assertEqual(humanize_duration(timedelta(milliseconds=500)), '0s')
