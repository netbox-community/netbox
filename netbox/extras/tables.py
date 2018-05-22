from __future__ import unicode_literals

import django_tables2 as tables
from taggit.models import Tag

from utilities.tables import BaseTable, ToggleColumn

TAG_ACTIONS = """
{% if perms.taggit.change_tag %}
    <a href="{% url 'extras:tag_edit' slug=record.slug %}" class="btn btn-xs btn-warning"><i class="glyphicon glyphicon-pencil" aria-hidden="true"></i></a>
{% endif %}
{% if perms.taggit.delete_tag %}
    <a href="{% url 'extras:tag_delete' slug=record.slug %}" class="btn btn-xs btn-danger"><i class="glyphicon glyphicon-trash" aria-hidden="true"></i></a>
{% endif %}
"""


class TagTable(BaseTable):
    pk = ToggleColumn()
    actions = tables.TemplateColumn(
        template_code=TAG_ACTIONS,
        attrs={'td': {'class': 'text-right'}},
        verbose_name=''
    )

    class Meta(BaseTable.Meta):
        model = Tag
        fields = ('pk', 'name', 'items')
