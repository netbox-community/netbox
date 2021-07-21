import django_tables2 as tables
from django.conf import settings
from django.contrib.auth.models import AnonymousUser
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import FieldDoesNotExist
from django.db.models.fields.related import RelatedField
from django.urls import reverse
from django.utils.safestring import mark_safe
from django_tables2 import RequestConfig
from django_tables2.data import TableQuerysetData
from django_tables2.utils import Accessor

from extras.models import CustomField
from .paginator import EnhancedPaginator, get_paginate_count


class BaseTable(tables.Table):
    """
    Default table for object lists

    :param user: Personalize table display for the given user (optional). Has no effect if AnonymousUser is passed.
    """

    class Meta:
        attrs = {
            'class': 'table table-hover object-list',
        }

    def __init__(self, *args, user=None, **kwargs):
        # Add custom field columns
        obj_type = ContentType.objects.get_for_model(self._meta.model)
        for cf in CustomField.objects.filter(content_types=obj_type):
            self.base_columns[f'cf_{cf.name}'] = CustomFieldColumn(cf)

        super().__init__(*args, **kwargs)

        # Set default empty_text if none was provided
        if self.empty_text is None:
            self.empty_text = f"No {self._meta.model._meta.verbose_name_plural} found"

        # Hide non-default columns
        default_columns = getattr(self.Meta, 'default_columns', list())
        if default_columns:
            for column in self.columns:
                if column.name not in default_columns:
                    self.columns.hide(column.name)

        # Apply custom column ordering for user
        if user is not None and not isinstance(user, AnonymousUser):
            columns = user.config.get(f"tables.{self.__class__.__name__}.columns")
            if columns:
                pk = self.base_columns.pop('pk', None)
                actions = self.base_columns.pop('actions', None)

                for name, column in self.base_columns.items():
                    if name in columns:
                        self.columns.show(name)
                    else:
                        self.columns.hide(name)
                self.sequence = [c for c in columns if c in self.base_columns]

                # Always include PK and actions column, if defined on the table
                if pk:
                    self.base_columns['pk'] = pk
                    self.sequence.insert(0, 'pk')
                if actions:
                    self.base_columns['actions'] = actions
                    self.sequence.append('actions')

        # Dynamically update the table's QuerySet to ensure related fields are pre-fetched
        if isinstance(self.data, TableQuerysetData):

            prefetch_fields = []
            for column in self.columns:
                if column.visible:
                    model = getattr(self.Meta, 'model')
                    accessor = column.accessor
                    prefetch_path = []
                    for field_name in accessor.split(accessor.SEPARATOR):
                        try:
                            field = model._meta.get_field(field_name)
                        except FieldDoesNotExist:
                            break
                        if isinstance(field, RelatedField):
                            # Follow ForeignKeys to the related model
                            prefetch_path.append(field_name)
                            model = field.remote_field.model
                        elif isinstance(field, GenericForeignKey):
                            # Can't prefetch beyond a GenericForeignKey
                            prefetch_path.append(field_name)
                            break
                    if prefetch_path:
                        prefetch_fields.append('__'.join(prefetch_path))
            self.data.data = self.data.data.prefetch_related(None).prefetch_related(*prefetch_fields)

    def _get_columns(self, visible=True):
        columns = []
        for name, column in self.columns.items():
            if column.visible == visible and name not in ['pk', 'actions']:
                columns.append((name, column.verbose_name))
        return columns

    @property
    def available_columns(self):
        return self._get_columns(visible=False)

    @property
    def selected_columns(self):
        return self._get_columns(visible=True)


#
# Table columns
#

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


class ButtonsColumn(tables.TemplateColumn):
    """
    Render edit, delete, and changelog buttons for an object.

    :param model: Model class to use for calculating URL view names
    :param prepend_content: Additional template content to render in the column (optional)
    :param return_url_extra: String to append to the return URL (e.g. for specifying a tab) (optional)
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
        <a href="{{% url '{app_label}:{model_name}_edit' pk=record.pk %}}?return_url={{{{ request.path }}}}{{{{ return_url_extra }}}}" class="btn btn-sm btn-warning" title="Edit">
            <i class="mdi mdi-pencil"></i>
        </a>
    {{% endif %}}
    {{% if "delete" in buttons and perms.{app_label}.delete_{model_name} %}}
        <a href="{{% url '{app_label}:{model_name}_delete' pk=record.pk %}}?return_url={{{{ request.path }}}}{{{{ return_url_extra }}}}" class="btn btn-sm btn-danger" title="Delete">
            <i class="mdi mdi-trash-can-outline"></i>
        </a>
    {{% endif %}}
    """

    def __init__(self, model, *args, buttons=None, prepend_template=None, return_url_extra='', **kwargs):
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
            'return_url_extra': return_url_extra,
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
        return value.name[0].upper() + value.name[1:]

    def value(self, value):
        return f"{value.app_label}.{value.model}"


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
    {% for tag in value.all %}
        {% include 'utilities/templatetags/tag.html' %}
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
        return value or self.default


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


#
# Pagination
#

def paginate_table(table, request):
    """
    Paginate a table given a request context.
    """
    paginate = {
        'paginator_class': EnhancedPaginator,
        'per_page': get_paginate_count(request)
    }
    RequestConfig(request, paginate).configure(table)
