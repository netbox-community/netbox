from django.apps import AppConfig


class NDXConfig(AppConfig):
    name = 'ndx'
    verbose_name = 'NetBox Data Exchange'

    def ready(self):
        from netbox.models.features import register_models

        from . import checks, jobs, search  # noqa: F401
        from .importers import register_core_importers

        # Register models
        register_models(*self.get_models())

        # Register the importers for core object types
        register_core_importers()

        # Schedule the periodic catalog sync
        jobs.register_sync_job()
