from extras.plugins import PluginMenuButton, PluginMenuItem
from utilities.choices import ButtonColorChoices


menu_items = (
    PluginMenuItem(
        link='plugins:dummy_plugin:dummy_models',
        link_text='Item 1',
        buttons=(
            PluginMenuButton(
                link='plugins:netbox_animal_sounds:random_animal',
                title='Random animal',
                icon_class='fa-question'
            ),
            PluginMenuButton(
                link='admin:netbox_animal_sounds_animal_add',
                title='Add a new animal',
                icon_class='fa-plus',
                color=ButtonColorChoices.GREEN,
                permissions=['netbox_animal_sounds.add_animal']
            ),
        )
    ),
    PluginMenuItem(
        link='plugins:dummy_plugin:dummy_models',
        link_text='Item 2',
    ),
)
