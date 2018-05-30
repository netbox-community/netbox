from django.conf import settings
from django.core.exceptions import ImproperlyConfigured


default_app_config = 'extras.apps.ExtrasConfig'

# check that django-rq is installed and we can connect to redis
if settings.WEBHOOKS_ENABLED:
    try:
        import django_rq
    except ImportError:
        raise ImproperlyConfigured(
            "django-rq is not installed! You must install this package per "
            "the documentation to use the webhook backend."
        )
