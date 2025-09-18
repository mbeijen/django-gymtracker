from django.core.management.commands.runserver import Command as BaseCommand


class Command(BaseCommand):
    """Custom runserver command that defaults to port 8098"""

    def add_arguments(self, parser):
        super().add_arguments(parser)
        # Override the default port
        parser.set_defaults(addrport="127.0.0.1:8098")
