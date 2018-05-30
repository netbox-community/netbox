from __future__ import unicode_literals

from django.apps import AppConfig
from django.core.cache import caches
from django.db.utils import ProgrammingError
from django.core.exceptions import ImproperlyConfigured
from django.conf import settings


class ExtrasConfig(AppConfig):
    name = "extras"

    def ready(self):
        import extras.signals

        # check that we can connect to redis
        if settings.WEBHOOK_BACKEND_ENABLED:
            try:
                import redis
                rs = redis.Redis(settings.REDIS_HOST,
                                 settings.REDIS_PORT,
                                 settings.REDIS_DB,
                                 settings.REDIS_PASSWORD or None)
                rs.ping()
            except redis.exceptions.ConnectionError:
                raise ImproperlyConfigured(
                    "Unable to connect to the redis database. You must provide "
                    "connection settings to redis per the documentation."
                )
