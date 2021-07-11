from typing import Dict
from django import template
from django.template import Context
from django.contrib.auth.context_processors import PermWrapper

from netbox.navigation_menu import Menu, MenuGroup, MENUS


register = template.Library()


def process_menu(menu: Menu, perms: PermWrapper) -> MenuGroup:
    """Enable a menu item if view permissions exist for the user."""
    for group in menu.groups:
        for item in group.items:
            # Parse the URL template tag to a permission string.
            app, scope = item.url.split(":")
            object_name = scope.replace("_list", "")

            view_perm = f"{app}.view_{scope}"
            add_perm = f"{app}.add_object_name"

            if view_perm in perms:
                # If the view permission for each item exists, toggle
                # the `disabled` field, which will be used in the UI.
                item.disabled = False

            if add_perm in perms:
                if item.add_url is not None:
                    item.has_add = True
                if item.import_url is not None:
                    item.has_import = True

    return menu


@register.inclusion_tag("navigation/nav_items.html", takes_context=True)
def nav(context: Context) -> Dict:
    """Provide navigation items to template."""
    perms: PermWrapper = context["perms"]
    groups = [process_menu(g, perms) for g in MENUS]

    return {"nav_items": groups, "request": context["request"]}
