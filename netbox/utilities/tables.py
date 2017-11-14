from __future__ import unicode_literals

import django_tables2 as tables
from django.utils.safestring import mark_safe


class BaseTable(tables.Table):
    """
    Default table for object lists
    """
    def __init__(self, *args, **kwargs):
        super(BaseTable, self).__init__(*args, **kwargs)

        # Set default empty_text if none was provided
        if self.empty_text is None:
            self.empty_text = 'No {} found'.format(self._meta.model._meta.verbose_name_plural)

    class Meta:
        attrs = {
            'class': 'table table-hover table-headings',
        }


class ToggleColumn(tables.CheckBoxColumn):

    def __init__(self, *args, **kwargs):
        default = kwargs.pop('default', '')
        visible = kwargs.pop('visible', False)
        super(ToggleColumn, self).__init__(*args, default=default, visible=visible, **kwargs)

    @property
    def header(self):
        return mark_safe('<input type="checkbox" id="toggle_all" title="Toggle all" />')
