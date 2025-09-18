#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""

import os
import sys


def main():
    """Run administrative tasks."""
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "gymtracker.settings")
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc

    # Set default port to 8098 for runserver command
    if len(sys.argv) == 1 or (len(sys.argv) > 1 and sys.argv[1] == "runserver"):
        # If no port is specified, use 8098 as default
        if len(sys.argv) == 2:  # Only 'runserver' command, no port specified
            sys.argv.append("127.0.0.1:8098")
        elif (
            len(sys.argv) == 2 and ":" not in sys.argv[1]
        ):  # 'runserver' with port but no IP
            sys.argv[1] = f"127.0.0.1:{sys.argv[1]}"

    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
