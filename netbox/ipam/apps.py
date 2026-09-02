from django.apps import AppConfig


class IPAMConfig(AppConfig):
    name = "ipam"
    verbose_name = "IPAM"

    def ready(self):
        from netbox.models.features import register_models

        from . import search, signals  # noqa: F401

        # Register models
        register_models(*self.get_models())
