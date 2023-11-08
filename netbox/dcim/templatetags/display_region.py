from django import template
from django.utils.safestring import mark_safe

register = template.Library()

def _display_site(obj):
    """
    Render a link to the site of an object.
    """
    if hasattr(obj, 'site'):
        return mark_safe('<a href="{}">{}</a>'.format(
            obj.site.get_absolute_url(),
            obj.site
        ))
    return None


@register.simple_tag(takes_context=True)
def display_region(context, obj, include_site=False):
    """
    Renders hierarchical region data for a given object.
    """
    # Attempt to retrieve the region from obj or its site attribute
    region = getattr(obj, 'region', None) or getattr(getattr(obj, 'site', None), 'region', None)

    # Return a placeholder if no region is found
    if not region:
        # If include_site is True, attempt to retrieve the site from obj
        if include_site:
            return _display_site(obj) or mark_safe('&mdash;')
        return mark_safe('&mdash;')

    # Retrieve all regions in the hierarchy
    regions = region.get_ancestors(include_self=True)

    # Build the URLs and names for the regions
    regions_links = [
        '<a href="{}">{}</a>'.format(
            context['request'].build_absolute_uri(region.get_absolute_url()), region
        ) for region in regions
    ]

    # Render the hierarchy as a list of links
    region = mark_safe(' / '.join(regions_links))
    if include_site:
        site = _display_site(obj)
        if site:
            return mark_safe('{} / {}'.format(region, site))

    return region
