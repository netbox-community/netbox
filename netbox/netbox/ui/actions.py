from urllib.parse import urlencode

from django.apps import apps
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from utilities.permissions import get_permission_for_model
from utilities.views import get_viewname

__all__ = (
    'AddObject',
    'PanelAction',
)


class PanelAction:
    label = None
    button_class = 'primary'
    button_icon = None

    def __init__(self, view_name, view_kwargs=None, url_params=None, permissions=None, label=None):
        self.view_name = view_name
        self.view_kwargs = view_kwargs
        self.url_params = url_params or {}
        self.permissions = permissions
        if label is not None:
            self.label = label

    def get_url(self, obj):
        url = reverse(self.view_name, kwargs=self.view_kwargs or {})
        if self.url_params:
            url_params = {
                k: v(obj) if callable(v) else v for k, v in self.url_params.items()
            }
            url = f'{url}?{urlencode(url_params)}'
        return url

    def get_context(self, obj):
        return {
            'url': self.get_url(obj),
            'label': self.label,
            'button_class': self.button_class,
            'button_icon': self.button_icon,
        }


class AddObject(PanelAction):
    label = _('Add')
    button_icon = 'plus-thick'

    def __init__(self, model, label=None, url_params=None):
        app_label, model_name = model.split('.')
        model = apps.get_model(app_label, model_name)
        view_name = get_viewname(model, 'add')
        super().__init__(view_name=view_name, label=label, url_params=url_params)
        self.permissions = [get_permission_for_model(model, 'add')]
