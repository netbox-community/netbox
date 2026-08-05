from datetime import timedelta

from django.test import TestCase

from utilities.string import humanize_duration


class HumanizeDurationTest(TestCase):

    def test_none(self):
        self.assertEqual(humanize_duration(None), '')

    def test_zero_duration(self):
        self.assertEqual(humanize_duration(timedelta(0)), '0s')

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

    def test_sub_second_renders_decimal(self):
        # Sub-second durations retain millisecond precision, with trailing zeros stripped.
        self.assertEqual(humanize_duration(timedelta(milliseconds=500)), '0.5s')
        self.assertEqual(humanize_duration(timedelta(milliseconds=430)), '0.43s')
        self.assertEqual(humanize_duration(timedelta(milliseconds=4)), '0.004s')

    def test_sub_millisecond_rounds_to_zero(self):
        # Anything below a millisecond has no decimal representation, so it reads as 0s.
        self.assertEqual(humanize_duration(timedelta(microseconds=400)), '0s')

    def test_fractional_seconds_truncated_above_one_second(self):
        self.assertEqual(humanize_duration(timedelta(seconds=1, milliseconds=999)), '1s')

    def test_negative_duration_clamped_to_zero(self):
        # A negative duration (e.g. resulting from clock skew) never renders as negative.
        self.assertEqual(humanize_duration(timedelta(seconds=-1.5)), '0s')
        self.assertEqual(humanize_duration(timedelta(days=-2)), '0s')
