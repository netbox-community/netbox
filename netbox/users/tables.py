import django_tables2 as tables
from django_tables2.utils import A
from .models import Token
from netbox.tables import NetBoxTable, columns
from users.models import NetBoxUser

__all__ = (
    'GroupTable',
    'ObjectPermissionTable',
    'TokenTable',
    'UserTable',
)


TOKEN = """<samp><span id="token_{{ record.pk }}">{{ record }}</span></samp>"""

ALLOWED_IPS = """{{ value|join:", " }}"""

COPY_BUTTON = """
{% if settings.ALLOW_TOKEN_RETRIEVAL %}
  <a class="btn btn-sm btn-success copy-token" data-clipboard-target="#token_{{ record.pk }}" title="Copy to clipboard">
    <i class="mdi mdi-content-copy"></i>
  </a>
{% endif %}
"""


class TokenActionsColumn(columns.ActionsColumn):
    # Subclass ActionsColumn to disregard permissions for edit & delete buttons
    actions = {
        'edit': columns.ActionsItem('Edit', 'pencil', None, 'warning'),
        'delete': columns.ActionsItem('Delete', 'trash-can-outline', None, 'danger'),
    }


class TokenTable(NetBoxTable):
    key = columns.TemplateColumn(
        template_code=TOKEN
    )
    write_enabled = columns.BooleanColumn(
        verbose_name='Write'
    )
    created = columns.DateColumn()
    expired = columns.DateColumn()
    last_used = columns.DateTimeColumn()
    allowed_ips = columns.TemplateColumn(
        template_code=ALLOWED_IPS
    )
    actions = TokenActionsColumn(
        actions=('edit', 'delete'),
        extra_buttons=COPY_BUTTON
    )

    class Meta(NetBoxTable.Meta):
        model = Token
        fields = (
            'pk', 'description', 'key', 'write_enabled', 'created', 'expires', 'last_used', 'allowed_ips',
        )


class UserTable(NetBoxTable):
    username = tables.LinkColumn('users:netboxuser', args=[A('pk')])
    actions = columns.ActionsColumn(
        actions=('edit', 'delete'),
    )

    class Meta(NetBoxTable.Meta):
        model = NetBoxUser
        fields = (
            'pk', 'id', 'username', 'email', 'first_name', 'last_name', 'is_superuser', 'is_staff', 'is_active'
        )
        default_columns = ('pk', 'username', 'email', 'first_name', 'last_name', 'is_superuser')


class GroupTable(NetBoxTable):
    username = tables.LinkColumn('users:netboxuser', args=[A('pk')])
    actions = columns.ActionsColumn(
        actions=('edit', 'delete'),
    )

    class Meta(NetBoxTable.Meta):
        model = NetBoxUser
        fields = (
            'pk', 'id', 'username', 'email', 'first_name', 'last_name', 'is_superuser', 'is_staff', 'is_active'
        )
        default_columns = ('pk', 'username', 'email', 'first_name', 'last_name', 'is_superuser')


class ObjectPermissionTable(NetBoxTable):
    username = tables.LinkColumn('users:netboxuser', args=[A('pk')])
    actions = columns.ActionsColumn(
        actions=('edit', 'delete'),
    )

    class Meta(NetBoxTable.Meta):
        model = NetBoxUser
        fields = (
            'pk', 'id', 'username', 'email', 'first_name', 'last_name', 'is_superuser', 'is_staff', 'is_active'
        )
        default_columns = ('pk', 'username', 'email', 'first_name', 'last_name', 'is_superuser')
