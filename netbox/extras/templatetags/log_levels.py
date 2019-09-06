from django import template

from extras.constants import LOG_DEFAULT, LOG_FAILURE, LOG_INFO, LOG_SUCCESS, LOG_WARNING


register = template.Library()


@register.inclusion_tag('extras/templatetags/log_level.html')
def log_level(level):
    """
    Display a label indicating a syslog severity (e.g. info, warning, etc.).
    """
    levels = {
        LOG_DEFAULT: {
            'name': 'Default',
            'class': 'default'
        },
        LOG_SUCCESS: {
            'name': 'Success',
            'class': 'success',
        },
        LOG_INFO: {
            'name': 'Info',
            'class': 'info'
        },
        LOG_WARNING: {
            'name': 'Warning',
            'class': 'warning'
        },
        LOG_FAILURE: {
            'name': 'Failure',
            'class': 'danger'
        }
    }

    return levels[level]
