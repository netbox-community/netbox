from django import template
from django.utils.safestring import mark_safe

from netbox.navigation.menu import MENUS

__all__ = (
    'nav',
    'htmx_boost',
)


register = template.Library()


@register.inclusion_tag("navigation/menu.html", takes_context=True)
def nav(context):
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
                if not user.has_perms(item.permissions):
                    continue
                if item.staff_only and not user.is_staff:
                    continue
                buttons = [
                    button for button in item.buttons if user.has_perms(button.permissions)
                ]
                items.append((item, buttons))
            if items:
                groups.append((group, items))
        if groups:
            nav_items.append((menu, groups))

    return {
        'nav_items': nav_items,
        'htmx_navigation': context['htmx_navigation']
    }


@register.simple_tag(takes_context=True)
def htmx_boost(context, target='#page-content', select='#page-content'):
    """
    Renders the HTML attributes needed to effect HTMX boosting within an element if
    HTMX navigation is enabled for the request. The target and select parameters are
    rendered as `hx-target` and `hx-select`, respectively. For example:

        <div id="page-content" {% htmx_boost %}>

    If HTMX navigation is not enabled, the tag renders no content.
    """
    if not context.get('htmx_navigation', False):
        return ''
    hx_params = {
        'hx-boost': 'true',
        'hx-target': target,
        'hx-select': select,
        'hx-swap': 'outerHTML show:window:top',
    }
    htmx_params = ' '.join([
        f'{k}="{v}"' for k, v in hx_params.items()
    ])
    return mark_safe(htmx_params)
