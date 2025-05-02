from django.utils.text import slugify
from django.utils.translation import gettext as _

from netbox.choices import ButtonColorChoices
from netbox.navigation import MenuGroup

__all__ = (
    'PluginMenu',
    'PluginMenuButton',
    'PluginMenuItem',
)


class PluginMenu:
    icon_class = 'mdi mdi-puzzle'

    def __init__(self, label, groups, icon_class=None):
        self.label = label
        self.groups = [
            MenuGroup(label, items) for label, items in groups
        ]
        if icon_class is not None:
            self.icon_class = icon_class

    @property
    def name(self):
        return slugify(self.label)


class PluginMenuItem:
    """
    This class represents a navigation menu item. This constitutes primary link and its text, but also allows for
    specifying additional link buttons that appear to the right of the item in the van menu.

    Links are specified as Django reverse URL strings.
    Buttons are each specified as a list of PluginMenuButton instances.
    """
    permissions = []
    buttons = []

    def __init__(self, link, link_text, auth_required=False, staff_only=False, permissions=None, buttons=None):
        self.link = link
        self.link_text = link_text
        self.auth_required = auth_required
        self.staff_only = staff_only
        if permissions is not None:
            if type(permissions) not in (list, tuple):
                raise TypeError(_("Permissions must be passed as a tuple or list."))
            self.permissions = permissions
        if buttons is not None:
            if type(buttons) not in (list, tuple):
                raise TypeError(_("Buttons must be passed as a tuple or list."))
            self.buttons = buttons


class PluginMenuButton:
    """
    This class represents a button within a PluginMenuItem. Note that button colors should come from
    ButtonColorChoices.
    """
    color = ButtonColorChoices.DEFAULT
    permissions = []

    def __init__(self, link, title, icon_class, color=None, permissions=None):
        self.link = link
        self.title = title
        self.icon_class = icon_class
        if permissions is not None:
            if type(permissions) not in (list, tuple):
                raise TypeError(_("Permissions must be passed as a tuple or list."))
            self.permissions = permissions
        if color is not None:
            if color not in ButtonColorChoices.values():
                raise ValueError(_("Button color must be a choice within ButtonColorChoices."))
            self.color = color
