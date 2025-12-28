from urllib.parse import urlencode

from django.apps import apps
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from utilities.permissions import get_permission_for_model
from utilities.views import get_viewname

__all__ = (
    'AddObject',
    'CopyContent',
    'LinkAction',
    'PanelAction',
)


class PanelAction:
    """
    A link (typically a button) within a panel to perform some associated action, such as adding an object.

    Attributes:
        template_name (str): The name of the template to render

    Parameters:
        label (str): The human-friendly button text
        permissions (list): An iterable of permissions required to display the action
        button_class (str): Bootstrap CSS class for the button
        button_icon (str): Name of the button's MDI icon
    """
    template_name = None

    def __init__(self, label, permissions=None, button_class='primary', button_icon=None):
        self.label = label
        self.permissions = permissions
        self.button_class = button_class
        self.button_icon = button_icon

    def get_context(self, context):
        """
        Return the template context used to render the action element.

        Parameters:
            context (dict): The template context
        """
        return {
            'label': self.label,
            'button_class': self.button_class,
            'button_icon': self.button_icon,
        }

    def render(self, context):
        """
        Render the action as HTML.

        Parameters:
            context (dict): The template context
        """
        # Enforce permissions
        user = context['request'].user
        if not user.has_perms(self.permissions):
            return ''

        return render_to_string(self.template_name, self.get_context(context))


class LinkAction(PanelAction):
    """
    A hyperlink (typically a button) within a panel to perform some associated action, such as adding an object.

    Parameters:
        view_name (str): Name of the view to which the action will link
        view_kwargs (dict): Additional keyword arguments to pass to `reverse()` when resolving the URL
        url_params (dict): A dictionary of arbitrary URL parameters to append to the action's URL. If the value of a key
            is a callable, it will be passed the current template context.
    """
    template_name = 'ui/actions/link.html'

    def __init__(self, view_name, view_kwargs=None, url_params=None, **kwargs):
        super().__init__(**kwargs)
        self.view_name = view_name
        self.view_kwargs = view_kwargs or {}
        self.url_params = url_params or {}

    def get_url(self, context):
        """
        Resolve the URL for the action from its view name and kwargs. Append any additional URL parameters.

        Parameters:
            context (dict): The template context
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

    def get_context(self, context):
        return {
            **super().get_context(context),
            'url': self.get_url(context),
        }


class AddObject(LinkAction):
    """
    An action to add a new object.

    Parameters:
        model (str): The dotted label of the model to be added (e.g. "dcim.site")
        url_params (dict): A dictionary of arbitrary URL parameters to append to the resolved URL
    """
    def __init__(self, model, url_params=None, **kwargs):
        # Resolve the model class from its app.name label
        try:
            app_label, model_name = model.split('.')
            model = apps.get_model(app_label, model_name)
        except (ValueError, LookupError):
            raise ValueError(f"Invalid model label: {model}")
        view_name = get_viewname(model, 'add')

        kwargs.setdefault('label', _('Add'))
        kwargs.setdefault('button_icon', 'plus-thick')
        kwargs.setdefault('permissions', [get_permission_for_model(model, 'add')])

        super().__init__(view_name=view_name, url_params=url_params, **kwargs)


class CopyContent(PanelAction):
    """
    An action to copy the contents of a panel to the clipboard.

    Parameters:
        target_id (str): The ID of the target element containing the content to be copied
    """
    template_name = 'ui/actions/copy_content.html'

    def __init__(self, target_id, **kwargs):
        kwargs.setdefault('label', _('Copy'))
        kwargs.setdefault('button_icon', 'content-copy')
        super().__init__(**kwargs)
        self.target_id = target_id

    def render(self, context):
        return render_to_string(self.template_name, {
            'target_id': self.target_id,
            'label': self.label,
            'button_class': self.button_class,
            'button_icon': self.button_icon,
        })
