from django import template

from extras.choices import LogLevelChoices


register = template.Library()


@register.inclusion_tag('extras/templatetags/log_level.html')
def log_level(level):
    """
    Display a label indicating a syslog severity (e.g. info, warning, etc.).
    """
    return {
        'name': LogLevelChoices.as_dict()[level],
        'class': LogLevelChoices.CSS_CLASSES.get(level)
    }
