import django_tables2 as tables
from django.utils.translation import gettext as _

from netbox.tables import NetBoxTable, columns
from users.models import Group, ObjectPermission, Owner, OwnerGroup, Token, User

__all__ = (
    'GroupTable',
    'ObjectPermissionTable',
    'OwnerGroupTable',
    'OwnerTable',
    'TokenTable',
    'UserTable',
)

TOKEN = """<samp><a href="{{ record.get_absolute_url }}">{{ record }}</a></samp>"""


class TokenTable(NetBoxTable):
    user = tables.Column(
        linkify=True,
        verbose_name=_('User')
    )
    token = columns.TemplateColumn(
        verbose_name=_('token'),
        template_code=TOKEN,
        orderable=False,
    )
    enabled = columns.BooleanColumn(
        verbose_name=_('Enabled')
    )
    write_enabled = columns.BooleanColumn(
        verbose_name=_('Write Enabled')
    )
    created = columns.DateTimeColumn(
        timespec='minutes',
        verbose_name=_('Created'),
    )
    expires = columns.DateTimeColumn(
        timespec='minutes',
        verbose_name=_('Expires'),
    )
    last_used = columns.DateTimeColumn(
        verbose_name=_('Last Used'),
    )
    allowed_ips = columns.ArrayColumn(
        verbose_name=_('Allowed IPs'),
    )
    actions = columns.ActionsColumn(
        actions=('edit', 'delete'),
    )

    class Meta(NetBoxTable.Meta):
        model = Token
        fields = (
            'pk', 'id', 'token', 'version', 'pepper_id', 'user', 'description', 'enabled', 'write_enabled', 'created',
            'expires', 'last_used', 'allowed_ips',
        )
        default_columns = ('token', 'version', 'user', 'enabled', 'write_enabled', 'description', 'allowed_ips')


class UserTable(NetBoxTable):
    username = tables.Column(
        verbose_name=_('Username'),
        linkify=True
    )
    groups = columns.ManyToManyColumn(
        verbose_name=_('Groups'),
        linkify_item=('users:group', {'pk': tables.A('pk')})
    )
    is_active = columns.BooleanColumn(
        verbose_name=_('Is Active'),
    )
    is_superuser = columns.BooleanColumn(
        verbose_name=_('Is Superuser'),
    )
    actions = columns.ActionsColumn(
        actions=('edit', 'delete'),
    )

    class Meta(NetBoxTable.Meta):
        model = User
        fields = (
            'pk', 'id', 'username', 'first_name', 'last_name', 'email', 'groups', 'is_active', 'is_superuser',
            'last_login',
        )
        default_columns = ('pk', 'username', 'first_name', 'last_name', 'email', 'is_active')


class GroupTable(NetBoxTable):
    name = tables.Column(
        verbose_name=_('Name'),
        linkify=True
    )
    actions = columns.ActionsColumn(
        actions=('edit', 'delete'),
    )

    class Meta(NetBoxTable.Meta):
        model = Group
        fields = ('pk', 'id', 'name', 'users_count', 'description')


class ObjectPermissionTable(NetBoxTable):
    name = tables.Column(
        verbose_name=_('Name'),
        linkify=True
    )
    object_types = columns.ContentTypesColumn(
        verbose_name=_('Object Types'),
    )
    enabled = columns.BooleanColumn(
        verbose_name=_('Enabled'),
    )
    can_view = columns.BooleanColumn(
        verbose_name=_('Can View'),
        orderable=False,
    )
    can_add = columns.BooleanColumn(
        verbose_name=_('Can Add'),
        orderable=False,
    )
    can_change = columns.BooleanColumn(
        verbose_name=_('Can Change'),
        orderable=False,
    )
    can_delete = columns.BooleanColumn(
        verbose_name=_('Can Delete'),
        orderable=False,
    )
    custom_actions = columns.ArrayColumn(
        verbose_name=_('Custom Actions'),
        accessor=tables.A('actions')
    )
    users = columns.ManyToManyColumn(
        verbose_name=_('Users'),
        linkify_item=('users:user', {'pk': tables.A('pk')})
    )
    groups = columns.ManyToManyColumn(
        verbose_name=_('Groups'),
        linkify_item=('users:group', {'pk': tables.A('pk')})
    )
    actions = columns.ActionsColumn(
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


class OwnerGroupTable(NetBoxTable):
    name = tables.Column(
        verbose_name=_('Name'),
        linkify=True
    )
    owner_count = columns.LinkedCountColumn(
        viewname='users:owner_list',
        url_params={'group_id': 'pk'},
        verbose_name=_('Owners')
    )
    actions = columns.ActionsColumn(
        actions=('edit', 'delete'),
    )

    class Meta(NetBoxTable.Meta):
        model = OwnerGroup
        fields = (
            'pk', 'id', 'name', 'description',
        )
        default_columns = ('pk', 'name', 'owner_count', 'description')


class OwnerTable(NetBoxTable):
    name = tables.Column(
        verbose_name=_('Name'),
        linkify=True
    )
    group = tables.Column(
        verbose_name=_('Group'),
        linkify=True,
    )
    user_groups = columns.ManyToManyColumn(
        verbose_name=_('Groups'),
        linkify_item=('users:group', {'pk': tables.A('pk')})
    )
    users = columns.ManyToManyColumn(
        verbose_name=_('Users'),
        linkify_item=('users:user', {'pk': tables.A('pk')})
    )
    actions = columns.ActionsColumn(
        actions=('edit', 'delete'),
    )

    class Meta(NetBoxTable.Meta):
        model = Owner
        fields = (
            'pk', 'id', 'name', 'group', 'description', 'user_groups', 'users',
        )
        default_columns = ('pk', 'name', 'group', 'description', 'user_groups', 'users')
