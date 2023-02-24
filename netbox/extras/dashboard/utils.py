import uuid

from netbox.registry import registry
from extras.constants import DEFAULT_DASHBOARD
from extras.models import Dashboard

__all__ = (
    'get_dashboard',
    'get_default_dashboard_config',
    'get_widget_class_and_config',
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


def get_widget_class_and_config(dashboard, id):
    config = dict(dashboard.config[id])  # Copy to avoid mutating userconfig data
    widget_class = registry['widgets'].get(config.pop('class'))
    return widget_class, config


def get_dashboard(user):
    """
    Return the dashboard layout for a given User.
    """
    if not user.is_anonymous and hasattr(user, 'dashboard'):
        dashboard = user.dashboard
    else:
        dashboard = get_default_dashboard_config()

    widgets = []
    for grid_item in dashboard.layout:
        widget_class, widget_config = get_widget_class_and_config(dashboard, grid_item['id'])
        widget = widget_class(id=grid_item['id'], **widget_config)
        widget.set_layout(grid_item)
        widgets.append(widget)

    return widgets


def get_default_dashboard_config():
    dashboard = Dashboard(
        layout=[],
        config={}
    )
    for widget in DEFAULT_DASHBOARD:
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
            'config': widget.get('config', {}),
        }

    return dashboard
