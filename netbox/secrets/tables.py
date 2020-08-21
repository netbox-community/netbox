import django_tables2 as tables

from utilities.tables import BaseTable, ButtonsColumn, TagColumn, ToggleColumn
from .models import SecretRole, Secret


#
# Secret roles
#

class SecretRoleTable(BaseTable):
    pk = ToggleColumn()
    name = tables.LinkColumn()
    secret_count = tables.Column(
        verbose_name='Secrets'
    )
    actions = ButtonsColumn(SecretRole, pk_field='slug')

    class Meta(BaseTable.Meta):
        model = SecretRole
        fields = ('pk', 'name', 'secret_count', 'description', 'slug', 'actions')
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
