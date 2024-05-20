from django.utils.translation import gettext as _
from netbox.plugins.navigation import PluginMenu, PluginMenuButton, PluginMenuItem


items = (
    PluginMenuItem(
        link='plugins:dummy_plugin:dummy_model_list',
        link_text='Item 1',
        buttons=(
            PluginMenuButton(
                link='plugins:dummy_plugin:dummy_model_add',
                title='Button 1',
                icon_class='mdi mdi-plus-thick',
            ),
            PluginMenuButton(
                link='plugins:dummy_plugin:dummy_model_add',
                title='Button 2',
                icon_class='mdi mdi-plus-thick',
            ),
        )
    ),
    PluginMenuItem(
        link='plugins:dummy_plugin:dummy_model_list',
        link_text='Item 2',
    ),
)

menu = PluginMenu(
    label=_('Dummy Plugin'),
    groups=(('Group 1', items),),
)
menu_items = items
