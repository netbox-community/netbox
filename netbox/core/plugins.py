import datetime
import importlib
import importlib.util
from dataclasses import dataclass, field
from typing import Optional

import requests
from django.conf import settings
from django.core.cache import cache

from netbox.plugins import PluginConfig
from utilities.datetime import datetime_from_timestamp

USER_AGENT_STRING = f'NetBox/{settings.RELEASE.version} {settings.RELEASE.edition}'
CACHE_KEY_CATALOG_FEED = 'plugins-catalog-feed'


@dataclass
class PluginAuthor:
    """
    Identifying information for the author of a plugin.
    """
    name: str
    org_id: str = ''
    url: str = ''


@dataclass
class PluginVersion:
    """
    Details for a specific versioned release of a plugin.
    """
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
    """
    The representation of a NetBox plugin in the catalog API.
    """
    id: str = ''
    icon_url: str = ''
    status: str = ''
    title_short: str = ''
    title_long: str = ''
    tag_line: str = ''
    description_short: str = ''
    slug: str = ''
    author: Optional[PluginAuthor] = None
    created_at: datetime.datetime = None
    updated_at: datetime.datetime = None
    license_type: str = ''
    homepage_url: str = ''
    package_name_pypi: str = ''
    config_name: str = ''
    is_certified: bool = False
    release_latest: PluginVersion = field(default_factory=PluginVersion)
    release_recent_history: list[PluginVersion] = field(default_factory=list)
    is_local: bool = False  # extra field for locally installed plugins
    is_installed: bool = False
    installed_version: str = ''


def get_local_plugins(plugins=None):
    """
    Return a dictionary of all locally-installed plugins, mapped by name.
    """
    plugins = plugins or {}
    local_plugins = {}

    # Gather all locally-installed plugins
    for plugin_name in settings.PLUGINS:
        plugin = importlib.import_module(plugin_name)
        plugin_config: PluginConfig = plugin.config

        if plugin_config.author:
            author = PluginAuthor(
                name=plugin_config.author,
            )
        else:
            author = None

        local_plugins[plugin_config.name] = Plugin(
            config_name=plugin_config.name,
            title_short=plugin_config.verbose_name,
            title_long=plugin_config.verbose_name,
            tag_line=plugin_config.description,
            description_short=plugin_config.description,
            is_local=True,
            is_installed=True,
            author=author,
            installed_version=plugin_config.version,
        )

    # Update catalog entries for local plugins, or add them to the list if not listed
    for k, v in local_plugins.items():
        if k in plugins:
            plugins[k].is_local = True
            plugins[k].is_installed = True
            plugins[k].installed_version = v.installed_version
        else:
            plugins[k] = v

    return plugins


def get_catalog_plugins():
    """
    Return a dictionary of all entries in the plugins catalog, mapped by name.
    """
    session = requests.Session()

    # Disable catalog fetching for isolated deployments
    if settings.ISOLATED_DEPLOYMENT:
        return {}

    def get_pages():
        # TODO: pagination is currently broken in API
        payload = {'page': '1', 'per_page': '50'}
        first_page = session.get(
            settings.PLUGIN_CATALOG_URL,
            headers={'User-Agent': USER_AGENT_STRING},
            proxies=settings.HTTP_PROXIES,
            timeout=3,
            params=payload
        ).json()
        yield first_page
        num_pages = first_page['metadata']['pagination']['last_page']

        for page in range(2, num_pages + 1):
            payload['page'] = page
            next_page = session.get(
                settings.PLUGIN_CATALOG_URL,
                headers={'User-Agent': USER_AGENT_STRING},
                proxies=settings.HTTP_PROXIES,
                timeout=3,
                params=payload
            ).json()
            yield next_page

    def make_plugin_dict():
        plugins = {}

        for page in get_pages():
            for data in page['data']:

                # Populate releases
                releases = []
                for version in data['release_recent_history']:
                    releases.append(
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
                releases = sorted(releases, key=lambda x: x.date, reverse=True)
                latest_release = PluginVersion(
                    date=datetime_from_timestamp(data['release_latest']['date']),
                    version=data['release_latest']['version'],
                    netbox_min_version=data['release_latest']['netbox_min_version'],
                    netbox_max_version=data['release_latest']['netbox_max_version'],
                    has_model=data['release_latest']['has_model'],
                    is_certified=data['release_latest']['is_certified'],
                    is_feature=data['release_latest']['is_feature'],
                    is_integration=data['release_latest']['is_integration'],
                    is_netboxlabs_supported=data['release_latest']['is_netboxlabs_supported'],
                )

                # Populate author (if any)
                if data['author']:
                    author = PluginAuthor(
                        name=data['author']['name'],
                        org_id=data['author']['org_id'],
                        url=data['author']['url'],
                    )
                else:
                    author = None

                # Populate plugin data
                plugins[data['config_name']] = Plugin(
                    id=data['id'],
                    icon_url=data['icon'],
                    status=data['status'],
                    title_short=data['title_short'],
                    title_long=data['title_long'],
                    tag_line=data['tag_line'],
                    description_short=data['description_short'],
                    slug=data['slug'],
                    author=author,
                    created_at=datetime_from_timestamp(data['created_at']),
                    updated_at=datetime_from_timestamp(data['updated_at']),
                    license_type=data['license_type'],
                    homepage_url=data['homepage_url'],
                    package_name_pypi=data['package_name_pypi'],
                    config_name=data['config_name'],
                    is_certified=data['is_certified'],
                    release_latest=latest_release,
                    release_recent_history=releases,
                )

        return plugins

    catalog_plugins = cache.get(CACHE_KEY_CATALOG_FEED, default={})
    if not catalog_plugins:
        try:
            catalog_plugins = make_plugin_dict()
            cache.set(CACHE_KEY_CATALOG_FEED, catalog_plugins, 3600)
        except requests.exceptions.RequestException:
            pass

    return catalog_plugins
