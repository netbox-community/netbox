import logging
import subprocess
import tempfile
from contextlib import contextmanager
from urllib.parse import quote, urlunparse, urlparse

from django import forms
from django.conf import settings
from django.utils.translation import gettext as _

from netbox.registry import registry
from .choices import DataSourceTypeChoices
from .exceptions import SyncError

__all__ = (
    'LocalBackend',
    'GitBackend',
)

logger = logging.getLogger('netbox.data_backends')


def register_backend(name):
    """
    Decorator for registering a DataBackend class.
    """
    def _wrapper(cls):
        registry['data_backends'][name] = cls
        return cls

    return _wrapper


class DataBackend:
    parameters = {}

    def __init__(self, url, **kwargs):
        self.url = url
        self.params = kwargs

    @property
    def url_scheme(self):
        return urlparse(self.url).scheme.lower()

    @contextmanager
    def fetch(self):
        raise NotImplemented()


@register_backend(DataSourceTypeChoices.LOCAL)
class LocalBackend(DataBackend):

    @contextmanager
    def fetch(self):
        logger.debug(f"Data source type is local; skipping fetch")
        local_path = urlparse(self.url).path  # Strip file:// scheme

        yield local_path


@register_backend(DataSourceTypeChoices.GIT)
class GitBackend(DataBackend):
    parameters = {
        'username': forms.CharField(
            required=False,
            label=_('Username'),
            widget=forms.TextInput(attrs={'class': 'form-control'})
        ),
        'password': forms.CharField(
            required=False,
            label=_('Password'),
            widget=forms.TextInput(attrs={'class': 'form-control'})
        ),
        'branch': forms.CharField(
            required=False,
            label=_('Branch'),
            widget=forms.TextInput(attrs={'class': 'form-control'})
        )
    }

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
