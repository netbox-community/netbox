from django.utils.translation import gettext as _
from netbox.plugins.navigation import PluginMenu, PluginMenuButton, PluginMenuItem


items = (
    PluginMenuItem(
        link='plugins:dummy_plugin:dummy_models',
        link_text='Item 1',
        buttons=(
            PluginMenuButton(
                link='admin:dummy_plugin_dummymodel_add',
                title='Add a new dummy model',
                icon_class='mdi mdi-plus-thick',
            ),
            PluginMenuButton(
                link='admin:dummy_plugin_dummymodel_add',
                title='Add a new dummy model',
                icon_class='mdi mdi-plus-thick',
            ),
        )
    ),
    PluginMenuItem(
        link='plugins:dummy_plugin:dummy_models',
        link_text='Item 2',
    ),
)

menu = PluginMenu(
    label=_('Dummy Plugin'),
    groups=(('Group 1', items),),
)
menu_items = items
