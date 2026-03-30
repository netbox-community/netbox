from django.utils.translation import gettext_lazy as _

from netbox.registry import registry
from netbox.ui import actions, attrs, panels
from users.constants import RESERVED_ACTIONS


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
    date_joined = attrs.DateTimeAttr('date_joined', label=_('Account created'), spec='date')
    last_login = attrs.DateTimeAttr('last_login', label=_('Last login'), spec='minutes')
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


class ObjectPermissionCustomActionsPanel(panels.ObjectPanel):
    """
    A panel which displays non-CRUD (custom) actions assigned to an ObjectPermission.
    """
    template_name = 'users/panels/custom_actions.html'
    title = _('Custom Actions')

    def get_context(self, context):
        obj = context['object']
        custom_actions = [a for a in obj.actions if a not in RESERVED_ACTIONS]

        # Build a list of (action_name, model_labels) tuples from the registry,
        # scoped to the object types assigned to this permission.
        assigned_types = {
            f'{ot.app_label}.{ot.model}' for ot in obj.object_types.all()
        }
        action_models = {}
        for model_key, model_actions in registry['model_actions'].items():
            if model_key in assigned_types:
                for action in model_actions:
                    if action.name in custom_actions:
                        action_models.setdefault(action.name, []).append(model_key)

        custom_actions_display = [
            (action, ', '.join(action_models.get(action, [])))
            for action in custom_actions
        ]

        return {
            **super().get_context(context),
            'custom_actions': custom_actions_display,
        }

    def render(self, context):
        ctx = self.get_context(context)
        if not ctx['custom_actions']:
            return ''
        return super().render(context)


class OwnerPanel(panels.ObjectAttributesPanel):
    name = attrs.TextAttr('name')
    group = attrs.RelatedObjectAttr('group', linkify=True)
    description = attrs.TextAttr('description')
