from __future__ import unicode_literals

from markdown import markdown

from django import template
from django.utils.safestring import mark_safe


register = template.Library()


#
# Filters
#

@register.filter()
def oneline(value):
    """
    Replace each line break with a single space
    """
    return value.replace('\n', ' ')


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
    html = markdown(value, extensions=['mdx_gfm'])
    return mark_safe(html)


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
def example_choices(field, arg=3):
    """
    Returns a number (default: 3) of example choices for a ChoiceFiled (useful for CSV import forms).
    """
    examples = []
    if hasattr(field, 'queryset'):
        choices = [(obj.pk, getattr(obj, field.to_field_name)) for obj in field.queryset[:arg + 1]]
    else:
        choices = field.choices
    for id, label in choices:
        if len(examples) == arg:
            examples.append('etc.')
            break
        if not id:
            continue
        examples.append(label)
    return ', '.join(examples) or 'None'


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
            querydict[k] = v
        elif k in querydict:
            querydict.pop(k)
    querystring = querydict.urlencode()
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
