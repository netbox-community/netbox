from dataclasses import dataclass
from typing import Sequence, Optional

from utilities.choices import ButtonColorChoices


__all__ = (
    'get_model_item',
    'get_model_buttons',
    'Menu',
    'MenuGroup',
    'MenuItem',
    'MenuItemButton',
)


#
# Navigation menu data classes
#

@dataclass
class MenuItemButton:

    link: str
    title: str
    icon_class: str
    permissions: Optional[Sequence[str]] = ()
    color: Optional[str] = None


@dataclass
class MenuItem:

    link: str
    link_text: str
    permissions: Optional[Sequence[str]] = ()
    buttons: Optional[Sequence[MenuItemButton]] = ()


@dataclass
class MenuGroup:

    label: str
    items: Sequence[MenuItem]


@dataclass
class Menu:

    label: str
    icon_class: str
    groups: Sequence[MenuGroup]

    @property
    def name(self):
        return self.label.replace(' ', '_')


#
# Utility functions
#

def get_model_item(app_label, model_name, label, actions=('add', 'import'), permission_app_label=None, permission_model_name=None):
    if not permission_app_label:
        permission_app_label = app_label
    if not permission_model_name:
        permission_model_name = model_name
    return MenuItem(
        link=f'{app_label}:{model_name}_list',
        link_text=label,
        permissions=[f'{permission_app_label}.view_{permission_model_name}'],
        buttons=get_model_buttons(app_label, model_name, actions, permission_app_label, permission_model_name)
    )


def get_model_buttons(app_label, model_name, actions=('add', 'import'), permission_app_label=None, permission_model_name=None):
    buttons = []
    if not permission_app_label:
        permission_app_label = app_label
    if not permission_model_name:
        permission_model_name = model_name

    if 'add' in actions:
        buttons.append(
            MenuItemButton(
                link=f'{app_label}:{model_name}_add',
                title='Add',
                icon_class='mdi mdi-plus-thick',
                permissions=[f'{permission_app_label}.add_{permission_model_name}'],
                color=ButtonColorChoices.GREEN
            )
        )
    if 'import' in actions:
        buttons.append(
            MenuItemButton(
                link=f'{app_label}:{model_name}_import',
                title='Import',
                icon_class='mdi mdi-upload',
                permissions=[f'{permission_app_label}.add_{permission_model_name}'],
                color=ButtonColorChoices.CYAN
            )
        )

    return buttons
