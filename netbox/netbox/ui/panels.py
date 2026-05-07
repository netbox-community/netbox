from django.apps import apps
from django.template.loader import render_to_string
from django.utils.translation import gettext_lazy as _

from netbox.ui import attrs
from netbox.ui.actions import CopyContent
from utilities.data import resolve_attr_path
from utilities.permissions import get_permission_for_model
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
    'TextCodePanel',
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
        if actions is not None:
            self.actions = actions
        self.actions = list(self.actions) if self.actions else []

    def get_context(self, context):
        """
        Return the context data to be used when rendering the panel.

        Parameters:
            context (dict): The template context
        """
        return {
            'request': context.get('request'),
            'object': context.get('object'),
            'perms': context.get('perms'),
            'title': self.title,
            'actions': self.actions,
            'panel_class': self.__class__.__name__,
        }

    def should_render(self, context):
        """
        Determines whether the panel should render on the page. (Default: True)

        Parameters:
            context (dict): The panel's prepared context (the return value of get_context())
        """
        return True

    def render(self, context):
        """
        Render the panel as HTML.

        Parameters:
            context (dict): The template context
        """
        ctx = self.get_context(context)
        if not self.should_render(ctx):
            return ''
        return render_to_string(self.template_name, ctx, request=ctx.get('request'))


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
        if self.title is not None:
            title_ = self.title
        elif obj is not None:
            title_ = title(obj._meta.verbose_name)
        else:
            title_ = None
        return {
            **super().get_context(context),
            'title': title_,
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
                    'value': attr.render(ctx['object'], {'name': name, 'perms': ctx['perms']}),
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
        ctx = super().get_context(context)
        return {
            **ctx,
            'comments': getattr(ctx['object'], self.field_name, None),
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
        ctx = super().get_context(context)
        return {
            **ctx,
            'data': getattr(ctx['object'], self.field_name, None),
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
        include_columns (list): A list of column names to always display (overrides user preferences)
        exclude_columns (list): A list of column names to hide from the table (overrides user preferences)
    """
    template_name = 'ui/panels/objects_table.html'
    title = None

    def __init__(self, model, filters=None, include_columns=None, exclude_columns=None, **kwargs):
        super().__init__(**kwargs)

        # Validate the model label format
        if '.' not in model:
            raise ValueError(f"Invalid model label: {model}")
        self.model_label = model
        self.filters = filters or {}
        self.include_columns = include_columns or []
        self.exclude_columns = exclude_columns or []

    @property
    def model(self):
        try:
            return apps.get_model(self.model_label)
        except LookupError:
            raise ValueError(f"Invalid model label: {self.model_label}")

    def get_context(self, context):
        model = self.model

        # If no title is specified, derive one from the model name
        panel_title = self.title or title(model._meta.verbose_name_plural)

        url_params = {
            k: v(context) if callable(v) else v for k, v in self.filters.items()
        }
        if 'return_url' not in url_params and 'object' in context:
            url_params['return_url'] = context['object'].get_absolute_url()
        if self.include_columns:
            url_params['include_columns'] = ','.join(self.include_columns)
        if self.exclude_columns:
            url_params['exclude_columns'] = ','.join(self.exclude_columns)
        return {
            **super().get_context(context),
            'title': panel_title,
            'viewname': get_viewname(model, 'list'),
            'url_params': dict_to_querydict(url_params),
        }

    def should_render(self, context):
        """
        Hide the panel if the user does not have view permission for the panel's model.
        """
        request = context.get('request')
        if request is None:
            return True

        return request.user.has_perm(get_permission_for_model(self.model, 'view'))


class TemplatePanel(Panel):
    """
    A panel which renders custom content using an HTML template.

    Parameters:
        template_name (str): The name of the template to render
    """
    def __init__(self, template_name, **kwargs):
        self.template_name = template_name
        super().__init__(**kwargs)

    def get_context(self, context):
        # Pass the entire context to the template, but let the panel's own context take precedence
        # for panel-specific variables (title, actions, panel_class)
        return {
            **context.flatten(),
            **super().get_context(context)
        }


class TextCodePanel(ObjectPanel):
    """
    A panel displaying a text field as a pre-formatted code block.
    """
    template_name = 'ui/panels/text_code.html'

    def __init__(self, field_name, show_sync_warning=False, **kwargs):
        super().__init__(**kwargs)
        self.field_name = field_name
        self.show_sync_warning = show_sync_warning

    def get_context(self, context):
        ctx = super().get_context(context)
        return {
            **ctx,
            'show_sync_warning': self.show_sync_warning,
            'value': getattr(ctx['object'], self.field_name, None),
        }


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
        # Override the default render() method to simply embed rendered plugin content
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
        return {
            **super().get_context(context),
            'table': self._resolve_table(context),
        }

    def should_render(self, context):
        return context.get('table') is not None
