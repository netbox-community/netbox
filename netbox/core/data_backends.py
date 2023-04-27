import logging
import os
import re
import tempfile
from contextlib import contextmanager
from pathlib import Path
from urllib.parse import urlparse

import boto3
from botocore.config import Config as Boto3Config
from django import forms
from django.conf import settings
from django.utils.translation import gettext as _
from dulwich import porcelain
from dulwich.config import StackedConfig

from netbox.registry import registry
from .choices import DataSourceTypeChoices
from .exceptions import SyncError

__all__ = (
    'LocalBackend',
    'GitBackend',
    'S3Backend',
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

        username = self.params.get('username')
        password = self.params.get('password')
        branch = self.params.get('branch')
        config = StackedConfig.default()

        if settings.HTTP_PROXIES and self.url_scheme in ('http', 'https'):
            if proxy := settings.HTTP_PROXIES.get(self.url_scheme):
                config.set("http", "proxy", proxy)

        logger.debug(f"Cloning git repo: {self.url}")
        try:
            porcelain.clone(
                self.url, local_path.name, depth=1, branch=branch, username=username, password=password,
                config=config, quiet=True, errstream=porcelain.NoneStream()
            )
        except BaseException as e:
            raise SyncError(f"Fetching remote data failed ({type(e).__name__}): {e}")

        yield local_path.name

        local_path.cleanup()


@register_backend(DataSourceTypeChoices.AMAZON_S3)
class S3Backend(DataBackend):
    parameters = {
        'aws_access_key_id': forms.CharField(
            label=_('AWS access key ID'),
            widget=forms.TextInput(attrs={'class': 'form-control'})
        ),
        'aws_secret_access_key': forms.CharField(
            label=_('AWS secret access key'),
            widget=forms.TextInput(attrs={'class': 'form-control'})
        ),
    }

    REGION_REGEX = r's3\.([a-z0-9-]+)\.amazonaws\.com'

    @contextmanager
    def fetch(self):
        local_path = tempfile.TemporaryDirectory()

        # Build the S3 configuration
        s3_config = Boto3Config(
            proxies=settings.HTTP_PROXIES,
        )

        # Initialize the S3 resource and bucket
        aws_access_key_id = self.params.get('aws_access_key_id')
        aws_secret_access_key = self.params.get('aws_secret_access_key')
        s3 = boto3.resource(
            's3',
            region_name=self._region_name,
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            config=s3_config
        )
        bucket = s3.Bucket(self._bucket_name)

        # Download all files within the specified path
        for obj in bucket.objects.filter(Prefix=self._remote_path):
            local_filename = os.path.join(local_path.name, obj.key)
            # Build local path
            Path(os.path.dirname(local_filename)).mkdir(parents=True, exist_ok=True)
            bucket.download_file(obj.key, local_filename)

        yield local_path.name

        local_path.cleanup()

    @property
    def _region_name(self):
        domain = urlparse(self.url).netloc
        if m := re.match(self.REGION_REGEX, domain):
            return m.group(1)
        return None

    @property
    def _bucket_name(self):
        url_path = urlparse(self.url).path.lstrip('/')
        return url_path.split('/')[0]

    @property
    def _remote_path(self):
        url_path = urlparse(self.url).path.lstrip('/')
        if '/' in url_path:
            return url_path.split('/', 1)[1]
        return ''
