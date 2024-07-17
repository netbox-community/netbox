import importlib
import importlib.util
import datetime
import requests

from dataclasses import dataclass, field
from django.conf import settings
from django.core.cache import cache
from django.utils.translation import gettext_lazy as _
from utilities.datetime import datetime_from_timestamp


@dataclass
class PluginVersion:
    date: datetime.datetime = None
    version: str = ''
    netbox_min_version: str = ''
    netbox_max_version: str = ''
    has_model: bool = False
    is_certified: bool = False
    is_feature: bool = False
    is_integration: bool = False
    is_netboxlabs_supported: bool = False


@dataclass
class Plugin:
    slug: str = ''
    config_name: str = ''
    name: str = ''
    title_long: str = ''
    tag_line: str = ''
    description_short: str = ''
    author: str = ''
    created: datetime.datetime = None
    updated: datetime.datetime = None
    is_local: bool = False
    is_installed: bool = False
    is_certified: bool = False
    is_community: bool = False
    versions: list[PluginVersion] = field(default_factory=list)


def get_local_plugins(plugins):
    for plugin_name in settings.PLUGINS:
        plugin = importlib.import_module(plugin_name)
        plugin_config: PluginConfig = plugin.config

        plugin_module = "{}.{}".format(plugin_config.__module__, plugin_config.__name__)  # type: ignore
        plugins[plugin_config.name] = Plugin(
            slug=plugin_config.name,
            name=plugin_config.verbose_name,
            tag_line=plugin_config.description,
            description_short=plugin_config.description,
            author=plugin_config.author or _('Unknown Author'),
            is_local=True,
            is_installed=True,
            is_certified=False,
            is_community=False,
        )

    return plugins


def get_catalog_plugins(plugins):
    url = 'https://api.netbox.oss.netboxlabs.com/v1/plugins'
    session = requests.Session()

    def get_pages():
        # TODO: pagintation is curently broken in API
        payload = {'page': '1', 'per_page': '50'}
        first_page = session.get(url, params=payload).json()
        yield first_page
        num_pages = first_page['metadata']['pagination']['last_page']

        for page in range(2, num_pages + 1):
            payload['page'] = page
            next_page = session.get(url, params=payload).json()
            yield next_page

    for page in get_pages():
        for data in page['data']:

            versions = []
            for version in data['release_recent_history']:
                versions.append(
                    PluginVersion(
                        date=datetime_from_timestamp(version['date']),
                        version=version['version'],
                        netbox_min_version=version['netbox_min_version'],
                        netbox_max_version=version['netbox_max_version'],
                        has_model=version['has_model'],
                        is_certified=version['is_certified'],
                        is_feature=version['is_feature'],
                        is_integration=version['is_integration'],
                        is_netboxlabs_supported=version['is_netboxlabs_supported'],
                    )
                )

            if data['slug'] in plugins:
                plugins[data['slug']].is_local = False
                plugins[data['slug']].is_certified = data['release_latest']['is_certified']
                plugins[data['slug']].description_short = data['description_short']
            else:
                plugins[data['slug']] = Plugin(
                    slug=data['slug'],
                    config_name=data['config_name'],
                    name=data['title_short'],
                    title_long=data['title_long'],
                    tag_line=data['tag_line'],
                    description_short=data['description_short'],
                    author=data['author']['name'] or _('Unknown Author'),
                    created=datetime_from_timestamp(data['created_at']),
                    updated=datetime_from_timestamp(data['updated_at']),
                    is_local=False,
                    is_installed=False,
                    is_certified=data['release_latest']['is_certified'],
                    is_community=not data['release_latest']['is_certified'],
                    versions=versions,
                )

    return plugins


def get_plugins():
    if plugins := cache.get('plugins-catalog-feed'):
        return plugins

    plugins = {}
    plugins = get_local_plugins(plugins)
    plugins = get_catalog_plugins(plugins)

    cache.set('plugins-catalog-feed', plugins, 3600)
    return plugins
