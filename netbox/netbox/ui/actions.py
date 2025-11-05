from urllib.parse import urlencode

from django.apps import apps
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from utilities.permissions import get_permission_for_model
from utilities.views import get_viewname

__all__ = (
    'AddObject',
    'PanelAction',
)


class PanelAction:
    """
    A link (typically a button) within a panel to perform some associated action, such as adding an object.

    Attributes:
        template_name: The name of the template to render
        label: The default human-friendly button text
        button_class: Bootstrap CSS class for the button
        button_icon: Name of the button's MDI icon
    """
    template_name = 'ui/actions/link.html'
    label = None
    button_class = 'primary'
    button_icon = None

    # TODO: Refactor URL parameters to AddObject
    def __init__(self, view_name, view_kwargs=None, url_params=None, permissions=None, label=None):
        """
        Initialize a new PanelAction.

        Parameters:
            view_name: Name of the view to which the action will link
            view_kwargs: Additional keyword arguments to pass to the view when resolving its URL
            url_params: A dictionary of arbitrary URL parameters to append to the action's URL
            permissions: A list of permissions required to display the action
            label: The human-friendly button text
        """
        self.view_name = view_name
        self.view_kwargs = view_kwargs or {}
        self.url_params = url_params or {}
        self.permissions = permissions
        if label is not None:
            self.label = label

    def get_url(self, context):
        """
        Resolve the URL for the action from its view name and kwargs. Append any additional URL parameters.

        Parameters:
            context: The template context
        """
        url = reverse(self.view_name, kwargs=self.view_kwargs)
        if self.url_params:
            # If the param value is callable, call it with the context and save the result.
            url_params = {
                k: v(context) if callable(v) else v for k, v in self.url_params.items()
            }
            # Set the return URL if not already set and an object is available.
            if 'return_url' not in url_params and 'object' in context:
                url_params['return_url'] = context['object'].get_absolute_url()
            url = f'{url}?{urlencode(url_params)}'
        return url

    def render(self, context):
        """
        Render the action as HTML.

        Parameters:
            context: The template context
        """
        # Enforce permissions
        user = context['request'].user
        if not user.has_perms(self.permissions):
            return ''

        return render_to_string(self.template_name, {
            'url': self.get_url(context),
            'label': self.label,
            'button_class': self.button_class,
            'button_icon': self.button_icon,
        })


class AddObject(PanelAction):
    """
    An action to add a new object.
    """
    label = _('Add')
    button_icon = 'plus-thick'

    def __init__(self, model, url_params=None, label=None):
        """
        Initialize a new AddObject action.

        Parameters:
            model: The dotted label of the model to be added (e.g. "dcim.site")
            url_params: A dictionary of arbitrary URL parameters to append to the resolved URL
            label: The human-friendly button text
        """
        # Resolve the model class from its app.name label
        try:
            app_label, model_name = model.split('.')
            model = apps.get_model(app_label, model_name)
        except (ValueError, LookupError):
            raise ValueError(f"Invalid model label: {model}")
        view_name = get_viewname(model, 'add')

        super().__init__(view_name=view_name, label=label, url_params=url_params)

        # Require "add" permission on the model
        self.permissions = [get_permission_for_model(model, 'add')]


class CopyContent:
    """
    An action to copy the contents of a panel to the clipboard.
    """
    template_name = 'ui/actions/copy_content.html'
    label = _('Copy')
    button_class = 'primary'
    button_icon = 'content-copy'

    def __init__(self, target_id):
        self.target_id = target_id

    def render(self, context):
        """
        Render the action as HTML.

        Parameters:
            context: The template context
        """
        return render_to_string(self.template_name, {
            'target_id': self.target_id,
            'label': self.label,
            'button_class': self.button_class,
            'button_icon': self.button_icon,
        })
