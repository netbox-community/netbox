from collections import namedtuple

import django_tables2 as tables
from django.conf import settings
from django.urls import reverse
from django.utils.safestring import mark_safe
from django_tables2.utils import Accessor

from extras.choices import CustomFieldTypeChoices
from utilities.utils import content_type_identifier, content_type_name

__all__ = (
    'ActionsColumn',
    'BooleanColumn',
    'ButtonsColumn',
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
    Overrides the stock TemplateColumn to render a placeholder if the returned value is an empty string.
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


ActionsMenuItem = namedtuple('ActionsMenuItem', ['title', 'icon', 'permission'])


class ActionsColumn(tables.Column):
    attrs = {'td': {'class': 'text-end noprint'}}
    empty_values = ()
    _actions = {
        'edit': ActionsMenuItem('Edit', 'pencil', 'change'),
        'delete': ActionsMenuItem('Delete', 'trash-can-outline', 'delete'),
        'changelog': ActionsMenuItem('Changelog', 'history', None),
    }

    def __init__(self, *args, actions=('edit', 'delete', 'changelog'), **kwargs):
        super().__init__(*args, **kwargs)

        # Determine which actions to enable
        self.actions = {
            name: self._actions[name] for name in actions
        }

    def header(self):
        return ''

    def render(self, record, table, **kwargs):
        # Skip dummy records (e.g. available VLANs) or those with no actions
        if not hasattr(record, 'pk') or not self.actions:
            return ''

        model = table.Meta.model
        viewname_base = f'{model._meta.app_label}:{model._meta.model_name}'
        request = getattr(table, 'context', {}).get('request')
        url_appendix = f'?return_url={request.path}' if request else ''

        links = []
        for action, attrs in self.actions.items():
            permission = f'{model._meta.app_label}.{attrs.permission}_{model._meta.model_name}'
            if attrs.permission is None or request.user.has_perm(permission):
                url = reverse(f'{viewname_base}_{action}', kwargs={'pk': record.pk})
                links.append(f'<li><a class="dropdown-item" href="{url}{url_appendix}">'
                             f'<i class="mdi mdi-{attrs.icon}"></i> {attrs.title}</a></li>')

        if not links:
            return ''

        menu = f'<div class="dropdown">' \
               f'<a class="btn btn-sm btn-outline-secondary dropdown-toggle" href="#" type="button" data-bs-toggle="dropdown">' \
               f'<i class="mdi mdi-wrench"></i></a>' \
               f'<ul class="dropdown-menu">{"".join(links)}</ul></div>'

        return mark_safe(menu)


class ButtonsColumn(tables.TemplateColumn):
    """
    Render edit, delete, and changelog buttons for an object.

    :param model: Model class to use for calculating URL view names
    :param prepend_content: Additional template content to render in the column (optional)
    """
    buttons = ('changelog', 'edit', 'delete')
    attrs = {'td': {'class': 'text-end text-nowrap noprint'}}
    # Note that braces are escaped to allow for string formatting prior to template rendering
    template_code = """
    {{% if "changelog" in buttons %}}
        <a href="{{% url '{app_label}:{model_name}_changelog' pk=record.pk %}}" class="btn btn-outline-dark btn-sm" title="Change log">
            <i class="mdi mdi-history"></i>
        </a>
    {{% endif %}}
    {{% if "edit" in buttons and perms.{app_label}.change_{model_name} %}}
        <a href="{{% url '{app_label}:{model_name}_edit' pk=record.pk %}}?return_url={{{{ request.path }}}}" class="btn btn-sm btn-warning" title="Edit">
            <i class="mdi mdi-pencil"></i>
        </a>
    {{% endif %}}
    {{% if "delete" in buttons and perms.{app_label}.delete_{model_name} %}}
        <a href="{{% url '{app_label}:{model_name}_delete' pk=record.pk %}}?return_url={{{{ request.path }}}}" class="btn btn-sm btn-danger" title="Delete">
            <i class="mdi mdi-trash-can-outline"></i>
        </a>
    {{% endif %}}
    """

    def __init__(self, model, *args, buttons=None, prepend_template=None, **kwargs):
        if prepend_template:
            prepend_template = prepend_template.replace('{', '{{')
            prepend_template = prepend_template.replace('}', '}}')
            self.template_code = prepend_template + self.template_code

        template_code = self.template_code.format(
            app_label=model._meta.app_label,
            model_name=model._meta.model_name,
            buttons=buttons
        )

        super().__init__(template_code=template_code, *args, **kwargs)

        # Exclude from export by default
        if 'exclude_from_export' not in kwargs:
            self.exclude_from_export = True

        self.extra_context.update({
            'buttons': buttons or self.buttons,
        })

    def header(self):
        return ''


class ChoiceFieldColumn(tables.Column):
    """
    Render a ChoiceField value inside a <span> indicating a particular CSS class. This is useful for displaying colored
    choices. The CSS class is derived by calling .get_FOO_class() on the row record.
    """
    def render(self, record, bound_column, value):
        if value:
            name = bound_column.name
            css_class = getattr(record, f'get_{name}_class')()
            label = getattr(record, f'get_{name}_display')()
            return mark_safe(
                f'<span class="badge bg-{css_class}">{label}</span>'
            )
        return self.default

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
    Display a color (#RRGGBB).
    """
    def render(self, value):
        return mark_safe(
            f'<span class="color-label" style="background-color: #{value}">&nbsp;</span>'
        )

    def value(self, value):
        return f'#{value}'


class ColoredLabelColumn(tables.TemplateColumn):
    """
    Render a colored label (e.g. for DeviceRoles).
    """
    template_code = """
    {% load helpers %}
    {% if value %}
    <span class="badge" style="color: {{ value.color|fgcolor }}; background-color: #{{ value.color }}">
      {{ value }}
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
    Display a list of tags assigned to the object.
    """
    template_code = """
    {% load helpers %}
    {% for tag in value.all %}
        {% tag tag url_name=url_name %}
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
        elif self.customfield.type == CustomFieldTypeChoices.TYPE_URL:
            # Linkify custom URLs
            return mark_safe(f'<a href="{value}">{value}</a>')
        if value is not None:
            return value
        return self.default


class CustomLinkColumn(tables.Column):
    """
    Render a custom links as a table column.
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
    {% load helpers %}
    {% if value %}
      {{ value|render_markdown }}
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
