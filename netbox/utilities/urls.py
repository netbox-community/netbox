from django.urls import path
from django.utils.module_loading import import_string
from django.views.generic import View

from netbox.registry import registry

__all__ = (
    'get_model_urls',
)


def get_model_urls(app_label, model_name, detail=True):
    """
    Return a list of URL paths for detail views registered to the given model.

    Args:
        app_label: App/plugin name
        model_name: Model name
        detail: If True (default), return only URL views for an individual object.
            Otherwise, return only list views.
    """
    paths = []

    # Retrieve registered views for this model
    try:
        views = [
            view for view in registry['views'][app_label][model_name]
            if view['detail'] == detail
        ]
    except KeyError:
        # No views have been registered for this model
        return []

    for config in views:
        # Import the view class or function
        if type(config['view']) is str:
            view_ = import_string(config['view'])
        else:
            view_ = config['view']
        if issubclass(view_, View):
            view_ = view_.as_view()

        # Create a path to the view
        name = f"{model_name}_{config['name']}" if config['name'] else model_name
        url_path = f"{config['path']}/" if config['path'] else ''
        paths.append(
            path(url_path, view_, name=name, kwargs=config['kwargs'])
        )

    return paths
