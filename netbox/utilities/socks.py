import logging

from urllib.parse import urlparse
from urllib3 import PoolManager, HTTPConnectionPool, HTTPSConnectionPool
from urllib3.connection import HTTPConnection, HTTPSConnection
from .constants import HTTP_PROXY_SOCK_RDNS_SCHEMAS


logger = logging.getLogger('netbox.utilities')


class ProxyHTTPConnection(HTTPConnection):
    """
    A Proxy connection class that uses a SOCK proxy - used to create
    a urllib3 PoolManager that routes connections via the proxy.
    This is for an HTTP (not HTTPS) connection
    """
    use_rdns = False

    def __init__(self, *args, **kwargs):
        socks_options = kwargs.pop('_socks_options')
        self._proxy_url = socks_options['proxy_url']
        super().__init__(*args, **kwargs)

    def _new_conn(self):
        try:
            from python_socks.sync import Proxy
        except ModuleNotFoundError as e:
            logger.info("Configuring an HTTP proxy using SOCKS requires the python_socks library. Check that it has been installed.")
            raise e

        proxy = Proxy.from_url(self._proxy_url, rdns=self.use_rdns)
        return proxy.connect(
            dest_host=self.host,
            dest_port=self.port,
            timeout=self.timeout
        )


class ProxyHTTPSConnection(ProxyHTTPConnection, HTTPSConnection):
    """
    A Proxy connection class for an HTTPS (not HTTP) connection.
    """
    pass


class RdnsProxyHTTPConnection(ProxyHTTPConnection):
    """
    A Proxy connection class for an HTTP remote-dns connection.
    I.E. socks4a, socks4h, socks5a, socks5h
    """
    use_rdns = True


class RdnsProxyHTTPSConnection(ProxyHTTPSConnection):
    """
    A Proxy connection class for an HTTPS remote-dns connection.
    I.E. socks4a, socks4h, socks5a, socks5h
    """
    use_rdns = True


class ProxyHTTPConnectionPool(HTTPConnectionPool):
    ConnectionCls = ProxyHTTPConnection


class ProxyHTTPSConnectionPool(HTTPSConnectionPool):
    ConnectionCls = ProxyHTTPSConnection


class RdnsProxyHTTPConnectionPool(HTTPConnectionPool):
    ConnectionCls = RdnsProxyHTTPConnection


class RdnsProxyHTTPSConnectionPool(HTTPSConnectionPool):
    ConnectionCls = RdnsProxyHTTPSConnection


class ProxyPoolManager(PoolManager):
    def __init__(self, proxy_url, timeout=5, num_pools=10, headers=None, **connection_pool_kw):
        # python_socks uses rdns param to denote remote DNS parsing and
        # doesn't accept the 'h' or 'a' in the proxy URL
        if use_rdns := urlparse(proxy_url).scheme in HTTP_PROXY_SOCK_RDNS_SCHEMAS:
            proxy_url = proxy_url.replace('socks5h:', 'socks5:').replace('socks5a:', 'socks5:')
            proxy_url = proxy_url.replace('socks4h:', 'socks4:').replace('socks4a:', 'socks4:')

        connection_pool_kw['_socks_options'] = {'proxy_url': proxy_url}
        connection_pool_kw['timeout'] = timeout

        super().__init__(num_pools, headers, **connection_pool_kw)

        if use_rdns:
            self.pool_classes_by_scheme = {
                'http': RdnsProxyHTTPConnectionPool,
                'https': RdnsProxyHTTPSConnectionPool,
            }
        else:
            self.pool_classes_by_scheme = {
                'http': ProxyHTTPConnectionPool,
                'https': ProxyHTTPSConnectionPool,
            }
