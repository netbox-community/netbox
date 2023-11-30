from django import template
from django.utils.safestring import mark_safe

register = template.Library()


@register.simple_tag()
def nested_tree(obj):
    """
    Renders the entire hierarchy of a recursively-nested object (such as Region or SiteGroup).
    """
    if not obj:
        return mark_safe('&mdash;')

    nodes = obj.get_ancestors(include_self=True)
    return mark_safe(
        ' / '.join(
            f'<a href="{node.get_absolute_url()}">{node}</a>' for node in nodes
        )
    )
