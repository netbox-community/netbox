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
