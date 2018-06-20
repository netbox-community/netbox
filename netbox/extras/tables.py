from __future__ import unicode_literals

import django_tables2 as tables
from taggit.models import Tag

from utilities.tables import BaseTable, ToggleColumn
from .models import ObjectChange

TAG_ACTIONS = """
{% if perms.taggit.change_tag %}
    <a href="{% url 'extras:tag_edit' slug=record.slug %}" class="btn btn-xs btn-warning"><i class="glyphicon glyphicon-pencil" aria-hidden="true"></i></a>
{% endif %}
{% if perms.taggit.delete_tag %}
    <a href="{% url 'extras:tag_delete' slug=record.slug %}" class="btn btn-xs btn-danger"><i class="glyphicon glyphicon-trash" aria-hidden="true"></i></a>
{% endif %}
"""

OBJECTCHANGE_ACTION = """
{% if record.action == 1 %}
    <span class="label label-success">Created</span>
{% elif record.action == 2 %}
    <span class="label label-primary">Updated</span>
{% elif record.action == 3 %}
    <span class="label label-danger">Deleted</span>
{% endif %}
"""

OBJECTCHANGE_OBJECT = """
{% if record.action != 3 and record.changed_object.get_absolute_url %}
    <a href="{{ record.changed_object.get_absolute_url }}">{{ record.object_repr }}</a>
{% else %}
    {{ record.object_repr }}
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


class ObjectChangeTable(BaseTable):
    time = tables.LinkColumn()
    action = tables.TemplateColumn(
        template_code=OBJECTCHANGE_ACTION
    )
    object_repr = tables.TemplateColumn(
        template_code=OBJECTCHANGE_OBJECT,
        verbose_name='Object'
    )
    request_id = tables.Column(
        verbose_name='Request ID'
    )

    class Meta(BaseTable.Meta):
        model = ObjectChange
        fields = ('time', 'user_name', 'action', 'content_type', 'object_repr', 'request_id')
