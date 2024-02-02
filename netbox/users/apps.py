from django.apps import AppConfig


class UsersConfig(AppConfig):
    name = 'users'

    def ready(self):
        import users.signals
        from .models import NetBoxGroup, ObjectPermission, Token, User, UserConfig
        from netbox.models.features import _register_features

        _register_features(NetBoxGroup)
        _register_features(ObjectPermission)
        _register_features(Token)
        _register_features(User)
        _register_features(UserConfig)
