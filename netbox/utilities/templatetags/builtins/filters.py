import datetime
import json
import re

import yaml
from django import template
from django.contrib.contenttypes.models import ContentType
from django.contrib.humanize.templatetags.humanize import naturaltime
from django.utils.html import escape
from django.utils.safestring import mark_safe
from markdown import markdown
from markdown.extensions.tables import TableExtension

from netbox.config import get_config
from utilities.html import clean_html, foreground_color
from utilities.markdown import StrikethroughExtension
from utilities.string import title

__all__ = (
    'bettertitle',
    'content_type',
    'content_type_id',
    'fgcolor',
    'isodate',
    'isodatetime',
    'isotime',
    'linkify',
    'meta',
    'placeholder',
    'render_json',
    'render_markdown',
    'render_yaml',
    'split',
    'tzoffset',
)

register = template.Library()


#
# General
#

@register.filter()
def linkify(instance, attr=None):
    """
    Render a hyperlink for an object with a `get_absolute_url()` method, optionally specifying the name of an
    attribute to use for the link text. If no attribute is given, the object's string representation will be
    used.

    If the object has no `get_absolute_url()` method, return the text without a hyperlink element.
    """
    if instance is None:
        return ''

    text = getattr(instance, attr) if attr is not None else str(instance)
    try:
        url = instance.get_absolute_url()
        return mark_safe(f'<a href="{url}">{escape(text)}</a>')
    except (AttributeError, TypeError):
        return text


@register.filter()
def bettertitle(value):
    """
    Alternative to the builtin title(). Ensures that the first letter of each word is uppercase but retains the
    original case of all others.
    """
    return title(value)


@register.filter()
def fgcolor(value, dark='000000', light='ffffff'):
    """
    Return black (#000000) or white (#ffffff) given an arbitrary background color in RRGGBB format. The foreground
    color with the better contrast is returned.

    Args:
        value: The background color
        dark: The foreground color to use for light backgrounds
        light: The foreground color to use for dark backgrounds
    """
    value = value.lower().strip('#')
    if not re.match('^[0-9a-f]{6}$', value):
        return ''
    return f'#{foreground_color(value, dark, light)}'


@register.filter()
def meta(model, attr):
    """
    Return the specified Meta attribute of a model. This is needed because Django does not permit templates
    to access attributes which begin with an underscore (e.g. _meta).

    Args:
        model: A Django model class or instance
        attr: The attribute name
    """
    return getattr(model._meta, attr, '')


@register.filter()
def placeholder(value):
    """
    Render a muted placeholder if the value equates to False.
    """
    if value not in ('', None):
        return value

    return mark_safe('<span class="text-muted">&mdash;</span>')


@register.filter()
def split(value, separator=','):
    """
    Wrapper for Python's `split()` string method.

    Args:
        value: A string
        separator: String on which the value will be split
    """
    return value.split(separator)


@register.filter()
def tzoffset(value):
    """
    Returns the hour offset of a given time zone using the current time.
    """
    return datetime.datetime.now(value).strftime('%z')


#
# Content types
#

@register.filter()
def content_type(model):
    """
    Return the ContentType for the given object.
    """
    return ContentType.objects.get_for_model(model)


@register.filter()
def content_type_id(model):
    """
    Return the ContentType ID for the given object.
    """
    content_type = ContentType.objects.get_for_model(model)
    if content_type:
        return content_type.pk
    return None


#
# Rendering
#

@register.filter('markdown', is_safe=True)
def render_markdown(value):
    """
    Render a string as Markdown. This filter is invoked as "markdown":

        {{ md_source_text|markdown }}
    """
    if not value:
        return ''

    # Render Markdown
    html = markdown(value, extensions=[
        'def_list',
        'fenced_code',
        StrikethroughExtension(),
        TableExtension(use_align_attribute=True),
    ])

    # If the string is not empty wrap it in rendered-markdown to style tables
    if html:
        html = f'<div class="rendered-markdown">{html}</div>'

    schemes = get_config().ALLOWED_URL_SCHEMES

    # Sanitize HTML
    html = clean_html(html, schemes)

    return mark_safe(html)


@register.filter('json')
def render_json(value):
    """
    Render a dictionary as formatted JSON. This filter is invoked as "json":

        {{ data_dict|json }}
    """
    return json.dumps(value, ensure_ascii=False, indent=4, sort_keys=True)


@register.filter('yaml')
def render_yaml(value):
    """
    Render a dictionary as formatted YAML. This filter is invoked as "yaml":

        {{ data_dict|yaml }}
    """
    return yaml.dump(json.loads(json.dumps(value)))


#
# Time & date
#

@register.filter()
def isodate(value):
    if type(value) is datetime.date:
        text = value.isoformat()
    elif type(value) is datetime.datetime:
        text = value.date().isoformat()
    else:
        return ''
    return mark_safe(f'<span title="{naturaltime(value)}">{text}</span>')


@register.filter()
def isotime(value, spec='seconds'):
    if type(value) is datetime.time:
        return value.isoformat(timespec=spec)
    if type(value) is datetime.datetime:
        return value.time().isoformat(timespec=spec)
    return ''


@register.filter()
def isodatetime(value, spec='seconds'):
    if type(value) is datetime.datetime:
        text = f'{isodate(value)} {isotime(value, spec=spec)}'
    else:
        return ''
    return mark_safe(f'<span title="{naturaltime(value)}">{text}</span>')
