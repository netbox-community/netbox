from django.utils.translation import gettext_lazy as _

from netbox.ui import actions, attrs, panels


class TokenPanel(panels.ObjectAttributesPanel):
    version = attrs.NumericAttr('version')
    key = attrs.TextAttr('key')
    token = attrs.TextAttr('partial')
    pepper_id = attrs.NumericAttr('pepper_id')
    user = attrs.RelatedObjectAttr('user', linkify=True)
    description = attrs.TextAttr('description')
    enabled = attrs.BooleanAttr('enabled')
    write_enabled = attrs.BooleanAttr('write_enabled')
    expires = attrs.TextAttr('expires')
    last_used = attrs.TextAttr('last_used')
    allowed_ips = attrs.TextAttr('allowed_ips')


class TokenExamplePanel(panels.Panel):
    template_name = 'users/panels/token_example.html'
    title = _('Example Usage')
    actions = [
        actions.CopyContent('token-example')
    ]


class UserPanel(panels.ObjectAttributesPanel):
    username = attrs.TextAttr('username')
    full_name = attrs.TemplatedAttr(
        'get_full_name',
        label=_('Full name'),
        template_name='users/attrs/full_name.html',
    )
    email = attrs.TextAttr('email')
    date_joined = attrs.TemplatedAttr(
        'date_joined',
        label=_('Account created'),
        template_name='users/attrs/date_joined.html',
    )
    last_login = attrs.TemplatedAttr(
        'last_login',
        label=_('Last login'),
        template_name='users/attrs/last_login.html',
    )
    is_active = attrs.BooleanAttr('is_active', label=_('Active'))
    is_superuser = attrs.BooleanAttr('is_superuser', label=_('Superuser'))


class ObjectPermissionPanel(panels.ObjectAttributesPanel):
    name = attrs.TextAttr('name')
    description = attrs.TextAttr('description')
    enabled = attrs.BooleanAttr('enabled')


class ObjectPermissionActionsPanel(panels.ObjectAttributesPanel):
    title = _('Actions')

    can_view = attrs.BooleanAttr('can_view', label=_('View'))
    can_add = attrs.BooleanAttr('can_add', label=_('Add'))
    can_change = attrs.BooleanAttr('can_change', label=_('Change'))
    can_delete = attrs.BooleanAttr('can_delete', label=_('Delete'))


class OwnerPanel(panels.ObjectAttributesPanel):
    name = attrs.TextAttr('name')
    group = attrs.RelatedObjectAttr('group', linkify=True)
    description = attrs.TextAttr('description')
