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


class ObjectPermissionActionsPanel(panels.ObjectPanel):
    template_name = 'users/panels/actions.html'
    title = _('Actions')

    def get_context(self, context):
        obj = context['object']

        crud_actions = [
            (_('View'), 'view' in obj.actions),
            (_('Add'), 'add' in obj.actions),
            (_('Change'), 'change' in obj.actions),
            (_('Delete'), 'delete' in obj.actions),
        ]

        enabled_actions = set(obj.actions) - set(RESERVED_ACTIONS)

        # Collect all registered actions from the full registry, deduplicating by name.
        seen = []
        seen_set = set()
        action_models = {}
        for model_key, model_actions in registry['model_actions'].items():
            for action in model_actions:
                if action.name not in seen_set:
                    seen.append(action.name)
                    seen_set.add(action.name)
                action_models.setdefault(action.name, []).append(model_key)

        registered_display = [
            (action, action in enabled_actions, ', '.join(sorted(action_models[action])))
            for action in seen
        ]

        return {
            **super().get_context(context),
            'crud_actions': crud_actions,
            'registered_actions': registered_display,
        }


class OwnerPanel(panels.ObjectAttributesPanel):
    name = attrs.TextAttr('name')
    group = attrs.RelatedObjectAttr('group', linkify=True)
    description = attrs.TextAttr('description')
