import uuid

from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.utils.translation import gettext as _

from netbox.registry import registry
from extras.constants import DEFAULT_DASHBOARD

__all__ = (
    'get_dashboard',
    'get_default_dashboard',
    'get_widget_class',
    'register_widget',
)


def register_widget(cls):
    """
    Decorator for registering a DashboardWidget class.
    """
    app_label = cls.__module__.split('.', maxsplit=1)[0]
    label = f'{app_label}.{cls.__name__}'
    registry['widgets'][label] = cls

    return cls


def get_widget_class(name):
    """
    Return a registered DashboardWidget class identified by its name.
    """
    try:
        return registry['widgets'][name]
    except KeyError:
        raise ValueError(_("Unregistered widget class: {name}").format(name=name))


def get_dashboard(user):
    """
    Return the Dashboard for a given User if one exists, or generate a default dashboard.
    """
    if user.is_anonymous:
        dashboard = get_default_dashboard()
    else:
        try:
            dashboard = user.dashboard
        except ObjectDoesNotExist:
            # Create a dashboard for this user
            dashboard = get_default_dashboard()
            dashboard.user = user
            dashboard.save()

    return dashboard


def get_default_dashboard(config=None):
    from extras.models import Dashboard

    dashboard = Dashboard()
    config = config or settings.DEFAULT_DASHBOARD or DEFAULT_DASHBOARD

    for widget in config:
        id = str(uuid.uuid4())
        dashboard.layout.append({
            'id': id,
            'w': widget['width'],
            'h': widget['height'],
            'x': widget.get('x'),
            'y': widget.get('y'),
        })
        dashboard.config[id] = {
            'class': widget['widget'],
            'title': widget.get('title'),
            'color': widget.get('color'),
            'config': widget.get('config', {}),
        }

    return dashboard
