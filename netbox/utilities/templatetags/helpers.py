import datetime
import json
import re
import yaml

from django import template
from django.utils.html import strip_tags
from django.utils.safestring import mark_safe
from markdown import markdown

from utilities.choices import unpack_grouped_choices
from utilities.utils import foreground_color


register = template.Library()


#
# Filters
#

@register.filter()
def oneline(value):
    """
    Replace each line break with a single space
    """
    value = value.replace('\r', '')
    return value.replace('\n', ' ')


@register.filter()
def placeholder(value):
    """
    Render a muted placeholder if value equates to False.
    """
    if value:
        return value
    placeholder = '<span class="text-muted">&mdash;</span>'
    return mark_safe(placeholder)


@register.filter()
def getlist(value, arg):
    """
    Return all values of a QueryDict key
    """
    return value.getlist(arg)


@register.filter
def getkey(value, key):
    """
    Return a dictionary item specified by key
    """
    return value[key]


@register.filter(is_safe=True)
def gfm(value):
    """
    Render text as GitHub-Flavored Markdown
    """
    # Strip HTML tags
    value = strip_tags(value)

    # Render Markdown with GFM extension
    html = markdown(value, extensions=['mdx_gfm'])

    return mark_safe(html)


@register.filter()
def render_json(value):
    """
    Render a dictionary as formatted JSON.
    """
    return json.dumps(value, indent=4, sort_keys=True)


@register.filter()
def render_yaml(value):
    """
    Render a dictionary as formatted YAML.
    """
    return yaml.dump(dict(value))


@register.filter()
def model_name(obj):
    """
    Return the name of the model of the given object
    """
    return obj._meta.verbose_name


@register.filter()
def model_name_plural(obj):
    """
    Return the plural name of the model of the given object
    """
    return obj._meta.verbose_name_plural


@register.filter()
def contains(value, arg):
    """
    Test whether a value contains any of a given set of strings. `arg` should be a comma-separated list of strings.
    """
    return any(s in value for s in arg.split(','))


@register.filter()
def bettertitle(value):
    """
    Alternative to the builtin title(); uppercases words without replacing letters that are already uppercase.
    """
    return ' '.join([w[0].upper() + w[1:] for w in value.split()])


@register.filter()
def humanize_speed(speed):
    """
    Humanize speeds given in Kbps. Examples:

        1544 => "1.544 Mbps"
        100000 => "100 Mbps"
        10000000 => "10 Gbps"
    """
    if not speed:
        return ''
    if speed >= 1000000000 and speed % 1000000000 == 0:
        return '{} Tbps'.format(int(speed / 1000000000))
    elif speed >= 1000000 and speed % 1000000 == 0:
        return '{} Gbps'.format(int(speed / 1000000))
    elif speed >= 1000 and speed % 1000 == 0:
        return '{} Mbps'.format(int(speed / 1000))
    elif speed >= 1000:
        return '{} Mbps'.format(float(speed) / 1000)
    else:
        return '{} Kbps'.format(speed)


@register.filter()
def example_choices(field, arg=3):
    """
    Returns a number (default: 3) of example choices for a ChoiceFiled (useful for CSV import forms).
    """
    examples = []
    if hasattr(field, 'queryset'):
        choices = [
            (obj.pk, getattr(obj, field.to_field_name)) for obj in field.queryset[:arg + 1]
        ]
    else:
        choices = field.choices
    for value, label in unpack_grouped_choices(choices):
        if len(examples) == arg:
            examples.append('etc.')
            break
        if not value or not label:
            continue
        examples.append(label)
    return ', '.join(examples) or 'None'


@register.filter()
def tzoffset(value):
    """
    Returns the hour offset of a given time zone using the current time.
    """
    return datetime.datetime.now(value).strftime('%z')


@register.filter()
def fgcolor(value):
    """
    Return black (#000000) or white (#ffffff) given an arbitrary background color in RRGGBB format.
    """
    value = value.lower().strip('#')
    if not re.match('^[0-9a-f]{6}$', value):
        return ''
    return '#{}'.format(foreground_color(value))


@register.filter()
def divide(x, y):
    """
    Return x/y (rounded).
    """
    if x is None or y is None:
        return None
    return round(x / y)


@register.filter()
def percentage(x, y):
    """
    Return x/y as a percentage.
    """
    if x is None or y is None:
        return None
    return round(x / y * 100)


#
# Tags
#

@register.simple_tag()
def querystring(request, **kwargs):
    """
    Append or update the page number in a querystring.
    """
    querydict = request.GET.copy()
    for k, v in kwargs.items():
        if v is not None:
            querydict[k] = str(v)
        elif k in querydict:
            querydict.pop(k)
    querystring = querydict.urlencode(safe='/')
    if querystring:
        return '?' + querystring
    else:
        return ''


@register.inclusion_tag('utilities/templatetags/utilization_graph.html')
def utilization_graph(utilization, warning_threshold=75, danger_threshold=90):
    """
    Display a horizontal bar graph indicating a percentage of utilization.
    """
    return {
        'utilization': utilization,
        'warning_threshold': warning_threshold,
        'danger_threshold': danger_threshold,
    }


@register.inclusion_tag('utilities/templatetags/tag.html')
def tag(tag, url_name=None):
    """
    Display a tag, optionally linked to a filtered list of objects.
    """
    return {
        'tag': tag,
        'url_name': url_name,
    }
