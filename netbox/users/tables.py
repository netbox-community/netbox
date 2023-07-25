import django_tables2 as tables
from django.utils.translation import gettext as _

from netbox.tables import NetBoxTable, columns
from users.models import NetBoxGroup, NetBoxUser, ObjectPermission, Token, UserToken

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


class UserTokenTable(NetBoxTable):
    """
    Table for users to manager their own API tokens under account views.
    """
    key = columns.TemplateColumn(
        verbose_name=_('Key'),
        template_code=TOKEN,
    )
    write_enabled = columns.BooleanColumn(
        verbose_name=_('Write Enabled')
    )
    created = columns.DateColumn(
        verbose_name=_('Created'),
    )
    expires = columns.DateColumn(
        verbose_name=_('Expires'),
    )
    last_used = columns.DateTimeColumn(
        verbose_name=_('Last Used'),
    )
    allowed_ips = columns.TemplateColumn(
        verbose_name=_('Allowed IPs'),
        template_code=ALLOWED_IPS
    )
    actions = TokenActionsColumn(
        actions=('edit', 'delete'),
        extra_buttons=COPY_BUTTON
    )

    class Meta(NetBoxTable.Meta):
        model = UserToken
        fields = [
            'pk', 'id', 'key', 'description', 'write_enabled', 'created', 'expires', 'last_used', 'allowed_ips',
        ]


class TokenTable(UserTokenTable):
    """
    General-purpose table for API token management.
    """
    user = tables.Column(
        linkify=True,
        verbose_name=_('User')
    )

    class Meta(NetBoxTable.Meta):
        model = Token
        fields = [
            'pk', 'id', 'key', 'user', 'description', 'write_enabled', 'created', 'expires', 'last_used', 'allowed_ips',
        ]


class UserTable(NetBoxTable):
    username = tables.Column(
        linkify=True
    )
    groups = columns.ManyToManyColumn(
        linkify_item=('users:netboxgroup', {'pk': tables.A('pk')})
    )
    is_active = columns.BooleanColumn()
    is_staff = columns.BooleanColumn()
    is_superuser = columns.BooleanColumn()
    actions = columns.ActionsColumn(
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
    object_types = columns.ContentTypesColumn()
    enabled = columns.BooleanColumn()
    can_view = columns.BooleanColumn()
    can_add = columns.BooleanColumn()
    can_change = columns.BooleanColumn()
    can_delete = columns.BooleanColumn()
    custom_actions = columns.ArrayColumn(
        accessor=tables.A('actions')
    )
    users = columns.ManyToManyColumn(
        linkify_item=('users:netboxuser', {'pk': tables.A('pk')})
    )
    groups = columns.ManyToManyColumn(
        linkify_item=('users:netboxgroup', {'pk': tables.A('pk')})
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
