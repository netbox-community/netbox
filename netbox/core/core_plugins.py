from dataclasses import dataclass

from django.conf import settings
from django.utils.translation import gettext_lazy as _

from core.choices import CorePluginStatusChoices

__all__ = (
    'CORE_PLUGINS',
    'CorePlugin',
    'get_core_plugin_names',
    'get_core_plugins',
)


@dataclass
class CorePlugin:
    """
    A NetBox Labs-maintained plugin. These are not published to the public plugins
    catalog, so we describe them statically and render them in a dedicated section
    of the plugins list page. Plugins with `commercial=True` are paid features and
    appear as "Locked" on Community edition; plugins with `commercial=False` are
    free and always appear as "Available" when not installed.
    """
    config_name: str
    title: str
    description: str
    mdi_icon: str
    product_url: str
    commercial: bool = False


CORE_PLUGINS = (
    CorePlugin(
        config_name='netbox_asset_lifecycle',
        title=_('Asset Lifecycle'),
        description=_('Track network hardware through procurement, deployment, and retirement.'),
        mdi_icon='mdi-clipboard-list-outline',
        product_url='#',
        commercial=True,
    ),
    CorePlugin(
        config_name='netbox_branching',
        title=_('Branching'),
        description=_('Stage and review changes to NetBox data in isolated branches before merging.'),
        mdi_icon='mdi-source-branch',
        product_url='https://netboxlabs.com/docs/extensions/branching/',
    ),
    CorePlugin(
        config_name='netbox_changes',
        title=_('Changes'),
        description=_('Manage proposed and scheduled changes to network infrastructure.'),
        mdi_icon='mdi-history',
        product_url='https://netboxlabs.com/docs/developer/plugins-extensions/changes/',
        commercial=True,
    ),
    CorePlugin(
        config_name='netbox_custom_objects',
        title=_('Custom Objects'),
        description=_('Define and manage your own object types alongside the built-in NetBox models.'),
        mdi_icon='mdi-cube-outline',
        product_url='https://netboxlabs.com/docs/extensions/custom-objects/',
    ),
    CorePlugin(
        config_name='netbox_diode_plugin',
        title=_('Diode'),
        description=_('Streamline data ingestion into NetBox from external sources.'),
        mdi_icon='mdi-database-import-outline',
        product_url='https://netboxlabs.com/docs/diode/',
    ),
    CorePlugin(
        config_name='netbox_physical_geometry',
        title=_('Visual Explorer'),
        description=_('Render interactive 3D visualizations of physical infrastructure.'),
        mdi_icon='mdi-cube-scan',
        product_url='#',
        commercial=True,
    ),
)


def get_core_plugins(local_plugins=None):
    """
    Return a list of display entries for NetBox Labs core plugins. Each entry
    includes the static metadata plus a resolved status and the installed version
    (when applicable). Status is derived from whether the plugin is locally installed
    and whether commercial features are enabled on this NetBox edition.
    """
    local_plugins = local_plugins or {}
    commercial_enabled = settings.RELEASE.features.commercial
    status_labels = {value: label for value, label, *_ in CorePluginStatusChoices.CHOICES}
    entries = []

    for plugin in CORE_PLUGINS:
        local = local_plugins.get(plugin.config_name)
        latest_version = local.release_latest.version if local and local.release_latest else ''

        if local is not None and local.is_local:
            status = CorePluginStatusChoices.STATUS_INSTALLED
            installed_version = local.installed_version
        elif not plugin.commercial or commercial_enabled:
            status = CorePluginStatusChoices.STATUS_AVAILABLE
            installed_version = ''
        else:
            status = CorePluginStatusChoices.STATUS_LOCKED
            installed_version = ''

        entries.append({
            'config_name': plugin.config_name,
            'title': plugin.title,
            'description': plugin.description,
            'mdi_icon': plugin.mdi_icon,
            'product_url': plugin.product_url,
            'status': status,
            'status_label': status_labels.get(status, status),
            'status_color': CorePluginStatusChoices.colors.get(status, 'gray'),
            'installed_version': installed_version,
            'latest_version': latest_version,
        })

    return entries


def get_core_plugin_names():
    """
    Return the set of config names of core plugins, for use in filtering them out
    of the community catalog list.
    """
    return {plugin.config_name for plugin in CORE_PLUGINS}
