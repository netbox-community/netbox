from abc import ABC, ABCMeta

from django.apps import apps
from django.template.loader import render_to_string
from django.utils.translation import gettext_lazy as _

from netbox.ui import attrs
from netbox.ui.actions import CopyContent
from utilities.querydict import dict_to_querydict
from utilities.string import title
from utilities.templatetags.plugins import _get_registered_content
from utilities.views import get_viewname

__all__ = (
    'CommentsPanel',
    'JSONPanel',
    'NestedGroupObjectPanel',
    'ObjectPanel',
    'ObjectsTablePanel',
    'OrganizationalObjectPanel',
    'RelatedObjectsPanel',
    'Panel',
    'PluginContentPanel',
    'TemplatePanel',
)


class Panel(ABC):
    """
    A block of content rendered within an HTML template.

    Attributes:
        template_name: The name of the template to render
        title: The human-friendly title of the panel
        actions: A list of PanelActions to include in the panel header
    """
    template_name = None
    title = None
    actions = None

    def __init__(self, title=None, actions=None):
        """
        Instantiate a new Panel.

        Parameters:
            title: The human-friendly title of the panel
            actions: A list of PanelActions to include in the panel header
        """
        if title is not None:
            self.title = title
        self.actions = actions or []

    def get_context(self, context):
        """
        Return the context data to be used when rendering the panel.

        Parameters:
            context: The template context
        """
        return {
            'request': context.get('request'),
            'object': context.get('object'),
            'title': self.title,
            'actions': self.actions,
        }

    def render(self, context):
        """
        Render the panel as HTML.

        Parameters:
            context: The template context
        """
        return render_to_string(self.template_name, self.get_context(context))


class ObjectPanelMeta(ABCMeta):

    def __new__(mcls, name, bases, namespace, **kwargs):
        declared = {}

        # Walk MRO parents (excluding `object`) for declared attributes
        for base in reversed([b for b in bases if hasattr(b, "_attrs")]):
            for key, attr in getattr(base, '_attrs', {}).items():
                if key not in declared:
                    declared[key] = attr

        # Add local declarations in the order they appear in the class body
        for key, attr in namespace.items():
            if isinstance(attr, attrs.Attr):
                declared[key] = attr

        namespace['_attrs'] = declared

        # Remove Attrs from the class namespace to keep things tidy
        local_items = [key for key, attr in namespace.items() if isinstance(attr, attrs.Attr)]
        for key in local_items:
            namespace.pop(key)

        cls = super().__new__(mcls, name, bases, namespace, **kwargs)
        return cls


class ObjectPanel(Panel, metaclass=ObjectPanelMeta):
    """
    A panel which displays selected attributes of an object.

    Attributes:
        template_name: The name of the template to render
        accessor: The name of the attribute on the object
    """
    template_name = 'ui/panels/object.html'
    accessor = None

    def __init__(self, accessor=None, only=None, exclude=None, **kwargs):
        """
        Instantiate a new ObjectPanel.

        Parameters:
            accessor: The name of the attribute on the object
            only: If specified, only attributes in this list will be displayed
            exclude: If specified, attributes in this list will be excluded from display
        """
        super().__init__(**kwargs)

        if accessor is not None:
            self.accessor = accessor

        # Set included/excluded attributes
        if only is not None and exclude is not None:
            raise ValueError("only and exclude cannot both be specified.")
        self.only = only or []
        self.exclude = exclude or []

    def get_context(self, context):
        """
        Return the context data to be used when rendering the panel.

        Parameters:
            context: The template context
        """
        # Determine which attributes to display in the panel based on only/exclude args
        attr_names = set(self._attrs.keys())
        if self.only:
            attr_names &= set(self.only)
        elif self.exclude:
            attr_names -= set(self.exclude)

        obj = getattr(context['object'], self.accessor) if self.accessor else context['object']

        return {
            **super().get_context(context),
            'title': self.title or title(obj._meta.verbose_name),
            'attrs': [
                {
                    'label': attr.label or title(name),
                    'value': attr.render(obj, {'name': name}),
                } for name, attr in self._attrs.items() if name in attr_names
            ],
        }


class OrganizationalObjectPanel(ObjectPanel, metaclass=ObjectPanelMeta):
    """
    An ObjectPanel with attributes common to OrganizationalModels.
    """
    name = attrs.TextAttr('name', label=_('Name'))
    description = attrs.TextAttr('description', label=_('Description'))


class NestedGroupObjectPanel(OrganizationalObjectPanel, metaclass=ObjectPanelMeta):
    """
    An ObjectPanel with attributes common to NestedGroupObjects.
    """
    parent = attrs.NestedObjectAttr('parent', label=_('Parent'), linkify=True)


class CommentsPanel(Panel):
    """
    A panel which displays comments associated with an object.
    """
    template_name = 'ui/panels/comments.html'
    title = _('Comments')


class RelatedObjectsPanel(Panel):
    """
    A panel which displays the types and counts of related objects.
    """
    template_name = 'ui/panels/related_objects.html'
    title = _('Related Objects')

    def get_context(self, context):
        """
        Return the context data to be used when rendering the panel.

        Parameters:
            context: The template context
        """
        return {
            **super().get_context(context),
            'related_models': context.get('related_models'),
        }


class ObjectsTablePanel(Panel):
    """
    A panel which displays a table of objects (rendered via HTMX).
    """
    template_name = 'ui/panels/objects_table.html'
    title = None

    def __init__(self, model, filters=None, **kwargs):
        """
        Instantiate a new ObjectsTablePanel.

        Parameters:
            model: The dotted label of the model to be added (e.g. "dcim.site")
            filters: A dictionary of arbitrary URL parameters to append to the table's URL
        """
        super().__init__(**kwargs)

        # Resolve the model class from its app.name label
        try:
            app_label, model_name = model.split('.')
            self.model = apps.get_model(app_label, model_name)
        except (ValueError, LookupError):
            raise ValueError(f"Invalid model label: {model}")

        self.filters = filters or {}

        # If no title is specified, derive one from the model name
        if self.title is None:
            self.title = title(self.model._meta.verbose_name_plural)

    def get_context(self, context):
        """
        Return the context data to be used when rendering the panel.

        Parameters:
            context: The template context
        """
        url_params = {
            k: v(context) if callable(v) else v for k, v in self.filters.items()
        }
        if 'return_url' not in url_params and 'object' in context:
            url_params['return_url'] = context['object'].get_absolute_url()
        return {
            **super().get_context(context),
            'viewname': get_viewname(self.model, 'list'),
            'url_params': dict_to_querydict(url_params),
        }


class JSONPanel(Panel):
    """
    A panel which renders formatted JSON data.
    """
    template_name = 'ui/panels/json.html'

    def __init__(self, field_name, copy_button=True, **kwargs):
        """
        Instantiate a new JSONPanel.

        Parameters:
            field_name: The name of the JSON field on the object
            copy_button: Set to True (default) to include a copy-to-clipboard button
        """
        super().__init__(**kwargs)
        self.field_name = field_name

        if copy_button:
            self.actions.append(
                CopyContent(f'panel_{field_name}'),
            )

    def get_context(self, context):
        """
        Return the context data to be used when rendering the panel.

        Parameters:
            context: The template context
        """
        return {
            **super().get_context(context),
            'data': getattr(context['object'], self.field_name),
            'field_name': self.field_name,
        }


class TemplatePanel(Panel):
    """
    A panel which renders content using an HTML template.
    """
    def __init__(self, template_name, **kwargs):
        """
        Instantiate a new TemplatePanel.

        Parameters:
            template_name: The name of the template to render
        """
        super().__init__(**kwargs)
        self.template_name = template_name

    def render(self, context):
        # Pass the entire context to the template
        return render_to_string(self.template_name, context.flatten())


class PluginContentPanel(Panel):
    """
    A panel which displays embedded plugin content.

    Parameters:
        method: The name of the plugin method to render (e.g. left_page)
    """
    def __init__(self, method, **kwargs):
        super().__init__(**kwargs)
        self.method = method

    def render(self, context):
        obj = context.get('object')
        return _get_registered_content(obj, self.method, context)
