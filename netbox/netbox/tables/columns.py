from dataclasses import dataclass
from typing import Optional

import django_tables2 as tables
from django.conf import settings
from django.contrib.auth.models import AnonymousUser
from django.db.models import DateField, DateTimeField
from django.template import Context, Template
from django.urls import reverse
from django.utils.formats import date_format
from django.utils.safestring import mark_safe
from django_tables2.columns import library
from django_tables2.utils import Accessor

from extras.choices import CustomFieldTypeChoices
from utilities.utils import content_type_identifier, content_type_name, get_viewname

__all__ = (
    'ActionsColumn',
    'BooleanColumn',
    'ChoiceFieldColumn',
    'ColorColumn',
    'ColoredLabelColumn',
    'ContentTypeColumn',
    'ContentTypesColumn',
    'CustomFieldColumn',
    'CustomLinkColumn',
    'LinkedCountColumn',
    'MarkdownColumn',
    'MPTTColumn',
    'TagColumn',
    'TemplateColumn',
    'ToggleColumn',
    'UtilizationColumn',
)


@library.register
class DateColumn(tables.DateColumn):
    """
    Overrides the default implementation of DateColumn to better handle null values, returning a default value for
    tables and null when exporting data. It is registered in the tables library to use this class instead of the
    default, making this behavior consistent in all fields of type DateField.
    """

    def value(self, value):
        return value

    @classmethod
    def from_field(cls, field, **kwargs):
        if isinstance(field, DateField):
            return cls(**kwargs)


@library.register
class DateTimeColumn(tables.DateTimeColumn):
    """
    Overrides the default implementation of DateTimeColumn to better handle null values, returning a default value for
    tables and null when exporting data. It is registered in the tables library to use this class instead of the
    default, making this behavior consistent in all fields of type DateTimeField.
    """

    def value(self, value):
        if value:
            return date_format(value, format="SHORT_DATETIME_FORMAT")
        return None

    @classmethod
    def from_field(cls, field, **kwargs):
        if isinstance(field, DateTimeField):
            return cls(**kwargs)


class ToggleColumn(tables.CheckBoxColumn):
    """
    Extend CheckBoxColumn to add a "toggle all" checkbox in the column header.
    """
    def __init__(self, *args, **kwargs):
        default = kwargs.pop('default', '')
        visible = kwargs.pop('visible', False)
        if 'attrs' not in kwargs:
            kwargs['attrs'] = {
                'td': {
                    'class': 'min-width',
                },
                'input': {
                    'class': 'form-check-input'
                }
            }
        super().__init__(*args, default=default, visible=visible, **kwargs)

    @property
    def header(self):
        return mark_safe('<input type="checkbox" class="toggle form-check-input" title="Toggle All" />')


class BooleanColumn(tables.Column):
    """
    Custom implementation of BooleanColumn to render a nicely-formatted checkmark or X icon instead of a Unicode
    character.
    """
    def render(self, value):
        if value:
            rendered = '<span class="text-success"><i class="mdi mdi-check-bold"></i></span>'
        elif value is None:
            rendered = '<span class="text-muted">&mdash;</span>'
        else:
            rendered = '<span class="text-danger"><i class="mdi mdi-close-thick"></i></span>'
        return mark_safe(rendered)

    def value(self, value):
        return str(value)


class TemplateColumn(tables.TemplateColumn):
    """
    Overrides django-tables2's stock TemplateColumn class to render a placeholder symbol if the returned value
    is an empty string.
    """
    PLACEHOLDER = mark_safe('&mdash;')

    def render(self, *args, **kwargs):
        ret = super().render(*args, **kwargs)
        if not ret.strip():
            return self.PLACEHOLDER
        return ret

    def value(self, **kwargs):
        ret = super().value(**kwargs)
        if ret == self.PLACEHOLDER:
            return ''
        return ret


@dataclass
class ActionsItem:
    title: str
    icon: str
    permission: Optional[str] = None


class ActionsColumn(tables.Column):
    """
    A dropdown menu which provides edit, delete, and changelog links for an object. Can optionally include
    additional buttons rendered from a template string.

    :param sequence: The ordered list of dropdown menu items to include
    :param extra_buttons: A Django template string which renders additional buttons preceding the actions dropdown
    """
    attrs = {'td': {'class': 'text-end text-nowrap noprint'}}
    empty_values = ()
    actions = {
        'edit': ActionsItem('Edit', 'pencil', 'change'),
        'delete': ActionsItem('Delete', 'trash-can-outline', 'delete'),
        'changelog': ActionsItem('Changelog', 'history'),
    }

    def __init__(self, *args, sequence=('edit', 'delete', 'changelog'), extra_buttons='', **kwargs):
        super().__init__(*args, **kwargs)

        self.extra_buttons = extra_buttons

        # Determine which actions to enable
        self.actions = {
            name: self.actions[name] for name in sequence
        }

    def header(self):
        return ''

    def render(self, record, table, **kwargs):
        # Skip dummy records (e.g. available VLANs) or those with no actions
        if not getattr(record, 'pk', None) or not self.actions:
            return ''

        model = table.Meta.model
        request = getattr(table, 'context', {}).get('request')
        url_appendix = f'?return_url={request.path}' if request else ''

        links = []
        user = getattr(request, 'user', AnonymousUser())
        for action, attrs in self.actions.items():
            permission = f'{model._meta.app_label}.{attrs.permission}_{model._meta.model_name}'
            if attrs.permission is None or user.has_perm(permission):
                url = reverse(get_viewname(model, action), kwargs={'pk': record.pk})
                links.append(f'<li><a class="dropdown-item" href="{url}{url_appendix}">'
                             f'<i class="mdi mdi-{attrs.icon}"></i> {attrs.title}</a></li>')

        if not links:
            return ''

        menu = f'<span class="dropdown">' \
               f'<a class="btn btn-sm btn-secondary dropdown-toggle" href="#" type="button" data-bs-toggle="dropdown">' \
               f'<i class="mdi mdi-wrench"></i></a>' \
               f'<ul class="dropdown-menu">{"".join(links)}</ul></span>'

        # Render any extra buttons from template code
        if self.extra_buttons:
            template = Template(self.extra_buttons)
            context = getattr(table, "context", Context())
            context.update({'record': record})
            menu = template.render(context) + menu

        return mark_safe(menu)


class ChoiceFieldColumn(tables.Column):
    """
    Render a model's static ChoiceField with its value from `get_FOO_display()` as a colored badge. Background color is
    set by the instance's get_FOO_color() method, if defined.
    """
    DEFAULT_BG_COLOR = 'secondary'

    def render(self, record, bound_column, value):
        if value in self.empty_values:
            return self.default

        # Determine the background color to use (try calling object.get_FOO_color())
        try:
            bg_color = getattr(record, f'get_{bound_column.name}_color')()
        except AttributeError:
            bg_color = self.DEFAULT_BG_COLOR

        return mark_safe(f'<span class="badge bg-{bg_color}">{value}</span>')

    def value(self, value):
        return value


class ContentTypeColumn(tables.Column):
    """
    Display a ContentType instance.
    """
    def render(self, value):
        if value is None:
            return None
        return content_type_name(value)

    def value(self, value):
        if value is None:
            return None
        return content_type_identifier(value)


class ContentTypesColumn(tables.ManyToManyColumn):
    """
    Display a list of ContentType instances.
    """
    def __init__(self, separator=None, *args, **kwargs):
        # Use a line break as the default separator
        if separator is None:
            separator = mark_safe('<br />')
        super().__init__(separator=separator, *args, **kwargs)

    def transform(self, obj):
        return content_type_name(obj)

    def value(self, value):
        return ','.join([
            content_type_identifier(ct) for ct in self.filter(value)
        ])


class ColorColumn(tables.Column):
    """
    Display an arbitrary color value, specified in RRGGBB format.
    """
    def render(self, value):
        return mark_safe(
            f'<span class="color-label" style="background-color: #{value}">&nbsp;</span>'
        )

    def value(self, value):
        return f'#{value}'


class ColoredLabelColumn(tables.TemplateColumn):
    """
    Render a related object as a colored label. The related object must have a `color` attribute (specifying
    an RRGGBB value) and a `get_absolute_url()` method.
    """
    template_code = """
{% load helpers %}
  {% if value %}
  <span class="badge" style="color: {{ value.color|fgcolor }}; background-color: #{{ value.color }}">
    <a href="{{ value.get_absolute_url }}">{{ value }}</a>
  </span>
{% else %}
  &mdash;
{% endif %}
"""

    def __init__(self, *args, **kwargs):
        super().__init__(template_code=self.template_code, *args, **kwargs)

    def value(self, value):
        return str(value)


class LinkedCountColumn(tables.Column):
    """
    Render a count of related objects linked to a filtered URL.

    :param viewname: The view name to use for URL resolution
    :param view_kwargs: Additional kwargs to pass for URL resolution (optional)
    :param url_params: A dict of query parameters to append to the URL (e.g. ?foo=bar) (optional)
    """
    def __init__(self, viewname, *args, view_kwargs=None, url_params=None, default=0, **kwargs):
        self.viewname = viewname
        self.view_kwargs = view_kwargs or {}
        self.url_params = url_params
        super().__init__(*args, default=default, **kwargs)

    def render(self, record, value):
        if value:
            url = reverse(self.viewname, kwargs=self.view_kwargs)
            if self.url_params:
                url += '?' + '&'.join([
                    f'{k}={getattr(record, v) or settings.FILTERS_NULL_CHOICE_VALUE}'
                    for k, v in self.url_params.items()
                ])
            return mark_safe(f'<a href="{url}">{value}</a>')
        return value

    def value(self, value):
        return value


class TagColumn(tables.TemplateColumn):
    """
    Display a list of Tags assigned to the object.
    """
    template_code = """
    {% load helpers %}
    {% for tag in value.all %}
        {% tag tag url_name %}
    {% empty %}
        <span class="text-muted">&mdash;</span>
    {% endfor %}
    """

    def __init__(self, url_name=None):
        super().__init__(
            template_code=self.template_code,
            extra_context={'url_name': url_name}
        )

    def value(self, value):
        return ",".join([tag.name for tag in value.all()])


class CustomFieldColumn(tables.Column):
    """
    Display custom fields in the appropriate format.
    """
    def __init__(self, customfield, *args, **kwargs):
        self.customfield = customfield
        kwargs['accessor'] = Accessor(f'custom_field_data__{customfield.name}')
        if 'verbose_name' not in kwargs:
            kwargs['verbose_name'] = customfield.label or customfield.name

        super().__init__(*args, **kwargs)

    def render(self, value):
        if isinstance(value, list):
            return ', '.join(v for v in value)
        elif self.customfield.type == CustomFieldTypeChoices.TYPE_BOOLEAN and value is True:
            return mark_safe('<i class="mdi mdi-check-bold text-success"></i>')
        elif self.customfield.type == CustomFieldTypeChoices.TYPE_BOOLEAN and value is False:
            return mark_safe('<i class="mdi mdi-close-thick text-danger"></i>')
        elif self.customfield.type == CustomFieldTypeChoices.TYPE_URL:
            return mark_safe(f'<a href="{value}">{value}</a>')
        if value is not None:
            obj = self.customfield.deserialize(value)
            if hasattr(obj, 'get_absolute_url'):
                return mark_safe(f'<a href="{obj.get_absolute_url}">{obj}</a>')
            return obj
        return self.default

    def value(self, value):
        if isinstance(value, list):
            return ','.join(v for v in value)
        if value is not None:
            return value
        return self.default


class CustomLinkColumn(tables.Column):
    """
    Render a custom link as a table column.
    """
    def __init__(self, customlink, *args, **kwargs):
        self.customlink = customlink
        kwargs['accessor'] = Accessor('pk')
        if 'verbose_name' not in kwargs:
            kwargs['verbose_name'] = customlink.name

        super().__init__(*args, **kwargs)

    def render(self, record):
        try:
            rendered = self.customlink.render({'obj': record})
            if rendered:
                return mark_safe(f'<a href="{rendered["link"]}"{rendered["link_target"]}>{rendered["text"]}</a>')
        except Exception as e:
            return mark_safe(f'<span class="text-danger" title="{e}"><i class="mdi mdi-alert"></i> Error</span>')
        return ''

    def value(self, record):
        try:
            rendered = self.customlink.render({'obj': record})
            if rendered:
                return rendered['link']
        except Exception:
            pass
        return None


class MPTTColumn(tables.TemplateColumn):
    """
    Display a nested hierarchy for MPTT-enabled models.
    """
    template_code = """
        {% load helpers %}
        {% for i in record.level|as_range %}<i class="mdi mdi-circle-small"></i>{% endfor %}
        <a href="{{ record.get_absolute_url }}">{{ record.name }}</a>
    """

    def __init__(self, *args, **kwargs):
        super().__init__(
            template_code=self.template_code,
            orderable=False,
            attrs={'td': {'class': 'text-nowrap'}},
            *args,
            **kwargs
        )

    def value(self, value):
        return value


class UtilizationColumn(tables.TemplateColumn):
    """
    Display a colored utilization bar graph.
    """
    template_code = """{% load helpers %}{% if record.pk %}{% utilization_graph value %}{% endif %}"""

    def __init__(self, *args, **kwargs):
        super().__init__(template_code=self.template_code, *args, **kwargs)

    def value(self, value):
        return f'{value}%'


class MarkdownColumn(tables.TemplateColumn):
    """
    Render a Markdown string.
    """
    template_code = """
    {% if value %}
      {{ value|markdown }}
    {% else %}
      &mdash;
    {% endif %}
    """

    def __init__(self):
        super().__init__(
            template_code=self.template_code
        )

    def value(self, value):
        return value
