from django.apps import AppConfig
from django.conf import settings
from django.core.cache import cache
from django.db import models
from django.db.migrations.operations import AlterModelOptions
from django.utils.translation import gettext as _

from core.events import *
from netbox.events import EventType, EVENT_TYPE_KIND_DANGER, EVENT_TYPE_KIND_SUCCESS, EVENT_TYPE_KIND_WARNING
from utilities.migration import custom_deconstruct

# Ignore verbose_name & verbose_name_plural Meta options when calculating model migrations
AlterModelOptions.ALTER_OPTION_KEYS.remove('verbose_name')
AlterModelOptions.ALTER_OPTION_KEYS.remove('verbose_name_plural')

# Use our custom destructor to ignore certain attributes when calculating field migrations
models.Field.deconstruct = custom_deconstruct


class CoreConfig(AppConfig):
    name = "core"

    def ready(self):
        from core.api import schema  # noqa: F401
        from netbox.models.features import register_models
        from . import data_backends, events, search  # noqa: F401
        from netbox import context_managers  # noqa: F401

        # Register models
        register_models(*self.get_models())

        # Register core events
        EventType(OBJECT_CREATED, _('Object created')).register()
        EventType(OBJECT_UPDATED, _('Object updated')).register()
        EventType(OBJECT_DELETED, _('Object deleted'), destructive=True).register()
        EventType(JOB_STARTED, _('Job started')).register()
        EventType(JOB_COMPLETED, _('Job completed'), kind=EVENT_TYPE_KIND_SUCCESS).register()
        EventType(JOB_FAILED, _('Job failed'), kind=EVENT_TYPE_KIND_WARNING).register()
        EventType(JOB_ERRORED, _('Job errored'), kind=EVENT_TYPE_KIND_DANGER).register()

        # Clear Redis cache on startup in development mode
        if settings.DEBUG:
            try:
                cache.clear()
            except Exception:
                pass
