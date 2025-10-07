from django import template
from datetime import timedelta

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
