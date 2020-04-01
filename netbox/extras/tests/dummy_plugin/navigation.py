from extras.plugins import PluginMenuButton, PluginMenuItem


menu_items = (
    PluginMenuItem(
        link='plugins:dummy_plugin:dummy_models',
        link_text='Item 1',
        buttons=(
            PluginMenuButton(
                link='admin:dummy_plugin_dummymodel_add',
                title='Add a new dummy model',
                icon_class='fa-plus',
            ),
            PluginMenuButton(
                link='admin:dummy_plugin_dummymodel_add',
                title='Add a new dummy model',
                icon_class='fa-plus',
            ),
        )
    ),
    PluginMenuItem(
        link='plugins:dummy_plugin:dummy_models',
        link_text='Item 2',
    ),
)
