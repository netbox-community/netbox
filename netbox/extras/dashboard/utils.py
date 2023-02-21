import uuid

from netbox.registry import registry
from extras.constants import DEFAULT_DASHBOARD

__all__ = (
    'get_dashboard',
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


def get_dashboard(user):
    """
    Return the dashboard layout for a given User.
    """
    if not user.is_anonymous and user.config.get('dashboard'):
        config = user.config.get('dashboard')
    else:
        config = get_default_dashboard_config()
        if not user.is_anonymous:
            user.config.set('dashboard', config, commit=True)

    widgets = []
    for grid_item in config['layout']:
        widget_id = grid_item['id']
        widget_config = config['widgets'][widget_id]
        widget_class = registry['widgets'].get(widget_config.pop('class'))
        widget = widget_class(id=widget_id, **widget_config)
        widget.set_layout(grid_item)
        widgets.append(widget)

    return widgets


def get_default_dashboard_config():
    config = {
        'layout': [],
        'widgets': {},
    }
    for widget in DEFAULT_DASHBOARD:
        id = str(uuid.uuid4())
        config['layout'].append({
            'id': id,
            'w': widget['width'],
            'h': widget['height'],
            'x': widget.get('x'),
            'y': widget.get('y'),
        })
        config['widgets'][id] = {
            'class': widget['widget'],
            'title': widget.get('title'),
            'config': widget.get('config', {}),
        }

    return config
