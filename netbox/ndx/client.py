import dataclasses
import logging
from urllib.parse import quote

import requests
from django.conf import settings
from django.core.cache import cache
from django.utils.translation import gettext_lazy as _

from utilities.proxy import resolve_proxies

from .constants import (
    CACHE_TIMEOUT,
    CATALOG_MAX_PAGE_SIZE,
    ERROR_CACHE_TIMEOUT,
    IMAGE_EXTENSIONS,
    IMAGE_MAX_SIZE,
    REQUEST_TIMEOUT,
)
from .utils import is_enabled

__all__ = (
    'DISABLED',
    'FORBIDDEN',
    'NOT_FOUND',
    'RATE_LIMITED',
    'UNAUTHORIZED',
    'UNAVAILABLE',
    'NDXClient',
    'NDXError',
    'NDXImage',
    'NDXResponse',
    'error_of',
    'get_client',
)

logger = logging.getLogger('netbox.ndx.client')

# Reasons an NDX API request may fail
UNAUTHORIZED = 'unauthorized'   # 401: Token missing or rejected
FORBIDDEN = 'forbidden'         # 403: Token valid but not entitled
NOT_FOUND = 'not_found'         # 404: Resource absent
RATE_LIMITED = 'rate_limited'   # 429: Token has exceeded its request limit
UNAVAILABLE = 'unavailable'     # 5xx, timeout, connection failure, or invalid JSON
DISABLED = 'disabled'           # The integration is not configured

ERROR_MESSAGES = {
    UNAUTHORIZED: (
        _('NDX API token rejected'),
        _('The NDX API rejected the configured token (HTTP 401). Check NDX_API_TOKEN in the NetBox configuration.'),
    ),
    FORBIDDEN: (
        _('NDX access not entitled'),
        _('The configured NDX API token is not entitled to this resource (HTTP 403).'),
    ),
    NOT_FOUND: (
        _('Not found in the NDX catalog'),
        _('This entry is not present in the NDX catalog.'),
    ),
    RATE_LIMITED: (
        _('NDX API rate limit reached'),
        _('The configured token has exceeded its NDX API request limit (HTTP 429). Try again in a few minutes.'),
    ),
    UNAVAILABLE: (
        _('NDX API unreachable'),
        _('NetBox could not reach the NDX API. Data shown may be stale or incomplete.'),
    ),
    DISABLED: (
        _('NDX integration disabled'),
        _('The NDX integration is not enabled. Set NDX_API_TOKEN in the NetBox configuration to enable it.'),
    ),
}

HTTP_STATUS_ERRORS = {
    401: UNAUTHORIZED,
    403: FORBIDDEN,
    404: NOT_FOUND,
    429: RATE_LIMITED,
}


@dataclasses.dataclass(frozen=True)
class NDXError:
    """
    The reason an NDX API request did not return data.
    """
    kind: str
    status: int | None = None
    detail: str = ''

    @property
    def title(self):
        return ERROR_MESSAGES.get(self.kind, ERROR_MESSAGES[UNAVAILABLE])[0]

    @property
    def message(self):
        return ERROR_MESSAGES.get(self.kind, ERROR_MESSAGES[UNAVAILABLE])[1]

    @property
    def is_auth(self):
        return self.kind in (UNAUTHORIZED, FORBIDDEN)


class NDXResponse(dict):
    """
    A JSON payload from the NDX API. A failed request yields an empty (falsy) response carrying an NDXError.
    """
    __slots__ = ('error',)

    def __init__(self, data=None, error=None):
        super().__init__(data or {})
        self.error = error


@dataclasses.dataclass(frozen=True)
class NDXImage:
    """
    An image retrieved from the NDX API.
    """
    content: bytes
    extension: str


def quote_segments(*values):
    """
    Return the given values encoded as URL path segments, or None if any is empty or a relative path reference.
    """
    values = [str(value or '') for value in values]
    if any(value in ('', '.', '..') or '/' in value for value in values):
        return None
    return '/'.join(quote(value, safe='') for value in values)


def error_of(response):
    """
    Return the NDXError carried by a client response, if any.
    """
    return response.error if isinstance(response, NDXResponse) else None


class NDXClient:
    """
    A client for the NetBox Data Exchange (NDX) catalog API.
    """
    def __init__(self, api_url=None, token=None):
        self.api_url = (api_url or settings.NDX_API_URL).rstrip('/')
        self.token = token if token is not None else settings.NDX_API_TOKEN

    @property
    def headers(self):
        headers = {
            'Accept': 'application/json',
            'User-Agent': f'NetBox/{settings.RELEASE.version} {settings.RELEASE.edition}',
        }
        if self.token:
            headers['Authorization'] = f'Bearer {self.token}'
        return headers

    def _get(self, url, params=None, stream=False):
        return requests.get(
            url,
            headers=self.headers,
            params=params,
            proxies=resolve_proxies(url=url),
            timeout=REQUEST_TIMEOUT,
            stream=stream,
        )

    def _fetch_json(self, path, params=None, use_cache=True):
        """
        Fetch a JSON resource from the NDX API. Always returns an NDXResponse; never raises.
        """
        if not is_enabled():
            return NDXResponse(error=NDXError(kind=DISABLED))

        cache_key = f'ndx:{path}:{params}'
        error_key = f'ndx:error:{path}:{params}'
        if use_cache:
            if (data := cache.get(cache_key)) is not None:
                return NDXResponse(data)
            if (error := cache.get(error_key)) is not None:
                return NDXResponse(error=error)

        url = f'{self.api_url}/{path}'
        try:
            response = self._get(url, params=params)
            response.raise_for_status()
            data = response.json()
            if not isinstance(data, dict):
                raise ValueError(f"Expected a JSON object; received {type(data).__name__}")
        except (requests.RequestException, ValueError) as e:
            logger.error(f"NDX API error fetching {url}: {e}")
            status = getattr(getattr(e, 'response', None), 'status_code', None)
            error = NDXError(kind=HTTP_STATUS_ERRORS.get(status, UNAVAILABLE), status=status, detail=str(e))
            if use_cache:
                cache.set(error_key, error, ERROR_CACHE_TIMEOUT)
            return NDXResponse(error=error)

        if use_cache:
            cache.set(cache_key, data, CACHE_TIMEOUT)
        return NDXResponse(data)

    def _fetch_image(self, path):
        """
        Fetch an image from the NDX API. Returns None if the request fails, or if the response is not an accepted
        image type or exceeds the maximum size.
        """
        if not is_enabled():
            return None

        url = f'{self.api_url}/{path}'
        try:
            with self._get(url, stream=True) as response:
                response.raise_for_status()
                content_type = response.headers.get('Content-Type', '').split(';')[0].strip().lower()
                if content_type not in IMAGE_EXTENSIONS:
                    logger.error(f"NDX API returned an unsupported content type ({content_type!r}) for {url}")
                    return None
                content = bytearray()
                for chunk in response.iter_content(chunk_size=65536):
                    content.extend(chunk)
                    if len(content) > IMAGE_MAX_SIZE:
                        logger.error(f"NDX API image at {url} exceeds the maximum size of {IMAGE_MAX_SIZE} bytes")
                        return None
        except requests.RequestException as e:
            status = getattr(getattr(e, 'response', None), 'status_code', None)
            log = logger.debug if status == 404 else logger.error
            log(f"NDX API error fetching {url}: {e}")
            return None
        return NDXImage(content=bytes(content), extension=IMAGE_EXTENSIONS[content_type])

    #
    # API methods
    #

    def verify_auth(self, use_cache=False):
        """
        Validate the configured token and return its entitlement tier.
        """
        response = self._fetch_json('auth/verify', use_cache=use_cache)
        if response and not response.get('authenticated', True):
            return NDXResponse(error=NDXError(kind=UNAUTHORIZED))
        return response

    def get_vendors(self, cursor=None, limit=CATALOG_MAX_PAGE_SIZE):
        """
        Return a page of catalog vendors.
        """
        params = {'limit': limit}
        if cursor:
            params['cursor'] = cursor
        return self._fetch_json('vendors', params=params)

    def get_all_vendors(self, max_pages=10):
        """
        Return all catalog vendors, following pagination cursors (up to max_pages requests).
        """
        vendors = []
        cursor = None
        for __ in range(max_pages):
            response = self.get_vendors(cursor=cursor)
            vendors.extend(response.get('results') or [])
            if not (cursor := response.get('next_cursor')):
                break
        return vendors

    def search(self, q=None, vendor=None, entry_type=None, cursor=None, offset=None, limit=50, **filters):
        """
        Search the catalog. Device, module, and rack types are all served from the device-types endpoint.
        """
        params = {'limit': min(limit, CATALOG_MAX_PAGE_SIZE)}
        if q:
            params['q'] = q
        if vendor:
            params['vendor'] = vendor
        if entry_type:
            params['type'] = entry_type
        if cursor:
            params['cursor'] = cursor
        if offset is not None:
            params['offset'] = offset
        for key, value in filters.items():
            if value is not None:
                params[key] = value
        return self._fetch_json('device-types', params=params)

    def get_entry(self, vendor_slug, slug):
        """
        Return the full detail of a catalog entry. Enrichment data is included according to the token's tier.
        """
        if (path := quote_segments(vendor_slug, slug)) is None:
            return NDXResponse(error=NDXError(kind=NOT_FOUND))
        return self._fetch_json(f'device-types/{path}', use_cache=False)

    def get_image(self, vendor_slug, slug, face):
        """
        Return the front or rear elevation image for a catalog entry as an NDXImage, or None.
        """
        if (path := quote_segments(vendor_slug, slug)) is None:
            return None
        return self._fetch_image(f'device-types/{path}/image/{face}')

    def check_sync(self, since=None):
        """
        Check for catalog changes since the given timestamp.
        """
        params = {'since': since} if since else {}
        return self._fetch_json('sync/check', params=params, use_cache=False)

    def get_manifest(self):
        """
        Return the catalog manifest, including per-vendor checksums.
        """
        return self._fetch_json('sync/manifest', use_cache=False)


def get_client():
    """
    Return an NDXClient for the configured API.
    """
    return NDXClient()
