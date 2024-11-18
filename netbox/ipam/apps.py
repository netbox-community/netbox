from django.apps import AppConfig

from netbox import denormalized


class IPAMConfig(AppConfig):
    name = "ipam"
    verbose_name = "IPAM"

    def ready(self):
        from netbox.models.features import register_models
        from . import signals, search  # noqa: F401
        from .models import Prefix

        # Register models
        register_models(*self.get_models())

        # Register denormalized fields
        denormalized.register(Prefix, '_site', {
            '_region': 'region',
            '_site_group': 'group',
        })
        denormalized.register(Prefix, '_location', {
            '_site': 'site',
        })
