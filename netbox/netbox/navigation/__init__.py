from collections.abc import Sequence
from dataclasses import dataclass

from django.urls import reverse_lazy

__all__ = (
    'Menu',
    'MenuGroup',
    'MenuItem',
    'MenuItemButton',
    'get_model_buttons',
    'get_model_item',
)


#
# Navigation menu data classes
#

@dataclass
class MenuItemButton:

    link: str
    title: str
    icon_class: str
    _url: str | None = None
    permissions: Sequence[str] | None = ()
    color: str | None = None

    def __post_init__(self):
        if self.link:
            self._url = reverse_lazy(self.link)

    @property
    def url(self):
        return self._url

    @url.setter
    def url(self, value):
        self._url = value


@dataclass
class MenuItem:

    link: str
    link_text: str
    _url: str | None = None
    permissions: Sequence[str] | None = ()
    auth_required: bool | None = False
    staff_only: bool | None = False
    buttons: Sequence[MenuItemButton] | None = ()

    def __post_init__(self):
        if self.link:
            self._url = reverse_lazy(self.link)

    @property
    def url(self):
        return self._url

    @url.setter
    def url(self, value):
        self._url = value


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

def get_model_item(app_label, model_name, label, actions=('add', 'bulk_import')):
    return MenuItem(
        link=f'{app_label}:{model_name}_list',
        link_text=label,
        permissions=[f'{app_label}.view_{model_name}'],
        buttons=get_model_buttons(app_label, model_name, actions)
    )


def get_model_buttons(app_label, model_name, actions=('add', 'bulk_import')):
    buttons = []

    if 'add' in actions:
        buttons.append(
            MenuItemButton(
                link=f'{app_label}:{model_name}_add',
                title='Add',
                icon_class='mdi mdi-plus-thick',
                permissions=[f'{app_label}.add_{model_name}']
            )
        )
    if 'bulk_import' in actions:
        buttons.append(
            MenuItemButton(
                link=f'{app_label}:{model_name}_bulk_import',
                title='Import',
                icon_class='mdi mdi-upload',
                permissions=[f'{app_label}.add_{model_name}']
            )
        )

    return buttons
