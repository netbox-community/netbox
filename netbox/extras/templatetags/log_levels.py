from django import template

from extras.constants import LOG_DEFAULT, LOG_FAILURE, LOG_INFO, LOG_SUCCESS, LOG_WARNING


register = template.Library()


@register.inclusion_tag('extras/templatetags/log_level.html')
def log_level(level):
    """
    Display a label indicating a syslog severity (e.g. info, warning, etc.).
    """
    # TODO: we should convert this to a choices class
    levels = {
        'default': {
            'name': 'Default',
            'class': 'default'
        },
        'success': {
            'name': 'Success',
            'class': 'success',
        },
        'info': {
            'name': 'Info',
            'class': 'info'
        },
        'warning': {
            'name': 'Warning',
            'class': 'warning'
        },
        'failure': {
            'name': 'Failure',
            'class': 'danger'
        }
    }

    return levels[level]
