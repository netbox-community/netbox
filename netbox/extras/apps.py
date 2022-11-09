from django.apps import AppConfig


class ExtrasConfig(AppConfig):
    name = "extras"

    def ready(self):
        from . import lookups, search, signals
