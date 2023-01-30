import logging
import subprocess
import tempfile
from contextlib import contextmanager
from urllib.parse import quote, urlunparse, urlparse

from django.conf import settings

from .exceptions import SyncError

__all__ = (
    'LocalBakend',
    'GitBackend',
)

logger = logging.getLogger('netbox.data_backends')


class DataBackend:

    def __init__(self, url, **kwargs):
        self.url = url
        self.params = kwargs

    @property
    def url_scheme(self):
        return urlparse(self.url).scheme.lower()

    @contextmanager
    def fetch(self):
        raise NotImplemented()


class LocalBakend(DataBackend):

    @contextmanager
    def fetch(self):
        logger.debug(f"Data source type is local; skipping fetch")
        local_path = urlparse(self.url).path  # Strip file:// scheme

        yield local_path


class GitBackend(DataBackend):

    @contextmanager
    def fetch(self):
        local_path = tempfile.TemporaryDirectory()

        # Add authentication credentials to URL (if specified)
        username = self.params.get('username')
        password = self.params.get('password')
        if username and password:
            url_components = list(urlparse(self.url))
            # Prepend username & password to netloc
            url_components[1] = quote(f'{username}@{password}:') + url_components[1]
            url = urlunparse(url_components)
        else:
            url = self.url

        # Compile git arguments
        args = ['git', 'clone', '--depth', '1']
        if branch := self.params.get('branch'):
            args.extend(['--branch', branch])
        args.extend([url, local_path.name])

        # Prep environment variables
        env_vars = {}
        if settings.HTTP_PROXIES and self.url_scheme in ('http', 'https'):
            env_vars['http_proxy'] = settings.HTTP_PROXIES.get(self.url_scheme)

        logger.debug(f"Cloning git repo: {' '.join(args)}")
        try:
            subprocess.run(args, check=True, capture_output=True, env=env_vars)
        except subprocess.CalledProcessError as e:
            raise SyncError(
                f"Fetching remote data failed: {e.stderr}"
            )

        yield local_path.name

        local_path.cleanup()
