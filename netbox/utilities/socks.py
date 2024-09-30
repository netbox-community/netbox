from urllib.parse import urlparse
from urllib3 import PoolManager, HTTPConnectionPool, HTTPSConnectionPool
from urllib3.connection import HTTPConnection, HTTPSConnection


# These Proxy Methods are for handling SOCKS connection proxy
class ProxyHTTPConnection(HTTPConnection):
    use_rdns = False

    def __init__(self, *args, **kwargs):
        socks_options = kwargs.pop('_socks_options')
        self._proxy_url = socks_options['proxy_url']
        super().__init__(*args, **kwargs)

    def _new_conn(self):
        from python_socks.sync import Proxy
        proxy = Proxy.from_url(self._proxy_url, rdns=self.use_rdns)
        return proxy.connect(
            dest_host=self.host,
            dest_port=self.port,
            timeout=self.timeout
        )


class ProxyHTTPSConnection(ProxyHTTPConnection, HTTPSConnection):
    pass


class RdnsProxyHTTPConnection(ProxyHTTPConnection):
    use_rdns = True


class RdnsProxyHTTPSConnection(ProxyHTTPSConnection):
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
        cleaned_proxy_url = proxy_url
        if use_rdns := urlparse(cleaned_proxy_url).scheme in ['socks4h', 'socks4a' 'socks5h', 'socks5a']:
            cleaned_proxy_url = cleaned_proxy_url.replace('socks5h:', 'socks5:').replace('socks5a:', 'socks5:')
            cleaned_proxy_url = cleaned_proxy_url.replace('socks4h:', 'socks4:').replace('socks4a:', 'socks4:')

        connection_pool_kw['_socks_options'] = {'proxy_url': cleaned_proxy_url}
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
