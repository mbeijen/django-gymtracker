from django.test import TestCase
from datetime import timedelta
from .templatetags.duration_filters import duration_format


class DurationFilterTests(TestCase):
    """Test the duration_format template filter"""

    def test_duration_format_hours_and_minutes(self):
        """Test formatting duration with hours and minutes"""
        duration = timedelta(hours=2, minutes=37, seconds=45)
        result = duration_format(duration)
        self.assertEqual(result, "2:37")

    def test_duration_format_minutes_only(self):
        """Test formatting duration with minutes only"""
        duration = timedelta(minutes=45, seconds=30)
        result = duration_format(duration)
        self.assertEqual(result, "45m")

    def test_duration_format_zero_minutes(self):
        """Test formatting duration with zero minutes"""
        duration = timedelta(hours=1, minutes=0, seconds=30)
        result = duration_format(duration)
        self.assertEqual(result, "1:00")

    def test_duration_format_none(self):
        """Test formatting None duration"""
        result = duration_format(None)
        self.assertEqual(result, "")

    def test_duration_format_string(self):
        """Test formatting string duration (fallback)"""
        result = duration_format("2:30")
        self.assertEqual(result, "2:30")
