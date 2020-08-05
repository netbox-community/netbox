import django_tables2 as tables
from django.utils.translation import gettext as _

from utilities.tables import BaseTable, TagColumn, ToggleColumn
from .models import SecretRole, Secret

SECRETROLE_ACTIONS = """
<a href="{% url 'secrets:secretrole_changelog' slug=record.slug %}" class="btn btn-default btn-xs" title="Change log">
    <i class="fa fa-history"></i>
</a>
{% if perms.secrets.change_secretrole %}
    <a href="{% url 'secrets:secretrole_edit' slug=record.slug %}?return_url={{ request.path }}" class="btn btn-xs btn-warning"><i class="glyphicon glyphicon-pencil" aria-hidden="true"></i></a>
{% endif %}
"""


#
# Secret roles
#

class SecretRoleTable(BaseTable):
    pk = ToggleColumn()
    name = tables.LinkColumn()
    secret_count = tables.Column(
        verbose_name=_('Secrets')
    )
    actions = tables.TemplateColumn(
        template_code=SECRETROLE_ACTIONS,
        attrs={'td': {'class': 'text-right noprint'}},
        verbose_name=''
    )

    class Meta(BaseTable.Meta):
        model = SecretRole
        fields = ('pk', 'name', 'secret_count', 'description', 'slug', 'users', 'groups', 'actions')
        default_columns = ('pk', 'name', 'secret_count', 'description', 'actions')


#
# Secrets
#

class SecretTable(BaseTable):
    pk = ToggleColumn()
    device = tables.LinkColumn()
    tags = TagColumn(
        url_name='secrets:secret_list'
    )

    class Meta(BaseTable.Meta):
        model = Secret
        fields = ('pk', 'device', 'role', 'name', 'last_updated', 'hash', 'tags')
        default_columns = ('pk', 'device', 'role', 'name', 'last_updated')
