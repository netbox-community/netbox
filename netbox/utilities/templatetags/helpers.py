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


#
# Tags
#

@register.simple_tag()
def querystring_toggle(request, multi=True, page_key='page', **kwargs):
    """
    Add or remove a parameter in the HTTP GET query string
    """
    new_querydict = request.GET.copy()

    # Remove page number from querystring
    try:
        new_querydict.pop(page_key)
    except KeyError:
        pass

    # Add/toggle parameters
    for k, v in kwargs.items():
        values = new_querydict.getlist(k)
        if k in new_querydict and v in values:
            values.remove(v)
            new_querydict.setlist(k, values)
        elif not multi:
            new_querydict[k] = v
        else:
            new_querydict.update({k: v})

    querystring = new_querydict.urlencode()
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
