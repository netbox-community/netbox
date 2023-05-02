from django.apps import AppConfig


class CoreConfig(AppConfig):
    name = "core"

    def ready(self):
        from . import data_backends, search
        from core.api import schema  # noqa: E402
