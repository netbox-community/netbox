from django.conf import settings
from django.utils.module_loading import import_string
from urllib.parse import urlparse

__all__ = (
    'DefaultProxyRouter',
    'resolve_proxies',
)


class DefaultProxyRouter:
    """
    Base class for a proxy router.
    """
    @staticmethod
    def _get_protocol_from_url(url):
        """
        Determine the applicable protocol (e.g. HTTP or HTTPS) from the given URL.
        """
        return urlparse(url).scheme

    def route(self, url=None, protocol=None, context=None):
        """
        Returns the appropriate proxy given a URL or protocol. Arbitrary context data may also be passed where
        available.

        Args:
            url: The specific request URL for which the proxy will be used (if known)
            protocol: The protocol in use (e.g. http or https) (if known)
            context: Additional context to aid in proxy selection. May include e.g. the requesting client.
        """
        if url and protocol is None:
            protocol = self._get_protocol_from_url(url)
        if protocol and protocol in settings.HTTP_PROXIES:
            return {
                protocol: settings.HTTP_PROXIES[protocol]
            }
        return settings.HTTP_PROXIES


def resolve_proxies(url=None, protocol=None, context=None):
    """
    Return a dictionary of candidate proxies (compatible with the requests module), or None.

    Args:
        url: The specific request URL for which the proxy will be used (optional)
        protocol: The protocol in use (e.g. http or https) (optional)
        context: Arbitrary additional context to aid in proxy selection (optional)
    """
    context = context or {}

    for item in settings.PROXY_ROUTERS:
        router = import_string(item) if type(item) is str else item
        if proxies := router().route(url=url, protocol=protocol, context=context):
            return proxies
