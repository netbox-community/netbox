from typing import Dict
from django import template
from django.template import Context

from netbox.navigation_menu import MENUS


register = template.Library()


@register.inclusion_tag("navigation/nav_items.html", takes_context=True)
def nav(context: Context) -> Dict:
    """
    Render the navigation menu.
    """
    return {
        "nav_items": MENUS,
        "request": context["request"]
    }
