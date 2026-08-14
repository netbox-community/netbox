import zoneinfo
from dataclasses import dataclass
from urllib.parse import quote

import django_tables2 as tables
from django.conf import settings
from django.contrib.auth.context_processors import auth
from django.contrib.auth.models import AnonymousUser
from django.db.models import Case, DateField, DateTimeField, IntegerField, Q, Value, When
from django.db.models.fields.json import KeyTextTransform
from django.template import Context, Template
from django.urls import reverse
from django.utils.dateparse import parse_date
from django.utils.html import escape, format_html
from django.utils.safestring import mark_safe
from django.utils.text import format_lazy
from django.utils.translation import gettext_lazy as _
from django_tables2.columns import library
from django_tables2.utils import Accessor

from extras.choices import CustomFieldTypeChoices
from utilities.object_types import object_type_identifier, object_type_name
from utilities.permissions import get_permission_for_model
from utilities.request import get_safe_request_context
from utilities.templatetags.builtins.filters import render_markdown
from utilities.validators import url_scheme_is_allowed
from utilities.views import get_action_url

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
    'DictColumn',
    'DistanceColumn',
    'DurationColumn',
    'LinkedCountColumn',
    'MPTTColumn',
    'ManyToManyColumn',
    'MarkdownColumn',
    'TagColumn',
    'TemplateColumn',
    'ToggleColumn',
    'TreeColumn',
    'UtilizationColumn',
)


#
# Django-tables2 overrides
#

@library.register
class DateColumn(tables.Column):
    """
    Render a datetime.date in ISO 8601 format.
    """
    def render(self, value):
        if value:
            return value.isoformat()
        return None

    def value(self, value):
        if value:
            return value.isoformat()
        return None

    @classmethod
    def from_field(cls, field, **kwargs):
        if isinstance(field, DateField):
            return cls(**kwargs)
        return None


@library.register
class DateTimeColumn(tables.Column):
    """
    Render a datetime.datetime in ISO 8601 format.

    Args:
        timespec: Granularity specification; passed through to datetime.isoformat()
    """
    def __init__(self, *args, timespec='seconds', **kwargs):
        self.timespec = timespec
        super().__init__(*args, **kwargs)

    def render(self, value):
        if value:
            current_tz = zoneinfo.ZoneInfo(settings.TIME_ZONE)
            value = value.astimezone(current_tz)
            return f"{value.date().isoformat()} {value.time().isoformat(timespec=self.timespec)}"
        return None

    def value(self, value):
        if value:
            return value.isoformat()
        return None

    @classmethod
    def from_field(cls, field, **kwargs):
        if isinstance(field, DateTimeField):
            return cls(**kwargs)
        return None


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
                    'aria-label': _('Select all'),
                },
                'td': {
                    'class': 'w-1',
                },
                'input': {
                    'class': 'form-check-input',
                    'aria-label': lambda record, value: format_lazy(_('Select {object}'), object=record),
                }
            }
        super().__init__(*args, default=default, visible=visible, **kwargs)

    @property
    def header(self):
        title_text = _('Toggle all')
        return format_html(
            '<input type="checkbox" class="toggle form-check-input" title="{}" aria-label="{}" />',
            title_text, title_text,
        )


class BooleanColumn(tables.Column):
    """
    Custom implementation of BooleanColumn to render a nicely-formatted checkmark or X icon instead of a Unicode
    character.
    """
    TRUE_MARK = mark_safe('<span class="text-success"><i class="mdi mdi-check-bold"></i></span>')
    FALSE_MARK = mark_safe('<span class="text-danger"><i class="mdi mdi-close-thick"></i></span>')
    EMPTY_MARK = mark_safe('<span class="text-muted">&mdash;</span>')  # Placeholder

    def __init__(self, *args, true_mark=TRUE_MARK, false_mark=FALSE_MARK, **kwargs):
        self.true_mark = true_mark
        self.false_mark = false_mark
        super().__init__(*args, **kwargs)

    def render(self, value):
        if value is None:
            return self.EMPTY_MARK
        if value and self.true_mark:
            return self.true_mark
        if not value and self.false_mark:
            return self.false_mark
        return self.EMPTY_MARK

    def value(self, value):
        return str(value)


@dataclass
class ActionsItem:
    title: str
    icon: str
    permission: str | None = None
    css_class: str | None = 'secondary'


class ActionsColumn(tables.Column):
    """
    A dropdown menu which provides edit, delete, and changelog links for an object. Can optionally include
    additional buttons rendered from a template string.

    :param actions: The ordered list of dropdown menu items to include
    :param extra_buttons: A Django template string which renders additional buttons preceding the actions dropdown
    :param split_actions: When True, converts the actions dropdown menu into a split button with first action as the
        direct button link and icon (default: True)
    """
    attrs = {
        'th': {
            'aria-label': _('Actions'),
        },
        'td': {
            'class': 'text-end text-nowrap noprint p-1'
        }
    }
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
        model = table.Meta.model

        # Skip if no actions or extra buttons are defined
        if not (self.actions or self.extra_buttons):
            return ''
        # Skip dummy records (e.g. available VLANs or IP ranges replacing individual IPs)
        if not isinstance(record, model) or not getattr(record, 'pk', None):
            return ''

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
                url = get_action_url(model, action=action, kwargs={'pk': record.pk})

                # Render a separate button if a) only one action exists, or b) if split_actions is True
                if len(self.actions) == 1 or (self.split_actions and idx == 0):
                    dropdown_class = attrs.css_class
                    button = (
                        f'<a class="btn btn-sm btn-{attrs.css_class}" href="{url}{url_appendix}" type="button" '
                        f'aria-label="{attrs.title}">'
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
                f'  <a class="btn btn-sm btn-{dropdown_class} dropdown-toggle" type="button" data-bs-toggle="dropdown" '
                f'style="padding-left: 2px">'
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
    set by the instance's get_FOO_color() method, if defined, or can be overridden by a "color" callable.
    """
    DEFAULT_BG_COLOR = 'secondary'

    def __init__(self, *args, color=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.color = color

    def render(self, record, bound_column, value):
        if value in self.empty_values:
            return self.default

        # Determine the background color to use (use "color" callable if given, else try calling object.get_FOO_color())
        if self.color:
            bg_color = self.color(record)
        else:
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
        return object_type_name(value, include_app=False)

    def value(self, value):
        if value is None:
            return None
        return object_type_identifier(value)


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
        return object_type_name(obj, include_app=False)

    def value(self, value):
        return ','.join([
            object_type_identifier(ot) for ot in self.filter(value)
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
            return mark_safe(f'<a href="{url}">{escape(value)}</a>')
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
        else:
            kwargs.setdefault('order_by', (
                self.unset_alias,
                f'custom_field_data__{customfield.name}',
            ))

        super().__init__(*args, **kwargs)

    @property
    def unset_alias(self):
        """
        Return the name of the annotation which groups together the objects holding no value for
        this field (see get_ordering_annotation()).

        The annotation is named for the custom field so that ordering by two custom field columns
        cannot produce a duplicate alias. Field names are validated to contain only alphanumerics
        and underscores, so the alias is always a legal identifier.
        """
        return f'_cf_{self.customfield.name}_unset'

    def get_ordering_annotation(self):
        """
        Return the annotation by which objects holding no value for this field are sorted together,
        as the leading sort key for the column. (BaseTable applies it to the queryset when ordering
        by this column.)

        An object can lack a value either by storing a JSON null or by carrying no key for the
        field at all -- the latter being the normal state for objects which predate it, as data is
        no longer provisioned onto existing objects (see CustomField.populate_initial_data()).
        Postgres sorts those two apart: a JSON null is the lowest jsonb value, whereas a missing
        key yields SQL NULL and sorts last, so the "empty" rows would otherwise land at both ends
        of the same column. This key (the `empty` lookup covers both states) groups them at one
        end, matching how SQL NULLs are ordered for an ordinary column: last when ascending, first
        when descending. The column's second sort key then orders by the raw value, so that numeric
        and date fields still sort by type rather than lexically.
        """
        return {
            self.unset_alias: Q(**{f'custom_field_data__{self.customfield.name}__empty': True})
        }

    def order(self, queryset, is_descending):
        """
        Override get_ordering_annotation()'s default (SQL-standard, direction-coupled) null
        placement to honor the custom field's nulls_first attribute instead: the empty group's
        position is fixed by admin preference, independent of ascending/descending. Returning
        (queryset, True) here signals django-tables2 to use this ordering as-is, bypassing the
        generic annotation set up by get_ordering_annotation() (which still runs, but its result
        goes unused for this column since only its alias name -- referenced by unset_alias --
        needs to exist, not the SQL-standard placement it would otherwise apply).

        A missing key or a JSON null value is extracted as SQL NULL via the ->> (text) operator,
        whereas the -> (JSONB) operator used for value ordering treats JSON null as a sortable
        value. We therefore annotate an explicit rank to control null placement independently of
        JSONB sorting.

        Ordering is expressed as plain string keys (not F()-based OrderBy expressions): NetBox's
        BaseTable._apply_ordering_tie_breaker() inspects self.data.data.query.order_by afterward
        and wraps each entry in django-tables2's own (string-only) OrderBy helper, which raises
        TypeError on a raw expression object.

        Trade-off: returning (queryset, True) here is django-tables2's signal that this column
        has fully handled ordering itself, which takes priority over -- and discards -- any other
        columns' sort keys requested in the same multi-column sort (see TableQuerysetData.order_by()
        in django_tables2/data.py: the loop applies whichever column's order() last returns
        modified=True and returns immediately, never combining it with sibling columns'
        contributions). A CustomFieldColumn can therefore not currently be composed with other
        columns in a single sort; it is always the sole and final sort key when included. Preserving
        nulls_first (an existing, widely-integrated per-field admin setting) was judged to matter
        more than gaining composability for this specific column, since django-tables2's per-key
        ascending/descending toggle is applied uniformly across an entire order_by tuple and cannot
        keep one key's effective placement constant while another flips -- so nulls_first and
        multi-column composition cannot both be expressed through the generic annotation mechanism
        for the same column.
        """
        name = self.customfield.name
        text_value = f'_cf_{name}_text'
        null_rank = f'_cf_{name}_nullrank'
        null_sort, value_sort = (0, 1) if self.customfield.nulls_first else (1, 0)
        queryset = queryset.annotate(**{
            text_value: KeyTextTransform(name, 'custom_field_data'),
        }).annotate(**{
            null_rank: Case(
                When(**{f'{text_value}__isnull': True}, then=Value(null_sort)),
                default=Value(value_sort),
                output_field=IntegerField(),
            ),
        })
        value_field = f'custom_field_data__{name}'
        ordering = (null_rank, f'-{value_field}' if is_descending else value_field)
        return queryset.order_by(*ordering), True

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
            # Only render as a link if the scheme is permitted by ALLOWED_URL_SCHEMES, to guard against
            # dangerous schemes (e.g. javascript:) in values which bypassed validation. A schemeless
            # (relative) value is considered safe.
            if url_scheme_is_allowed(value):
                return mark_safe(f'<a href="{escape(value)}">{escape(value)}</a>')
            return escape(value)
        if self.customfield.type == CustomFieldTypeChoices.TYPE_SELECT:
            if value is None:
                return self.default
            label = self.customfield.get_choice_label(value)
            color = self.customfield.get_choice_color(value)
            if color:
                return mark_safe(
                    f'<span class="badge text-bg-{escape(color)}">{escape(label)}</span>'
                )
            return label
        if self.customfield.type == CustomFieldTypeChoices.TYPE_MULTISELECT:
            if not value:
                return ''

            has_color = False
            parts = []

            for v in value:
                label = self.customfield.get_choice_label(v)
                color = self.customfield.get_choice_color(v)
                if color:
                    has_color = True
                parts.append((label, color))
            if has_color:
                badges = []
                for label, color in parts:
                    badges.append(
                        f'<span class="badge text-bg-{escape(color or "secondary")}">{escape(label)}</span>'
                    )
                return mark_safe(' '.join(badges))
            return ', '.join(label for label, _ in parts)

        if self.customfield.type == CustomFieldTypeChoices.TYPE_MULTIOBJECT:
            return mark_safe(', '.join(
                self._linkify_item(obj) for obj in self.customfield.deserialize(value)
            ))
        if self.customfield.type == CustomFieldTypeChoices.TYPE_LONGTEXT and value:
            return render_markdown(value)
        if self.customfield.type == CustomFieldTypeChoices.TYPE_DATE and value:
            return parse_date(value).isoformat()
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
            # If the request is available, include a sanitized subset of it as context
            context.update({
                'request': get_safe_request_context(request),
                **auth(request),
            })

        return self.customlink.render(context)

    def render(self, record, table, **kwargs):
        try:
            if rendered := self._render_customlink(record, table):
                return mark_safe(f'<a href="{rendered["link"]}"{rendered["link_target"]}>{rendered["text"]}</a>')
        except Exception as e:
            error_text = _('Error')
            return format_html(
                '<span class="text-danger" title="{}"><i class="mdi mdi-alert"></i> {}</span>', e, error_text
            )
        return ''

    def value(self, record, table, **kwargs):
        try:
            if rendered := self._render_customlink(record, table):
                return rendered['link']
        except Exception:
            pass
        return None


class TreeColumn(tables.TemplateColumn):
    """
    Display a nested hierarchy for tree-enabled models (Region, Location, etc.).
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


# Deprecated alias for plugin compatibility; use TreeColumn going forward.
# TODO: Remove this in NetBox v5.0
MPTTColumn = TreeColumn


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


class DistanceColumn(TemplateColumn):
    """
    Distance with template code for formatting
    """
    template_code = """
    {% load helpers %}
    {% display_distance record.distance record.distance_unit record.abs_distance %}
    """

    def __init__(self, template_code=template_code, order_by='_abs_distance', **kwargs):
        super().__init__(template_code=template_code, order_by=order_by, **kwargs)


class DictColumn(tables.Column):
    """
    Render a dictionary of data in a simple key: value format, one pair per line.
    """
    def render(self, value):
        output = '<br />'.join([
            f'{escape(k)}: {escape(v)}' for k, v in value.items()
        ])
        return mark_safe(output)
