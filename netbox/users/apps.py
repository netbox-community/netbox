from django.apps import AppConfig


class UsersConfig(AppConfig):
    name = 'users'

    def ready(self):
        from netbox.models.features import register_models
        from . import signals

        # Register models
        register_models(*self.get_models())
