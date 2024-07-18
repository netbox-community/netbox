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
class PluginAuthor:
    name: str = ''
    org_id: str = ''
    url: str = ''


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
    id: str = ''
    status: str = ''
    title_short: str = ''
    title_long: str = ''
    tag_line: str = ''
    description_short: str = ''
    slug: str = ''
    author: PluginAuthor = field(default_factory=PluginAuthor)
    created_at: datetime.datetime = None
    updated_at: datetime.datetime = None
    license_type: str = ''
    homepage_url: str = ''
    package_name_pypi: str = ''
    config_name: str = ''
    is_certified: bool = False
    release_latest: PluginVersion = field(default_factory=PluginVersion)
    release_recent_history: list[PluginVersion] = field(default_factory=list)
    is_local: bool = False  # extra field for locall intsalled plugins
    is_installed: bool = False


def get_local_plugins():
    plugins = {}
    for plugin_name in settings.PLUGINS:
        plugin = importlib.import_module(plugin_name)
        plugin_config: PluginConfig = plugin.config

        plugin_module = "{}.{}".format(plugin_config.__module__, plugin_config.__name__)  # type: ignore
        plugins[plugin_config.name] = Plugin(
            slug=plugin_config.name,
            title_short=plugin_config.verbose_name,
            tag_line=plugin_config.description,
            description_short=plugin_config.description,
            is_local=True,
            is_installed=True,
        )
        plugins[plugin_config.name].author.name = plugin_config.author or _('Unknown Author')

    return plugins


def get_catalog_plugins():
    session = requests.Session()
    plugins = {}

    def get_pages():
        # TODO: pagintation is curently broken in API
        payload = {'page': '1', 'per_page': '50'}
        first_page = session.get(settings.PLUGIN_CATALOG_URL, params=payload).json()
        yield first_page
        num_pages = first_page['metadata']['pagination']['last_page']

        for page in range(2, num_pages + 1):
            payload['page'] = page
            next_page = session.get(settings.PLUGIN_CATALOG_URL, params=payload).json()
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
            versions = sorted(versions, key=lambda x: x.date, reverse=True)
            latest = PluginVersion(
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
            author = PluginAuthor(
                name=data['author']['name'],
                org_id=data['author']['org_id'],
                url=data['author']['url'],
            )
            plugins[data['slug']] = Plugin(
                id=data['id'],
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
                release_latest=latest,
                release_recent_history=versions,
            )

    return plugins


def get_plugins():
    local_plugins = get_local_plugins()
    catalog_plugins = cache.get('plugins-catalog-feed')
    if not catalog_plugins:
        catalog_plugins = get_catalog_plugins()
        cache.set('plugins-catalog-feed', catalog_plugins, 3600)

    plugins = catalog_plugins
    for k, v in local_plugins.items():
        if k in plugins:
            plugins[k].is_local = True
            plugins[k].is_installed = True
        else:
            plugins[k] = v

    return plugins
