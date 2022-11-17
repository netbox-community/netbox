from django.apps import AppConfig


class HomeConfig(AppConfig):
    name = 'users'

    def ready(self):
        import users.signals
