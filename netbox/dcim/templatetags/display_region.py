from django import template
from django.utils.safestring import mark_safe

register = template.Library()


def _display_site(obj):
    """
    Render a link to the site of an object.
    """
    site = getattr(obj, 'site', None)
    return mark_safe('<a href="{}">{}</a>'.format(site.get_absolute_url(), site)) if site else None


@register.simple_tag(takes_context=True)
def display_region(context, obj, include_site=False):
    """
    Renders hierarchical region data for a given object, optionally including the site.
    """
    # Retrieve the region or site information
    region = getattr(obj, 'region', None) or getattr(obj.site, 'region', None) if hasattr(obj, 'site') else None
    site_link = _display_site(obj) if include_site else None

    # Return a placeholder if no region or site is found
    if not region and not site_link:
        return mark_safe('&mdash;')

    # Build the region links if the region is available
    region_links = ' / '.join(
        '<a href="{}">{}</a>'.format(context['request'].build_absolute_uri(reg.get_absolute_url()), reg)
        for reg in region.get_ancestors(include_self=True)
    ) if region else ''

    # Concatenate region and site links
    links = ' / '.join(filter(None, [region_links, site_link]))

    return mark_safe(links)
