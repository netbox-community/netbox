from django.conf import settings as django_settings

from netbox.config import get_config
from netbox.registry import registry as registry_

__all__ = (
    'config',
    'preferences',
    'registry',
    'settings',
)


def config(request):
    """
    Adds NetBox configuration parameters to the template context. Example: {{ config.BANNER_LOGIN }}
    """
    return {
        'config': get_config(),
    }


def preferences(request):
    """
    Adds preferences for the current user (if authenticated) to the template context.
    Example: {{ preferences|get_key:"pagination.placement" }}
    """
    user_preferences = request.user.config if request.user.is_authenticated else {}
    return {
        'preferences': user_preferences,
        'htmx_navigation': user_preferences.get('ui.htmx_navigation', False) == 'true'
    }


def registry(request):
    """
    Adds NetBox registry items to the template context. Example: {{ registry.models.core }}
    """
    return {
        'registry': registry_,
    }


def settings(request):
    """
    Adds Django settings to the template context. Example: {{ settings.DEBUG }}
    """
    return {
        'settings': django_settings,
    }
