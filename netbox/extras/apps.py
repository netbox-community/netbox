from django.apps import AppConfig
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
import redis


class ExtrasConfig(AppConfig):
    name = "extras"

    def ready(self):
        import extras.signals
