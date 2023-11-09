from django import template
from django.utils.safestring import mark_safe
from dcim.models import Site

register = template.Library()


@register.simple_tag(takes_context=True)
def nested_tree(context, obj):
    """
    Renders hierarchical region data for a given object.
    """
    # Retrieve the region or site information
    if isinstance(obj, Site):
        region = obj.region
    else:
        region = getattr(obj, 'region', None) or getattr(obj.site, 'region', None)

    # Return a placeholder if no region or site is found
    if not region:
        return mark_safe('&mdash;')

    # Build the region links if the region is available
    return mark_safe(
        ' / '.join(
            '<a href="{}">{}</a>'.format(context['request'].build_absolute_uri(reg.get_absolute_url()), reg)
            for reg in region.get_ancestors(include_self=True)
        ) if region else ''
    )
