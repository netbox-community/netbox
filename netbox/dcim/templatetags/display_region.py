from django import template
from django.utils.safestring import mark_safe

from dcim.models import Site

register = template.Library()


@register.simple_tag(takes_context=True)
def display_region(context, obj):
    """
    Renders hierarchical region data for a given object.
    """
    # Check if the obj is an instance of Site
    if isinstance(obj, Site):
        if not obj.region:
            return mark_safe('&mdash;')

        # If so, retrieve the Site's Region
        region = obj.region
    else:
        if not hasattr(obj, 'site'):
            return mark_safe('&mdash;')

        # Otherwise, retrieve the Region from the Site associated with the object
        region = obj.site.region

    # Retrieve all regions in the hierarchy
    regions = region.get_ancestors(include_self=True)

    # Render the hierarchy as a list of links
    return mark_safe(
        ' / '.join([
            '<a href="{}">{}</a>'.format(
                context['request'].build_absolute_uri(region.get_absolute_url()),
                region
            ) for region in regions
        ])
    )
