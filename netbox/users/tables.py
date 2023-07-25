from django.conf import settings
import django_tables2 as tables

from netbox.tables import NetBoxTable, columns
from users.models import NetBoxGroup, NetBoxUser, ObjectPermission, Token, UserToken

__all__ = (
    'GroupTable',
    'ObjectPermissionTable',
    'TokenTable',
    'UserTable',
    'UserTokenTable',
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
        verbose_name='Key',
        template_code=TOKEN
    )
    write_enabled = columns.BooleanColumn(
        verbose_name='Write'
    )
    created = columns.DateColumn(
        verbose_name='Created',
    )
    expired = columns.DateColumn(
        verbose_name='Expired',
    )
    last_used = columns.DateTimeColumn(
        verbose_name='Last used',
    )
    allowed_ips = columns.TemplateColumn(
        verbose_name='Allowed IPs',
        template_code=ALLOWED_IPS
    )
    actions = TokenActionsColumn(
        verbose_name='Actions',
        actions=('edit', 'delete'),
        extra_buttons=COPY_BUTTON
    )

    class Meta(NetBoxTable.Meta):
        model = Token
        fields = (
            'pk', 'description', 'key', 'write_enabled', 'created', 'expires', 'last_used', 'allowed_ips',
        )


class UserTokenTable(NetBoxTable):
    key = columns.TemplateColumn(
        verbose_name='Key',
        template_code=TOKEN,
    )
    write_enabled = columns.BooleanColumn(
        verbose_name='Write'
    )
    created = columns.DateColumn(
        verbose_name='Created',
    )
    expired = columns.DateColumn(
        verbose_name='Expired',
    )
    last_used = columns.DateTimeColumn(
        verbose_name='Last used',
    )
    allowed_ips = columns.TemplateColumn(
        verbose_name='Allowed IPs',
        template_code=ALLOWED_IPS
    )
    actions = TokenActionsColumn(
        verbose_name='Actions',
        actions=('edit', 'delete'),
        extra_buttons=COPY_BUTTON
    )

    class Meta(NetBoxTable.Meta):
        model = UserToken
        fields = [
            'pk', 'id', 'key', 'user', 'description', 'write_enabled', 'created', 'expires', 'last_used', 'allowed_ips',
        ]


class UserTable(NetBoxTable):
    username = tables.Column(
        verbose_name='Username',
        linkify=True
    )
    groups = columns.ManyToManyColumn(
        verbose_name='Groups',
        linkify_item=('users:netboxgroup', {'pk': tables.A('pk')})
    )
    is_active = columns.BooleanColumn(
        verbose_name='Is active',
    )
    is_staff = columns.BooleanColumn(
        verbose_name='Is staff',
    )
    is_superuser = columns.BooleanColumn(
        verbose_name='Is superuser',
    )
    actions = columns.ActionsColumn(
        verbose_name='Actions',
        actions=('edit', 'delete'),
    )

    class Meta(NetBoxTable.Meta):
        model = NetBoxUser
        fields = (
            'pk', 'id', 'username', 'first_name', 'last_name', 'email', 'groups', 'is_active', 'is_staff',
            'is_superuser',
        )
        default_columns = ('pk', 'username', 'first_name', 'last_name', 'email', 'is_active')


class GroupTable(NetBoxTable):
    name = tables.Column(
        verbose_name='Name',
        linkify=True
    )
    actions = columns.ActionsColumn(
        verbose_name='Actions',
        actions=('edit', 'delete'),
    )

    class Meta(NetBoxTable.Meta):
        model = NetBoxGroup
        fields = (
            'pk', 'id', 'name', 'users_count',
        )
        default_columns = ('pk', 'name', 'users_count', )


class ObjectPermissionTable(NetBoxTable):
    name = tables.Column(
        verbose_name='Name',
        linkify=True
    )
    object_types = columns.ContentTypesColumn(
        verbose_name='Object types',
    )
    enabled = columns.BooleanColumn(
        verbose_name='Enabled',
    )
    can_view = columns.BooleanColumn(
        verbose_name='Can view',
    )
    can_add = columns.BooleanColumn(
        verbose_name='Can add',
    )
    can_change = columns.BooleanColumn(
        verbose_name='Can change',
    )
    can_delete = columns.BooleanColumn(
        verbose_name='Can delete',
    )
    custom_actions = columns.ArrayColumn(
        verbose_name='Custom actions',
        accessor=tables.A('actions')
    )
    users = columns.ManyToManyColumn(
        verbose_name='Users',
        linkify_item=('users:netboxuser', {'pk': tables.A('pk')})
    )
    groups = columns.ManyToManyColumn(
        verbose_name='Groups',
        linkify_item=('users:netboxgroup', {'pk': tables.A('pk')})
    )
    actions = columns.ActionsColumn(
        verbose_name='Actions',
        actions=('edit', 'delete'),
    )

    class Meta(NetBoxTable.Meta):
        model = ObjectPermission
        fields = (
            'pk', 'id', 'name', 'enabled', 'object_types', 'can_view', 'can_add', 'can_change', 'can_delete',
            'custom_actions', 'users', 'groups', 'constraints', 'description',
        )
        default_columns = (
            'pk', 'name', 'enabled', 'object_types', 'can_view', 'can_add', 'can_change', 'can_delete', 'description',
        )
