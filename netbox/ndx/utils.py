from django.conf import settings

__all__ = (
    'get_web_url',
    'is_enabled',
)


def is_enabled():
    """
    Return True if the NDX integration has been configured and outbound requests are permitted.
    """
    return bool(settings.NDX_API_TOKEN) and not settings.ISOLATED_DEPLOYMENT


def get_web_url():
    """
    Return the base URL of the NDX web portal, derived from the configured API URL.
    """
    url = settings.NDX_API_URL.rstrip('/')
    return url.removesuffix('/api/v1')
