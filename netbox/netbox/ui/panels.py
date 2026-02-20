from django.apps import apps
from django.template.loader import render_to_string
from django.utils.translation import gettext_lazy as _

from netbox.ui import attrs
from netbox.ui.actions import CopyContent
from utilities.data import resolve_attr_path
from utilities.querydict import dict_to_querydict
from utilities.string import title
from utilities.templatetags.plugins import _get_registered_content
from utilities.views import get_viewname

__all__ = (
    'CommentsPanel',
    'ContextTablePanel',
    'JSONPanel',
    'NestedGroupObjectPanel',
    'ObjectAttributesPanel',
    'ObjectPanel',
    'ObjectsTablePanel',
    'OrganizationalObjectPanel',
    'Panel',
    'PluginContentPanel',
    'RelatedObjectsPanel',
    'TemplatePanel',
)


#
# Base classes
#

class Panel:
    """
    A block of content rendered within an HTML template.

    Panels are arranged within rows and columns, (generally) render as discrete "cards" within the user interface. Each
    panel has a title and may have one or more actions associated with it, which will be rendered as hyperlinks in the
    top right corner of the card.

    Attributes:
        template_name (str): The name of the template used to render the panel

    Parameters:
        title (str): The human-friendly title of the panel
        actions (list): An iterable of PanelActions to include in the panel header
    """
    template_name = None
    title = None
    actions = None

    def __init__(self, title=None, actions=None):
        if title is not None:
            self.title = title
        self.actions = actions or self.actions or []

    def get_context(self, context):
        """
        Return the context data to be used when rendering the panel.

        Parameters:
            context (dict): The template context
        """
        return {
            'request': context.get('request'),
            'object': context.get('object'),
            'title': self.title,
            'actions': self.actions,
            'panel_class': self.__class__.__name__,
        }

    def render(self, context):
        """
        Render the panel as HTML.

        Parameters:
            context (dict): The template context
        """
        return render_to_string(self.template_name, self.get_context(context))


#
# Object-specific panels
#

class ObjectPanel(Panel):
    """
    Base class for object-specific panels.

    Parameters:
        accessor (str): The dotted path in context data to the object being rendered (default: "object")
    """
    accessor = 'object'

    def __init__(self, accessor=None, **kwargs):
        super().__init__(**kwargs)

        if accessor is not None:
            self.accessor = accessor

    def get_context(self, context):
        obj = resolve_attr_path(context, self.accessor)
        return {
            **super().get_context(context),
            'title': self.title or title(obj._meta.verbose_name),
            'object': obj,
        }


class ObjectAttributesPanelMeta(type):

    def __new__(mcls, name, bases, namespace, **kwargs):
        declared = {}

        # Walk MRO parents (excluding `object`) for declared attributes
        for base in reversed([b for b in bases if hasattr(b, "_attrs")]):
            for key, attr in getattr(base, '_attrs', {}).items():
                if key not in declared:
                    declared[key] = attr

        # Add local declarations in the order they appear in the class body
        for key, attr in namespace.items():
            if isinstance(attr, attrs.ObjectAttribute):
                declared[key] = attr

        namespace['_attrs'] = declared

        # Remove Attrs from the class namespace to keep things tidy
        local_items = [key for key, attr in namespace.items() if isinstance(attr, attrs.ObjectAttribute)]
        for key in local_items:
            namespace.pop(key)

        cls = super().__new__(mcls, name, bases, namespace, **kwargs)
        return cls


class ObjectAttributesPanel(ObjectPanel, metaclass=ObjectAttributesPanelMeta):
    """
    A panel which displays selected attributes of an object.

    Attributes are added to the panel by declaring ObjectAttribute instances in the class body (similar to fields on
    a Django form). Attributes are displayed in the order they are declared.

    Note that the `only` and `exclude` parameters are mutually exclusive.

    Parameters:
            only (list): If specified, only attributes in this list will be displayed
            exclude (list): If specified, attributes in this list will be excluded from display
    """
    template_name = 'ui/panels/object_attributes.html'

    def __init__(self, only=None, exclude=None, **kwargs):
        super().__init__(**kwargs)

        # Set included/excluded attributes
        if only is not None and exclude is not None:
            raise ValueError("only and exclude cannot both be specified.")
        self.only = only or []
        self.exclude = exclude or []

    @staticmethod
    def _name_to_label(name):
        """
        Format an attribute's name to be presented as a human-friendly label.
        """
        label = name[:1].upper() + name[1:]
        label = label.replace('_', ' ')
        return _(label)

    def get_context(self, context):
        # Determine which attributes to display in the panel based on only/exclude args
        attr_names = set(self._attrs.keys())
        if self.only:
            attr_names &= set(self.only)
        elif self.exclude:
            attr_names -= set(self.exclude)

        ctx = super().get_context(context)

        return {
            **ctx,
            'attrs': [
                {
                    'label': attr.label or self._name_to_label(name),
                    'value': attr.render(ctx['object'], {'name': name}),
                } for name, attr in self._attrs.items() if name in attr_names
            ],
        }


class OrganizationalObjectPanel(ObjectAttributesPanel, metaclass=ObjectAttributesPanelMeta):
    """
    An ObjectPanel with attributes common to OrganizationalModels. Includes `name` and `description` attributes.
    """
    name = attrs.TextAttr('name', label=_('Name'))
    description = attrs.TextAttr('description', label=_('Description'))


class NestedGroupObjectPanel(ObjectAttributesPanel, metaclass=ObjectAttributesPanelMeta):
    """
    An ObjectPanel with attributes common to NestedGroupObjects. Includes the `parent` attribute.
    """
    parent = attrs.NestedObjectAttr('parent', label=_('Parent'), linkify=True)
    name = attrs.TextAttr('name', label=_('Name'))
    description = attrs.TextAttr('description', label=_('Description'))


class CommentsPanel(ObjectPanel):
    """
    A panel which displays comments associated with an object.

    Parameters:
        field_name (str): The name of the comment field on the object (default: "comments")
    """
    template_name = 'ui/panels/comments.html'
    title = _('Comments')

    def __init__(self, field_name='comments', **kwargs):
        super().__init__(**kwargs)
        self.field_name = field_name

    def get_context(self, context):
        return {
            **super().get_context(context),
            'comments': getattr(context['object'], self.field_name),
        }


class JSONPanel(ObjectPanel):
    """
    A panel which renders formatted JSON data from an object's JSONField.

    Parameters:
        field_name (str): The name of the JSON field on the object
        copy_button (bool): Set to True (default) to include a copy-to-clipboard button
    """
    template_name = 'ui/panels/json.html'

    def __init__(self, field_name, copy_button=True, **kwargs):
        super().__init__(**kwargs)
        self.field_name = field_name

        if copy_button:
            self.actions.append(CopyContent(f'panel_{field_name}'))

    def get_context(self, context):
        return {
            **super().get_context(context),
            'data': getattr(context['object'], self.field_name),
            'field_name': self.field_name,
        }


#
# Miscellaneous panels
#

class RelatedObjectsPanel(Panel):
    """
    A panel which displays the types and counts of related objects.
    """
    template_name = 'ui/panels/related_objects.html'
    title = _('Related Objects')

    def get_context(self, context):
        return {
            **super().get_context(context),
            'related_models': context.get('related_models'),
        }


class ObjectsTablePanel(Panel):
    """
    A panel which displays a table of objects (rendered via HTMX).

    Parameters:
        model (str): The dotted label of the model to be added (e.g. "dcim.site")
        filters (dict): A dictionary of arbitrary URL parameters to append to the table's URL. If the value of a key is
            a callable, it will be passed the current template context.
    """
    template_name = 'ui/panels/objects_table.html'
    title = None

    def __init__(self, model, filters=None, **kwargs):
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


class TemplatePanel(Panel):
    """
    A panel which renders custom content using an HTML template.

    Parameters:
        template_name (str): The name of the template to render
    """
    def __init__(self, template_name, **kwargs):
        super().__init__(**kwargs)
        self.template_name = template_name

    def render(self, context):
        # Pass the entire context to the template
        return render_to_string(self.template_name, context.flatten())


class PluginContentPanel(Panel):
    """
    A panel which displays embedded plugin content.

    Parameters:
        method (str): The name of the plugin method to render (e.g. "left_page")
    """
    def __init__(self, method, **kwargs):
        super().__init__(**kwargs)
        self.method = method

    def render(self, context):
        obj = context.get('object')
        return _get_registered_content(obj, self.method, context)


class ContextTablePanel(ObjectPanel):
    """
    A panel which renders a django-tables2/NetBoxTable instance provided
    via the view's extra context.

    This is useful when you already have a fully constructed table
    (custom queryset, special columns, no list view) and just want to
    render it inside a declarative layout panel.

    Parameters:
        table (str | callable): Either the context key holding the table
            (e.g. "vlan_table") or a callable which accepts the template
            context and returns a table instance.
    """
    template_name = 'ui/panels/context_table.html'

    def __init__(self, table, **kwargs):
        super().__init__(**kwargs)
        self.table = table

    def _resolve_table(self, context):
        if callable(self.table):
            return self.table(context)
        return context.get(self.table)

    def get_context(self, context):
        table = self._resolve_table(context)
        return {
            **super().get_context(context),
            'table': table,
        }

    def render(self, context):
        table = self._resolve_table(context)
        if table is None:
            return ''
        return super().render(context)
