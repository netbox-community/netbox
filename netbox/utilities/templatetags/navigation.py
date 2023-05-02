from typing import Dict
from django import template
from django.template import Context

from netbox.navigation.menu import MENUS

__all__ = (
    'nav',
)


register = template.Library()


@register.inclusion_tag("navigation/menu.html", takes_context=True)
def nav(context: Context) -> Dict:
    """
    Render the navigation menu.
    """
    user = context['request'].user
    nav_items = []

    # Construct the navigation menu based upon the current user's permissions
    for menu in MENUS:
        groups = []
        for group in menu.groups:
            items = []
            for item in group.items:
                if user.has_perms(item.permissions):
                    buttons = [
                        button for button in item.buttons if user.has_perms(button.permissions)
                    ]
                    items.append((item, buttons))
            if items:
                groups.append((group, items))
        if groups:
            nav_items.append((menu, groups))

    return {
        "nav_items": nav_items,
        "request": context["request"]
    }
