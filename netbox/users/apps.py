from django.apps import AppConfig


class UsersConfig(AppConfig):
    name = 'users'

    def ready(self):
        from netbox.models.features import register_model
        from . import signals

        # Register models
        for model in self.get_models():
            register_model(model)
