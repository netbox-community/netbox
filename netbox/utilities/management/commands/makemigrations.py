# noinspection PyUnresolvedReferences
from django.conf import settings
from django.core.management.base import CommandError
from django.core.management.commands.makemigrations import Command as _Command
from django.db import models

from . import custom_deconstruct

models.Field.deconstruct = custom_deconstruct


class Command(_Command):

    def handle(self, *args, **kwargs):
        """
        This built-in management command enables the creation of new database schema migration files, which should
        never be required by and ordinary user. We prevent this command from executing unless the configuration
        indicates that the user is a developer (i.e. configuration.DEVELOPER == True).
        """
        if not settings.DEVELOPER:
            raise CommandError(
                "This command is available for development purposes only. It will\n"
                "NOT resolve any issues with missing or unapplied migrations. For assistance,\n"
                "please post to the NetBox mailing list:\n"
                "    https://groups.google.com/g/netbox-discuss"
            )

        super().handle(*args, **kwargs)
