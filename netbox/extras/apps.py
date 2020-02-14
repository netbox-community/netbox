from django.apps import AppConfig
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
import redis


class ExtrasConfig(AppConfig):
    name = "extras"

    def ready(self):

        import extras.signals

        # Check that we can connect to the configured Redis database.
        try:
            if settings.WEBHOOKS_REDIS_USING_SENTINEL:
                sentinel = redis.sentinel.Sentinel(
                    settings.WEBHOOKS_REDIS_SENTINELS,
                    socket_timeout=settings.WEBHOOKS_REDIS_DEFAULT_TIMEOUT
                )
                rs = sentinel.master_for(
                    settings.WEBHOOKS_REDIS_SENTINEL_SERVICE,
                    socket_timeout=settings.WEBHOOKS_REDIS_DEFAULT_TIMEOUT
                )
            else:
                rs = redis.Redis(
                    host=settings.WEBHOOKS_REDIS_HOST,
                    port=settings.WEBHOOKS_REDIS_PORT,
                    db=settings.WEBHOOKS_REDIS_DATABASE,
                    password=settings.WEBHOOKS_REDIS_PASSWORD or None,
                    ssl=settings.WEBHOOKS_REDIS_SSL,
                )
            rs.ping()
        except redis.exceptions.ConnectionError:
            raise ImproperlyConfigured(
                "Unable to connect to the Redis database. Check that the Redis configuration has been defined in "
                "configuration.py."
            )
