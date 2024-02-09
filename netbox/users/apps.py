from django.apps import AppConfig


class UsersConfig(AppConfig):
    name = 'users'

    def ready(self):
        import users.signals
        from .models import NetBoxGroup, ObjectPermission, Token, User, UserConfig
        from netbox.models.features import _register_features

        # have to register these manually as the signal handler for class_prepared does
        # not get registered until after these models are loaded. Any models defined in
        # users.models should be registered here.
        _register_features(NetBoxGroup)
        _register_features(ObjectPermission)
        _register_features(Token)
        _register_features(User)
        _register_features(UserConfig)
