from django.apps import AppConfig
from django.db import models
from django.db.migrations.operations import AlterModelOptions

from utilities.migration import custom_deconstruct

# Ignore verbose_name & verbose_name_plural Meta options when calculating model migrations
AlterModelOptions.ALTER_OPTION_KEYS.remove('verbose_name')
AlterModelOptions.ALTER_OPTION_KEYS.remove('verbose_name_plural')

# Use our custom destructor to ignore certain attributes when calculating field migrations
models.Field.deconstruct = custom_deconstruct


class CoreConfig(AppConfig):
    name = "core"

    def ready(self):
        from core.api import schema  # noqa
        from netbox.models.features import register_models
        from . import data_backends, events, search

        # Register models
        register_models(*self.get_models())
