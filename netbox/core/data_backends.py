import logging
import os
import re
import tempfile
from contextlib import contextmanager
from pathlib import Path
from urllib.parse import urlparse

from django import forms
from django.conf import settings
from django.utils.translation import gettext as _

from netbox.data_backends import DataBackend
from netbox.utils import register_data_backend
from .exceptions import SyncError

__all__ = (
    'GitBackend',
    'LocalBackend',
    'S3Backend',
)

logger = logging.getLogger('netbox.data_backends')


@register_data_backend()
class LocalBackend(DataBackend):
    name = 'local'
    label = _('Local')
    is_local = True

    @contextmanager
    def fetch(self):
        logger.debug(f"Data source type is local; skipping fetch")
        local_path = urlparse(self.url).path  # Strip file:// scheme

        yield local_path


@register_data_backend()
class GitBackend(DataBackend):
    name = 'git'
    label = 'Git'
    parameters = {
        'username': forms.CharField(
            required=False,
            label=_('Username'),
            widget=forms.TextInput(attrs={'class': 'form-control'}),
            help_text=_("Only used for cloning with HTTP(S)"),
        ),
        'password': forms.CharField(
            required=False,
            label=_('Password'),
            widget=forms.TextInput(attrs={'class': 'form-control'}),
            help_text=_("Only used for cloning with HTTP(S)"),
        ),
        'branch': forms.CharField(
            required=False,
            label=_('Branch'),
            widget=forms.TextInput(attrs={'class': 'form-control'})
        )
    }
    sensitive_parameters = ['password']

    def init_config(self):
        from dulwich.config import ConfigDict

        # Initialize backend config
        config = ConfigDict()

        # Apply HTTP proxy (if configured)
        if settings.HTTP_PROXIES and self.url_scheme in ('http', 'https'):
            if proxy := settings.HTTP_PROXIES.get(self.url_scheme):
                config.set("http", "proxy", proxy)

        return config

    @contextmanager
    def fetch(self):
        from dulwich import porcelain

        local_path = tempfile.TemporaryDirectory()

        clone_args = {
            "branch": self.params.get('branch'),
            "config": self.config,
            "errstream": porcelain.NoneStream(),
        }

        if self.url_scheme in ('http', 'https'):
            if self.params.get('username'):
                clone_args.update(
                    {
                        "username": self.params.get('username'),
                        "password": self.params.get('password'),
                    }
                )
        if self.url_scheme:
            clone_args["quiet"] = True
            clone_args["depth"] = 1

        logger.debug(f"Cloning git repo: {self.url}")
        try:
            porcelain.clone(self.url, local_path.name, **clone_args)
        except BaseException as e:
            raise SyncError(_("Fetching remote data failed ({name}): {error}").format(name=type(e).__name__, error=e))

        yield local_path.name

        local_path.cleanup()


@register_data_backend()
class S3Backend(DataBackend):
    name = 'amazon-s3'
    label = 'Amazon S3'
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
    sensitive_parameters = ['aws_secret_access_key']

    REGION_REGEX = r's3\.([a-z0-9-]+)\.amazonaws\.com'

    def init_config(self):
        from botocore.config import Config as Boto3Config

        # Initialize backend config
        return Boto3Config(
            proxies=settings.HTTP_PROXIES,
        )

    @contextmanager
    def fetch(self):
        import boto3

        local_path = tempfile.TemporaryDirectory()

        # Initialize the S3 resource and bucket
        aws_access_key_id = self.params.get('aws_access_key_id')
        aws_secret_access_key = self.params.get('aws_secret_access_key')
        s3 = boto3.resource(
            's3',
            region_name=self._region_name,
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            config=self.config,
            endpoint_url=self._endpoint_url
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
    def _endpoint_url(self):
        url_path = urlparse(self.url)
        return url_path._replace(params="", fragment="", query="", path="").geturl()

    @property
    def _remote_path(self):
        url_path = urlparse(self.url).path.lstrip('/')
        if '/' in url_path:
            return url_path.split('/', 1)[1]
        return ''
