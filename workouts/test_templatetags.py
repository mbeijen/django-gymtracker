from django.test import TestCase
from datetime import timedelta
from decimal import Decimal
from .templatetags.duration_filters import duration_format, weight_format


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


class WeightFilterTests(TestCase):
    """Test the weight_format template filter"""

    def test_weight_format_whole_number(self):
        """Test formatting whole number weights"""
        result = weight_format(Decimal("20"))
        self.assertEqual(result, "20")

    def test_weight_format_whole_number_float(self):
        """Test formatting whole number weights from float"""
        result = weight_format(20.0)
        self.assertEqual(result, "20")

    def test_weight_format_half_kg(self):
        """Test formatting half kilogram weights"""
        result = weight_format(Decimal("22.5"))
        self.assertEqual(result, "22,5")

    def test_weight_format_half_kg_float(self):
        """Test formatting half kilogram weights from float"""
        result = weight_format(22.5)
        self.assertEqual(result, "22,5")

    def test_weight_format_quarter_kg(self):
        """Test formatting quarter kilogram weights"""
        result = weight_format(Decimal("20.25"))
        self.assertEqual(result, "20,25")

    def test_weight_format_removes_trailing_zeros(self):
        """Test that trailing zeros are removed"""
        result = weight_format(Decimal("22.50"))
        self.assertEqual(result, "22,5")

    def test_weight_format_complex_decimal(self):
        """Test formatting complex decimals like 1.66"""
        result = weight_format(Decimal("1.66"))
        self.assertEqual(result, "1,66")

    def test_weight_format_none(self):
        """Test formatting None weight"""
        result = weight_format(None)
        self.assertEqual(result, "")

    def test_weight_format_string(self):
        """Test formatting string weight (fallback)"""
        result = weight_format("25")
        self.assertEqual(result, "25")
