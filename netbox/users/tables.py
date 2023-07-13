import django_tables2 as tables
from django_tables2.utils import A
from .models import Token
from netbox.tables import NetBoxTable, columns
from users.models import NetBoxGroup, NetBoxUser, ObjectPermission

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
  {% copy_content record.pk prefix="token_" color="success" %}
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
    username = tables.Column(linkify=True)
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
    name = tables.Column(linkify=True)
    actions = columns.ActionsColumn(
        actions=('edit', 'delete'),
    )

    class Meta(NetBoxTable.Meta):
        model = NetBoxGroup
        fields = (
            'pk', 'id', 'name', 'users_count',
        )
        default_columns = ('pk', 'name', 'users_count', )


class ObjectPermissionTable(NetBoxTable):
    name = tables.Column(linkify=True)
    actions = columns.ActionsColumn(
        actions=('edit', 'delete'),
    )

    class Meta(NetBoxTable.Meta):
        model = ObjectPermission
        fields = (
            'pk', 'id', 'name', 'enabled', 'actions', 'constraints',
        )
        default_columns = ('pk', 'name', 'enabled', 'actions', 'constraints',)
