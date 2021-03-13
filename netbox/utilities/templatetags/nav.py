from pathlib import Path
from typing import Dict, List
from django import template
from django.template import Context
from django.contrib.auth.context_processors import PermWrapper

import yaml

register = template.Library()

NAV_GROUPS = Path.cwd() / "utilities" / "templatetags" / "nav.yaml"


def import_groups() -> Dict:
    with NAV_GROUPS.open("r") as f:
        menus = yaml.safe_load(f.read())
        return menus


def process_nav_group(nav_group: Dict, perms: PermWrapper) -> Dict:
    """Enable a menu item if view permissions exist for the user."""
    for group in nav_group["groups"]:
        for item in group["items"]:
            # Parse the URL template tag to a permission string.
            app, scope = item["url"].split(":")
            view_perm = f"{app}.view_{scope}"
            if view_perm in perms:
                # If the view permission for each item exists, toggle
                # the `disabled` field, which will be used in the UI.
                item["disabled"] = False

    return nav_group


@register.inclusion_tag("navigation/nav_items.html", takes_context=True)
def nav(context: Context) -> Dict:
    """Provide navigation items to template."""
    perms: PermWrapper = context["perms"]
    nav_menus = import_groups()
    groups = [process_nav_group(g, perms) for g in nav_menus["menus"]]

    return {"nav_items": groups, "request": context["request"]}
