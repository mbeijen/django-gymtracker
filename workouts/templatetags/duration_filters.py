from django import template
from datetime import timedelta
from decimal import Decimal

register = template.Library()


@register.filter
def duration_format(duration):
    """
    Format a timedelta object as H:MM (e.g., 2:37)
    """
    if not duration:
        return ""

    if isinstance(duration, timedelta):
        total_seconds = int(duration.total_seconds())
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60

        if hours > 0:
            return f"{hours}:{minutes:02d}"
        else:
            return f"{minutes}m"

    return str(duration)


@register.filter
def weight_format(weight):
    """
    Format a weight value to show whole numbers by default,
    and only show decimals when meaningful (e.g., 2,5 instead of 2,50)
    """
    if not weight:
        return ""

    if isinstance(weight, (int, float, Decimal)):
        # Convert to Decimal for precise handling
        weight_decimal = Decimal(str(weight))

        # If it's a whole number, show without decimals
        if weight_decimal == weight_decimal.quantize(Decimal("1")):
            return str(int(weight_decimal))

        # If it has meaningful decimals, show them (but remove trailing zeros)
        # This handles cases like 2.50 -> 2,5 and 1.66 -> 1,66
        formatted = f"{weight_decimal:.2f}".rstrip("0").rstrip(".")
        # Replace decimal point with comma for Dutch formatting
        return formatted.replace(".", ",")

    return str(weight)
