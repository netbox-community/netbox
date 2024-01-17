from dataclasses import dataclass
from typing import Optional
from urllib.parse import quote

import django_tables2 as tables
from django.conf import settings
from django.contrib.auth.context_processors import auth
from django.contrib.auth.models import AnonymousUser
from django.db.models import DateField, DateTimeField
from django.template import Context, Template
from django.urls import reverse
from django.utils.dateparse import parse_date
from django.utils.formats import date_format
from django.utils.html import escape
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _
from django_tables2.columns import library
from django_tables2.utils import Accessor

from extras.choices import CustomFieldTypeChoices
from utilities.permissions import get_permission_for_model
from utilities.templatetags.builtins.filters import render_markdown
from utilities.utils import content_type_identifier, content_type_name, get_viewname

__all__ = (
    'ActionsColumn',
    'ArrayColumn',
    'BooleanColumn',
    'ChoiceFieldColumn',
    'ChoicesColumn',
    'ColorColumn',
    'ColoredLabelColumn',
    'ContentTypeColumn',
    'ContentTypesColumn',
    'CustomFieldColumn',
    'CustomLinkColumn',
    'DurationColumn',
    'LinkedCountColumn',
    'MarkdownColumn',
    'ManyToManyColumn',
    'MPTTColumn',
    'TagColumn',
    'TemplateColumn',
    'ToggleColumn',
    'UtilizationColumn',
)


#
# Django-tables2 overrides
#

@library.register
class DateColumn(tables.DateColumn):
    """
    Overrides the default implementation of DateColumn to better handle null values, returning a default value for
    tables and null when exporting data. It is registered in the tables library to use this class instead of the
    default, making this behavior consistent in all fields of type DateField.
    """
    def render(self, value):
        if value:
            return date_format(value, format="SHORT_DATE_FORMAT")

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


class DurationColumn(tables.Column):
    """
    Express a duration of time (in minutes) in a human-friendly format. Example: 437 minutes becomes "7h 17m"
    """
    def render(self, value):
        ret = ''
        if days := value // 1440:
            ret += f'{days}d '
        if hours := value % 1440 // 60:
            ret += f'{hours}h '
        if minutes := value % 60:
            ret += f'{minutes}m'
        return ret.strip()

    def value(self, value):
        return value


class ManyToManyColumn(tables.ManyToManyColumn):
    """
    Overrides django-tables2's stock ManyToManyColumn to ensure that value() returns only plaintext data.
    """
    def value(self, value):
        items = [self.transform(item) for item in self.filter(value)]
        return self.separator.join(items)


class TemplateColumn(tables.TemplateColumn):
    """
    Overrides django-tables2's stock TemplateColumn class to render a placeholder symbol if the returned value
    is an empty string.
    """
    PLACEHOLDER = mark_safe('&mdash;')

    def __init__(self, export_raw=False, **kwargs):
        """
        Args:
            export_raw: If true, data export returns the raw field value rather than the rendered template. (Default:
                        False)
        """
        super().__init__(**kwargs)
        self.export_raw = export_raw

    def render(self, *args, **kwargs):
        ret = super().render(*args, **kwargs)
        if not ret.strip():
            return self.PLACEHOLDER
        return ret

    def value(self, **kwargs):
        if self.export_raw:
            # Skip template rendering and export raw value
            return kwargs.get('value')

        ret = super().value(**kwargs)
        if ret == self.PLACEHOLDER:
            return ''
        return ret


#
# Custom columns
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
                'th': {
                    'class': 'w-1',
                },
                'td': {
                    'class': 'w-1',
                },
                'input': {
                    'class': 'form-check-input'
                }
            }
        super().__init__(*args, default=default, visible=visible, **kwargs)

    @property
    def header(self):
        title_text = _('Toggle all')
        return mark_safe(f'<input type="checkbox" class="toggle form-check-input" title="{title_text}" />')


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


@dataclass
class ActionsItem:
    title: str
    icon: str
    permission: Optional[str] = None
    css_class: Optional[str] = 'secondary'


class ActionsColumn(tables.Column):
    """
    A dropdown menu which provides edit, delete, and changelog links for an object. Can optionally include
    additional buttons rendered from a template string.

    :param actions: The ordered list of dropdown menu items to include
    :param extra_buttons: A Django template string which renders additional buttons preceding the actions dropdown
    :param split_actions: When True, converts the actions dropdown menu into a split button with first action as the
        direct button link and icon (default: True)
    """
    attrs = {'td': {'class': 'text-end text-nowrap noprint'}}
    empty_values = ()
    actions = {
        'edit': ActionsItem('Edit', 'pencil', 'change', 'warning'),
        'delete': ActionsItem('Delete', 'trash-can-outline', 'delete', 'danger'),
        'changelog': ActionsItem('Changelog', 'history'),
    }

    def __init__(self, *args, actions=('edit', 'delete', 'changelog'), extra_buttons='', split_actions=True, **kwargs):
        super().__init__(*args, **kwargs)

        self.extra_buttons = extra_buttons
        self.split_actions = split_actions

        # Determine which actions to enable
        self.actions = {
            name: self.actions[name] for name in actions
        }

    def header(self):
        return ''

    def render(self, record, table, **kwargs):
        # Skip dummy records (e.g. available VLANs) or those with no actions
        if not getattr(record, 'pk', None) or not self.actions:
            return ''

        model = table.Meta.model
        if request := getattr(table, 'context', {}).get('request'):
            return_url = request.GET.get('return_url', request.get_full_path())
            url_appendix = f'?return_url={quote(return_url)}'
        else:
            url_appendix = ''

        html = ''

        # Compile actions menu
        button = None
        dropdown_class = 'secondary'
        dropdown_links = []
        user = getattr(request, 'user', AnonymousUser())
        for idx, (action, attrs) in enumerate(self.actions.items()):
            permission = get_permission_for_model(model, attrs.permission)
            if attrs.permission is None or user.has_perm(permission):
                url = reverse(get_viewname(model, action), kwargs={'pk': record.pk})

                # Render a separate button if a) only one action exists, or b) if split_actions is True
                if len(self.actions) == 1 or (self.split_actions and idx == 0):
                    dropdown_class = attrs.css_class
                    button = (
                        f'<a class="btn btn-sm btn-{attrs.css_class}" href="{url}{url_appendix}" type="button">'
                        f'<i class="mdi mdi-{attrs.icon}"></i></a>'
                    )

                # Add dropdown menu items
                else:
                    dropdown_links.append(
                        f'<li><a class="dropdown-item" href="{url}{url_appendix}">'
                        f'<i class="mdi mdi-{attrs.icon}"></i> {attrs.title}</a></li>'
                    )

        # Create the actions dropdown menu
        toggle_text = _('Toggle Dropdown')
        if button and dropdown_links:
            html += (
                f'<span class="btn-group dropdown">'
                f'  {button}'
                f'  <a class="btn btn-sm btn-{dropdown_class} dropdown-toggle" type="button" data-bs-toggle="dropdown" style="padding-left: 2px">'
                f'  <span class="visually-hidden">{toggle_text}</span></a>'
                f'  <ul class="dropdown-menu">{"".join(dropdown_links)}</ul>'
                f'</span>'
            )
        elif button:
            html += button
        elif dropdown_links:
            html += (
                f'<span class="btn-group dropdown">'
                f'  <a class="btn btn-sm btn-secondary dropdown-toggle" type="button" data-bs-toggle="dropdown">'
                f'  <span class="visually-hidden">{toggle_text}</span></a>'
                f'  <ul class="dropdown-menu">{"".join(dropdown_links)}</ul>'
                f'</span>'
            )

        # Render any extra buttons from template code
        if self.extra_buttons:
            template = Template(self.extra_buttons)
            context = getattr(table, "context", Context())
            context.update({'record': record})
            html = template.render(context) + html

        return mark_safe(html)


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
            bg_color = getattr(record, f'get_{bound_column.name}_color')() or self.DEFAULT_BG_COLOR
        except AttributeError:
            bg_color = self.DEFAULT_BG_COLOR

        return mark_safe(f'<span class="badge text-bg-{bg_color}">{value}</span>')

    def value(self, value):
        return value


class ContentTypeColumn(tables.Column):
    """
    Display a ContentType instance.
    """
    def render(self, value):
        if value is None:
            return None
        return content_type_name(value, include_app=False)

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
        return content_type_name(obj, include_app=False)

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
            orderable=False,
            template_code=self.template_code,
            extra_context={'url_name': url_name},
            verbose_name=_('Tags'),
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
        # We can't logically sort on FK values
        if customfield.type in (
            CustomFieldTypeChoices.TYPE_OBJECT,
            CustomFieldTypeChoices.TYPE_MULTIOBJECT
        ):
            kwargs['orderable'] = False

        super().__init__(*args, **kwargs)

    @staticmethod
    def _linkify_item(item):
        if hasattr(item, 'get_absolute_url'):
            return f'<a href="{item.get_absolute_url()}">{escape(item)}</a>'
        return escape(item)

    def render(self, value):
        if self.customfield.type == CustomFieldTypeChoices.TYPE_BOOLEAN and value is True:
            return mark_safe('<i class="mdi mdi-check-bold text-success"></i>')
        if self.customfield.type == CustomFieldTypeChoices.TYPE_BOOLEAN and value is False:
            return mark_safe('<i class="mdi mdi-close-thick text-danger"></i>')
        if self.customfield.type == CustomFieldTypeChoices.TYPE_URL:
            return mark_safe(f'<a href="{escape(value)}">{escape(value)}</a>')
        if self.customfield.type == CustomFieldTypeChoices.TYPE_SELECT:
            return self.customfield.get_choice_label(value)
        if self.customfield.type == CustomFieldTypeChoices.TYPE_MULTISELECT:
            return ', '.join(self.customfield.get_choice_label(v) for v in value)
        if self.customfield.type == CustomFieldTypeChoices.TYPE_MULTIOBJECT:
            return mark_safe(', '.join(
                self._linkify_item(obj) for obj in self.customfield.deserialize(value)
            ))
        if self.customfield.type == CustomFieldTypeChoices.TYPE_LONGTEXT and value:
            return render_markdown(value)
        if self.customfield.type == CustomFieldTypeChoices.TYPE_DATE and value:
            return date_format(parse_date(value), format="SHORT_DATE_FORMAT")
        if value is not None:
            obj = self.customfield.deserialize(value)
            return mark_safe(self._linkify_item(obj))
        return self.default

    def value(self, value):
        if isinstance(value, list):
            return ','.join(str(v) for v in self.customfield.deserialize(value))
        if value is not None:
            return self.customfield.deserialize(value)
        return self.default


class CustomLinkColumn(tables.Column):
    """
    Render a custom link as a table column.
    """
    def __init__(self, customlink, *args, **kwargs):
        self.customlink = customlink
        kwargs.setdefault('accessor', Accessor('pk'))
        kwargs.setdefault('orderable', False)
        kwargs.setdefault('verbose_name', customlink.name)

        super().__init__(*args, **kwargs)

    def _render_customlink(self, record, table):
        context = {
            'object': record,
            'debug': settings.DEBUG,
        }
        if request := getattr(table, 'context', {}).get('request'):
            # If the request is available, include it as context
            context.update({
                'request': request,
                **auth(request),
            })

        return self.customlink.render(context)

    def render(self, record, table, **kwargs):
        try:
            if rendered := self._render_customlink(record, table):
                return mark_safe(f'<a href="{rendered["link"]}"{rendered["link_target"]}>{rendered["text"]}</a>')
        except Exception as e:
            error_text = _('Error')
            return mark_safe(f'<span class="text-danger" title="{e}"><i class="mdi mdi-alert"></i> {error_text}</span>')
        return ''

    def value(self, record, table, **kwargs):
        try:
            if rendered := self._render_customlink(record, table):
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
        {% if not table.order_by %}
          {% for i in record.level|as_range %}<i class="mdi mdi-circle-small"></i>{% endfor %}
        {% endif %}
        <a href="{{ record.get_absolute_url }}">{{ record.name }}</a>
    """

    def __init__(self, *args, **kwargs):
        super().__init__(
            template_code=self.template_code,
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

    def __init__(self, **kwargs):
        super().__init__(
            template_code=self.template_code,
            **kwargs,
        )

    def value(self, value):
        return value


class ArrayColumn(tables.Column):
    """
    List array items as a comma-separated list.
    """
    def __init__(self, *args, max_items=None, func=str, **kwargs):
        self.max_items = max_items
        self.func = func
        super().__init__(*args, **kwargs)

    def render(self, value):
        omitted_count = 0

        # Limit the returned items to the specified maximum number (if any)
        if self.max_items:
            omitted_count = len(value) - self.max_items
            value = value[:self.max_items - 1]

        # Apply custom processing function (if any) per item
        if self.func:
            value = [self.func(v) for v in value]

        # Annotate omitted items (if applicable)
        if omitted_count > 0:
            value.append(f'({omitted_count} more)')

        return ', '.join(value)


class ChoicesColumn(tables.Column):
    """
    Display the human-friendly labels of a set of choices.
    """
    def __init__(self, *args, max_items=None, **kwargs):
        self.max_items = max_items
        super().__init__(*args, **kwargs)

    def render(self, value):
        omitted_count = 0
        value = [v[1] for v in value]

        # Limit the returned items to the specified maximum number (if any)
        if self.max_items:
            omitted_count = len(value) - self.max_items
            value = value[:self.max_items - 1]

        # Annotate omitted items (if applicable)
        if omitted_count > 0:
            value.append(f'({omitted_count} more)')

        return ', '.join(value)
