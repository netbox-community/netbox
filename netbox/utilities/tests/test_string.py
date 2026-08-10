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

    def test_fractional_seconds_rounded_above_one_second(self):
        self.assertEqual(humanize_duration(timedelta(seconds=1, milliseconds=999)), '2s')
        self.assertEqual(humanize_duration(timedelta(seconds=1, milliseconds=100)), '1s')
        self.assertEqual(humanize_duration(timedelta(seconds=59, milliseconds=600)), '1m')

    def test_negative_duration_retains_sign(self):
        # A negative duration is anomalous (e.g. resulting from clock skew), so it is rendered as
        # such rather than decomposed into a nonsensical value.
        self.assertEqual(humanize_duration(timedelta(seconds=-5)), '-5s')
        self.assertEqual(humanize_duration(timedelta(seconds=-1.5)), '-2s')
        self.assertEqual(humanize_duration(timedelta(days=-2)), '-2d')
        self.assertEqual(humanize_duration(timedelta(milliseconds=-430)), '-0.43s')

    def test_negative_duration_rounding_to_zero_carries_no_sign(self):
        self.assertEqual(humanize_duration(timedelta(microseconds=-400)), '0s')

    def test_sub_second_rounding_up_to_one_second(self):
        # A magnitude which rounds up to a whole second reads as "1s", not "1.0s"
        self.assertEqual(humanize_duration(timedelta(seconds=0.9996)), '1s')
