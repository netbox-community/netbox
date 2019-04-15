from django.conf import settings
from django.views.decorators.cache import cache_page


def cached(view):
    """
    Return a cache_page decorated view
    """
    return cache_page(settings.CACHE_TIMEOUT)(view)
