import django_tables2 as tables
from django.core.exceptions import FieldDoesNotExist
from django.db.models.fields.related import RelatedField
from django.utils.safestring import mark_safe
from django_tables2.data import TableQuerysetData


class BaseTable(tables.Table):
    """
    Default table for object lists

    :param add_prefetch: By default, modify the queryset passed to the table upon initialization to automatically
      prefetch related data. Set this to False if it's necessary to avoid modifying the queryset (e.g. to
      accommodate PrefixQuerySet.annotate_depth()).
    """
    add_prefetch = True

    class Meta:
        attrs = {
            'class': 'table table-hover table-headings',
        }

    def __init__(self, *args, columns=None, **kwargs):
        super().__init__(*args, **kwargs)

        # Set default empty_text if none was provided
        if self.empty_text is None:
            self.empty_text = 'No {} found'.format(self._meta.model._meta.verbose_name_plural)

        # Hide non-default columns
        default_columns = getattr(self.Meta, 'default_columns', list())
        if default_columns:
            for column in self.columns:
                if column.name not in default_columns:
                    self.columns.hide(column.name)

        # Apply custom column ordering
        if columns is not None:
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
        if self.add_prefetch and isinstance(self.data, TableQuerysetData):
            model = getattr(self.Meta, 'model')
            prefetch_fields = []
            for column in self.columns:
                if column.visible:
                    field_path = column.accessor.split('.')
                    try:
                        model_field = model._meta.get_field(field_path[0])
                        if isinstance(model_field, RelatedField):
                            prefetch_fields.append('__'.join(field_path))
                    except FieldDoesNotExist:
                        pass
            self.data.data = self.data.data.prefetch_related(None).prefetch_related(*prefetch_fields)

    @property
    def configurable_columns(self):
        selected_columns = [
            (name, self.columns[name].verbose_name) for name in self.sequence if name not in ['pk', 'actions']
        ]
        available_columns = [
            (name, column.verbose_name) for name, column in self.columns.items() if name not in self.sequence and name not in ['pk', 'actions']
        ]
        return selected_columns + available_columns

    @property
    def visible_columns(self):
        return [name for name in self.sequence if self.columns[name].visible]


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
                    'class': 'min-width'
                }
            }
        super().__init__(*args, default=default, visible=visible, **kwargs)

    @property
    def header(self):
        return mark_safe('<input type="checkbox" class="toggle" title="Toggle all" />')


class BooleanColumn(tables.Column):
    """
    Custom implementation of BooleanColumn to render a nicely-formatted checkmark or X icon instead of a Unicode
    character.
    """
    def render(self, value):
        if value:
            rendered = '<span class="text-success"><i class="fa fa-check"></i></span>'
        elif value is None:
            rendered = '<span class="text-muted">&mdash;</span>'
        else:
            rendered = '<span class="text-danger"><i class="fa fa-close"></i></span>'
        return mark_safe(rendered)


class ButtonsColumn(tables.TemplateColumn):
    """
    Render edit, delete, and changelog buttons for an object.

    :param model: Model class to use for calculating URL view names
    :param prepend_content: Additional template content to render in the column (optional)
    """
    buttons = ('changelog', 'edit', 'delete')
    attrs = {'td': {'class': 'text-right text-nowrap noprint'}}
    # Note that braces are escaped to allow for string formatting prior to template rendering
    template_code = """
    {{% if "changelog" in buttons %}}
        <a href="{{% url '{app_label}:{model_name}_changelog' {pk_field}=record.{pk_field} %}}" class="btn btn-default btn-xs" title="Change log">
            <i class="fa fa-history"></i>
        </a>
    {{% endif %}}
    {{% if "edit" in buttons and perms.{app_label}.change_{model_name} %}}
        <a href="{{% url '{app_label}:{model_name}_edit' {pk_field}=record.{pk_field} %}}?return_url={{{{ request.path }}}}" class="btn btn-xs btn-warning" title="Edit">
            <i class="fa fa-pencil"></i>
        </a>
    {{% endif %}}
    {{% if "delete" in buttons and perms.{app_label}.delete_{model_name} %}}
        <a href="{{% url '{app_label}:{model_name}_delete' {pk_field}=record.{pk_field} %}}?return_url={{{{ request.path }}}}" class="btn btn-xs btn-danger" title="Delete">
            <i class="fa fa-trash"></i>
        </a>
    {{% endif %}}
    """

    def __init__(self, model, *args, pk_field='pk', buttons=None, prepend_template=None, **kwargs):
        if prepend_template:
            prepend_template = prepend_template.replace('{', '{{')
            prepend_template = prepend_template.replace('}', '}}')
            self.template_code = prepend_template + self.template_code

        template_code = self.template_code.format(
            app_label=model._meta.app_label,
            model_name=model._meta.model_name,
            pk_field=pk_field,
            buttons=buttons
        )

        super().__init__(template_code=template_code, *args, **kwargs)

        self.extra_context.update({
            'buttons': buttons or self.buttons,
        })

    def header(self):
        return ''


class ColorColumn(tables.Column):
    """
    Display a color (#RRGGBB).
    """
    def render(self, value):
        return mark_safe(
            '<span class="label color-block" style="background-color: #{}">&nbsp;</span>'.format(value)
        )


class ColoredLabelColumn(tables.TemplateColumn):
    """
    Render a colored label (e.g. for DeviceRoles).
    """
    template_code = """
    {% load helpers %}
    {% if value %}<label class="label" style="color: {{ value.color|fgcolor }}; background-color: #{{ value.color }}">{{ value }}</label>{% else %}&mdash;{% endif %}
    """

    def __init__(self, *args, **kwargs):
        super().__init__(template_code=self.template_code, *args, **kwargs)


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
