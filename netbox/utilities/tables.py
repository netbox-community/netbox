import django_tables2 as tables
from django.core.exceptions import FieldDoesNotExist
from django.db.models import ForeignKey
from django_tables2.data import TableQuerysetData
from django.utils.safestring import mark_safe


class BaseTable(tables.Table):
    """
    Default table for object lists
    """
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
            self.sequence = columns

            # Always include PK and actions column, if defined on the table
            if pk:
                self.base_columns['pk'] = pk
                self.sequence.insert(0, 'pk')
            if actions:
                self.base_columns['actions'] = actions
                self.sequence.append('actions')

        # Dynamically update the table's QuerySet to ensure related fields are pre-fetched
        if isinstance(self.data, TableQuerysetData):
            model = getattr(self.Meta, 'model')
            prefetch_fields = []
            for column in self.columns:
                if column.visible:
                    field_path = column.accessor.split('.')
                    try:
                        model_field = model._meta.get_field(field_path[0])
                        if isinstance(model_field, ForeignKey):
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
        if value is True:
            rendered = '<span class="text-success"><i class="fa fa-check"></i></span>'
        elif value is False:
            rendered = '<span class="text-danger"><i class="fa fa-close"></i></span>'
        else:
            rendered = '<span class="text-muted">&mdash;</span>'
        return mark_safe(rendered)


class ColorColumn(tables.Column):
    """
    Display a color (#RRGGBB).
    """
    def render(self, value):
        return mark_safe(
            '<span class="label color-block" style="background-color: #{}">&nbsp;</span>'.format(value)
        )
